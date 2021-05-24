import scrapy
from ..items import CoreItem
from scrapy_splash import SplashRequest


class ProductsSpider(scrapy.Spider):
    name = 'products'
    current_page = 1
    url_prefix = 'https:'
    urls = ['https://www.aliexpress.com/category/200003482/dresses.html?page=',
            'https://www.aliexpress.com/category/100003127/t-shirts.html?spm=a2g0o.home.101.4.650c2145HaFx24',
            'https://www.aliexpress.com/category/200001648/blouses-shirts.html?spm=a2g0o.home.101.5.650c2145HaFx24']
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
        for url in self.urls:
            yield SplashRequest(url + str(self.current_page), self.parse,
                                endpoint='execute',
                                args={'html': 1, 'lua_source': self.script, 'wait': 2}, meta={'source_url': url})

    def parse(self, response):
        url = response.request.meta['source_url']
        products = response.xpath("//div[@class='hover-help']/div[@class='item-title-wrap']/a")
        if len(products) > 0:
            for product in products:
                product_link = product.xpath(".//@href").get()
                yield SplashRequest(self.url_prefix + product_link, self.parse_product_details,
                                    endpoint='execute',
                                    args={'html': 1, 'lua_source': self.script, 'wait': 2})

            self.current_page += 1
            yield SplashRequest(url + str(self.current_page), self.parse,
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
