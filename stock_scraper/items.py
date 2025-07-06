import scrapy

class HeadlineItem(scrapy.Item):
    source     = scrapy.Field()
    date       = scrapy.Field()
    title      = scrapy.Field()
    url        = scrapy.Field()
    content    = scrapy.Field()