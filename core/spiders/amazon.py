import scrapy
from ..items import CoreItem
from scrapy_splash import SplashRequest
import urllib.parse as urlparse
from urllib.parse import parse_qs
import re


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    url_prefix = 'https://www.amazon.co.uk'
    urls = ['https://www.amazon.co.uk/gp/browse.html?node=10745681&ref_=nav_em__furniture_t2_0_2_13_6#nav-top']
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
                                args={'html': 1, 'lua_source': self.script, 'wait': 2})

    def parse(self, response):
        categories2 = response.xpath("//div[@class='a-section octopus-pc-category-card-v2-item-block']")
        for cat2 in categories2:
            cat2_name = cat2.xpath(".//span[@class='a-size-medium a-color-base a-text-bold']/text()").get()
            cat3_name = cat2.xpath(
                ".//a[@class='a-link-normal octopus-pc-category-card-v2-subcategory-link']/@title").getall()
            cat3_link = cat2.xpath(
                ".//a[@class='a-link-normal octopus-pc-category-card-v2-subcategory-link']/@href").getall()

            for index, element in enumerate(cat3_name):
                yield SplashRequest(self.url_prefix + cat3_link[index], self.parse_products_list,
                                    endpoint='execute',
                                    args={'html': 1, 'lua_source': self.script, 'wait': 2},
                                    meta={'Sub-Category-2': cat2_name, 'Sub-Category-3': element})
                break
            break

    def parse_products_list(self, response):
        products = response.xpath("//div[@class='a-section a-spacing-medium']")
        cat2_name = response.meta.get('Sub-Category-2')
        cat3_name = response.meta.get('Sub-Category-3')
        for product in products:
            product_link = product.xpath(".//h2/a[@class='a-link-normal a-text-normal']/@href").get()
            product_name = product.xpath(".//h2/a[@class='a-link-normal a-text-normal']/span/text()").get()

            yield SplashRequest(self.url_prefix + product_link, self.parse_product_details,
                                endpoint='execute',
                                args={'html': 1, 'lua_source': self.script, 'wait': 2},
                                meta={'Sub-Category-2': cat2_name,
                                      'Sub-Category-3': cat3_name,
                                      'Product Name': product_name,
                                      'Product Keyword': get_product_keywords(self.url_prefix + product_link),
                                      'Product Link': self.url_prefix + product_link})
            break

    def parse_product_details(self, response):
        cat2_name = response.meta.get('Sub-Category-2')
        cat3_name = response.meta.get('Sub-Category-3')
        name = response.meta.get('Product Name')
        keyword = response.meta.get('Product Keyword')
        link = response.meta.get('Product Link')
        price_currency = response.xpath("//span[@class='a-size-medium a-color-price priceBlockBuyingPriceString']/text()").get()
        print(price_currency)
        price = price_currency #re.findall("\d+\.\d+", price_currency)
        currency = price_currency#re.sub(r'[\d,.\s]', '', price_currency)

        brand = response.xpath("//table[@id='productDetails_techSpec_section_1']/tbody/tr/td/text()").get()
        details = response.xpath("//table[@id='productDetails_detailBullets_sections1']")
        asin = ""
        date_first_available = ""
        for index, element in enumerate(details.xpath(".//tbody/tr/th/text()").getall()):
            if element.strip() == "ASIN":
                asin = details.xpath(".//tbody/tr/td/text()").getall()[index]
            if element.strip() == "Date First Available":
                date_first_available = details.xpath(".//tbody/tr/td/text()").getall()[index]

        yield {'Sub-Category-2': cat2_name,
               'Sub-Category-3': cat3_name,
               'Product Name': name,
               'Product Keyword': keyword,
               'Product Price': price,
               'Currency': currency,
               'Manufacturer': brand,
               'ASIN': asin,
               'Date First Available': date_first_available,
               'Product Page URL': link
               }


def get_product_keywords(product_url):
    parsed = urlparse.urlparse(product_url)
    return parse_qs(parsed.query)['keywords']
