import os
import json
import psycopg2
import scrapy

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from dotenv import load_dotenv


class NewsSpider(scrapy.Spider):
    name = 'news'

    custom_settings = {
        'FEEDS': {},  # disable Scrapy file outputs
        'USER_AGENT': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Safari/537.36'
        ),
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 2,
        'HTTPERROR_ALLOW_ALL': True,
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 1.0,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load environment variables
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        load_dotenv(PROJECT_ROOT / '.env')

        # Connect to PostgreSQL
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
        )
        self.cur = self.conn.cursor()

    def start_requests(self):
        # Load tickers from JSON file
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        tickers_file = PROJECT_ROOT / 'stock_scraper' / 'tickers.json'
        with open(tickers_file, 'r') as f:
            symbols = json.load(f)

        # Feeds requiring a symbol placeholder
        symbol_feeds = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline?s={}&region=US&lang=en-US',
            'https://www.nasdaq.com/feed/rssoutbound?symbol={}'
        ]

        # Feeds that do not require a symbol
        global_feeds = [
            'https://rss.cnn.com/rss/money_latest.rss',
            'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
            'https://feeds.bbci.co.uk/news/business/rss.xml',
            'https://www.marketwatch.com/rss/topstories',
            'https://www.marketwatch.com/rss/markets',
            'https://www.investing.com/rss/news.rss',
            'https://www.ft.com/markets?format=rss',
            'https://www.economist.com/business/rss.xml',
            'https://www.theguardian.com/business/rss',
            'https://seekingalpha.com/feed.xml',
            'https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml',
            'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
            'https://feeds.a.dj.com/rss/RSSWSJcomUSBusiness.xml',
            'https://feeds.a.dj.com/rss/RSSWSJcomUSMarkets.xml',
            'https://www.cnbc.com/id/19854910/device/rss/rss.html',
            'https://www.barrons.com/rss',
            'https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=topNews',
            'https://www.reddit.com/r/finance/.rss',
            'https://business.financialpost.com/feed',
            'https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines',
            'https://feeds.content.dowjones.io/public/rss/mw_topstories',
            'https://feeds.content.dowjones.io/public/rss/mw_bulletins',
            'https://feeds.content.dowjones.io/public/rss/mw_marketpulse',
            'https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&hl=en-US&gl=US&ceid=US:en',
            'https://www.marketbeat.com/rss.ashx?type=headlines',
            'https://www.marketbeat.com/rss.ashx?type=originals',
            'https://www.marketbeat.com/rss.ashx?type=instant-alerts',
            'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
            'https://ragingbull.com/feed/',
        ]

        # Yield requests for global feeds
        for url in global_feeds:
            yield scrapy.Request(
                url,
                callback=self.parse,
                errback=self.handle_error,
                meta={'source_feed': url}
            )

        # Yield requests for each symbol in symbol_feeds
        for sym in symbols:
            for tpl in symbol_feeds:
                url = tpl.format(sym)
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    errback=self.handle_error,
                    meta={'source_feed': url}
                )

    def parse(self, response):
        if response.status != 200:
            self.logger.warning(f"Skipping {response.url} → HTTP {response.status}")
            return

        today = datetime.now(timezone.utc).date()
        min_date = today - timedelta(days=7)

        for item in response.xpath('//item'):
            # Try <link>, fallback to <guid>
            link = item.xpath('link/text()').get() or item.xpath('guid/text()').get()
            pub  = item.xpath('pubDate/text()').get()
            if not link or not pub:
                continue

            # Parse publication date
            try:
                dt = parsedate_to_datetime(pub)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            except Exception:
                continue

            # Date filter (last 7 days)
            if not (min_date <= dt.date() <= today):
                continue

            title   = item.xpath('title/text()').get()
            summary = item.xpath('description/text()').get()
            source  = response.meta['source_feed']
            self.save_to_postgres((pub, title, link, summary, source))

    def save_to_postgres(self, record):
        try:
            self.cur.execute(
                """
                INSERT INTO news (date, title, url, summary, source_feed)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                """,
                record
            )
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"DB insert failed: {e}")
            self.conn.rollback()

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.request.url} ({failure.value})")

    def closed(self, reason):
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(NewsSpider)
    process.start()
