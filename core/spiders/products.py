import scrapy
from ..items import CoreItem
from scrapy_splash import SplashRequest


class ProductsSpider(scrapy.Spider):
    name = 'products'
    current_page = 1
    url_prefix = 'https:'
    url = 'https://www.aliexpress.com/category/200003482/dresses.html?page='
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
        yield SplashRequest(self.url + str(self.current_page), self.parse,
                            endpoint='execute',
                            args={'html': 1, 'lua_source': self.script, 'wait': 2})

    def parse(self, response, **kwargs):
        products = response.xpath("//div[@class='hover-help']/div[@class='item-title-wrap']/a")
        # if self.current_page < 2:  # len(products) > 0:
        for product in products:
            product_link = product.xpath(".//@href").get()
            yield SplashRequest(self.url_prefix + product_link, self.parse_product_details,
                                endpoint='execute',
                                args={'html': 1, 'lua_source': self.script, 'wait': 2})

            break

        self.current_page += 1
        yield SplashRequest(self.url + str(self.current_page), self.parse,
                            endpoint='execute',
                            args={'html': 1, 'lua_source': self.script, 'wait': 2})

    def parse_product_details(self, response):
        product = CoreItem()
        product['product_title'] = response.xpath("//h1[@class='product-title-text']/text()").get()
        product['product_rating'] = response.xpath("//span[@class='overview-rating-average']/text()").get()
        product['product_reviews'] = response.xpath("//span[@class='product-reviewer-reviews black-link']/text()").get()
        product['product_orders'] = response.xpath("//span[@class='product-reviewer-sold']/text()").get()
        product['product_image'] = response.xpath("//img[@class='magnifier-image']/@src").get()
        yield product
