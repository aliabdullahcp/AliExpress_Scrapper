# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CoreItem(scrapy.Item):
    product_title = scrapy.Field()
    product_reviews = scrapy.Field()
    product_rating = scrapy.Field()
    product_orders = scrapy.Field()
    product_image=scrapy.Field()
