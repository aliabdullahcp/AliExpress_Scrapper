# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CoreItem(scrapy.Item):
    Product_Category = scrapy.Field()
    Product_Title = scrapy.Field()
    Product_Reviews = scrapy.Field()
    Product_Rating = scrapy.Field()
    Product_Orders = scrapy.Field()
    Product_Image = scrapy.Field()
