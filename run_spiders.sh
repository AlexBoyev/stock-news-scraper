#!/usr/bin/env bash
set -e

while true; do
  echo "[NEWS] $(date --iso-8601=seconds) → Scraping news into Postgres…"
  scrapy runspider stock_scraper/spiders/news_spider.py

  echo "[NEWS] $(date --iso-8601=seconds) → Storing to Postgres from JSON…"
  python postgresql/store_to_postgres.py

  echo "[NEWS] $(date --iso-8601=seconds) → Exporting JSON from Postgres…"
  python postgresql/read_data_from_postgres.py

  echo "[NEWS] $(date --iso-8601=seconds) → Cycle complete; sleeping 2m…"
  sleep 120
done