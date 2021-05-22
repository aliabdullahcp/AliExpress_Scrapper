import scrapy
from scrapy_splash import SplashRequest


class ProductsSpider(scrapy.Spider):
    name = 'products'

    def start_requests(self):
        url = 'https://www.aliexpress.com/category/200003482/dresses.html'

        yield SplashRequest(url, self.parse, args={'wait': 0.5, 'viewport': '1024x2480', 'timeout':90, 'images': 0})

    def parse(self, response):
        products = response.xpath("//div[@class=('hover-help')]/div[@class=('item-title-wrap')]/a")
        for product in products:
            product_title = product.xpath(".//@title")
            yield {
                'product_title': product_title
            }
        # categories = response.xpath("//dt[@class='cate-name']/span")  #Selector used to get main categories from home page
        # for category in categories:
        #     category_name = category.xpath(".//a/text()").get()
        #     yield {
        #         'category_name': category_name,
        #     }
