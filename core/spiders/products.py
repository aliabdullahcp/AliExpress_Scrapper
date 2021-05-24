import scrapy
from ..items import CoreItem
from scrapy_splash import SplashRequest


class ProductsSpider(scrapy.Spider):
    name = 'products'

    url_prefix = 'https:'
    urls = ['https://www.aliexpress.com/category/200003482/dresses.html?page=',
            'https://www.aliexpress.com/category/100003127/t-shirts.html?page=',
            'https://www.aliexpress.com/category/200001648/blouses-shirts.html?page=']
    script = """
                function main(splash)
                    local num_scrolls = 10
                    local scroll_delay = 1

                    local scroll_to = splash:jsfunc("window.scrollTo")
                    local get_body_height = splash:jsfunc(
                        "function() {return document.body.scrollHeight;}"
                    )
                    assert(splash:go(splash.args.url))
                    splash:wait(splash.args.wait)

                    for _ = 1, num_scrolls do
                        local height = get_body_height()
                        for i = 1, 10 do
                            scroll_to(0, height * i/10)
                            splash:wait(scroll_delay/10)
                        end
                    end        
                    return splash:html()
                end
                """

    def start_requests(self):
        start_page = 1
        for url in self.urls:
            yield SplashRequest(url + str(start_page), self.parse,
                                endpoint='execute',
                                args={'html': 1, 'lua_source': self.script, 'wait': 2},
                                meta={'source_url': url, 'current_page': 1})

    def parse(self, response):
        url = response.meta.get('source_url')
        current_page = response.meta.get('current_page')

        category = str(url).split('/')[5].split('.')[0]

        products = response.xpath("//div[@class='hover-help']/div[@class='item-title-wrap']/a")

        if len(products) > 0:
            for product in products:
                product_link = product.xpath(".//@href").get()
                yield SplashRequest(self.url_prefix + product_link, self.parse_product_details,
                                    endpoint='execute',
                                    args={'html': 1, 'lua_source': self.script, 'wait': 2},
                                    meta={'category': category})

            current_page += 1
            yield SplashRequest(url + str(current_page), self.parse,
                                endpoint='execute',
                                args={'html': 1, 'lua_source': self.script, 'wait': 2},
                                meta={'source_url': url, 'current_page': current_page})

    def parse_product_details(self, response):
        product = CoreItem()
        product['Product_Category'] = response.meta.get('category')
        product['Product_Title'] = response.xpath("//h1[@class='product-title-text']/text()").get()
        product['Product_Rating'] = response.xpath("//span[@class='overview-rating-average']/text()").get()
        product['Product_Image'] = response.xpath("//img[@class='magnifier-image']/@src").get()
        reviews = response.xpath("//span[@class='product-reviewer-reviews black-link']/text()").get()
        orders = response.xpath("//span[@class='product-reviewer-sold']/text()").get()
        product['Product_Reviews'] = str(reviews).split()[0]
        product['Product_Orders'] = str(orders).split()[0]
        yield product
