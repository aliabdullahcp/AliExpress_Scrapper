import scrapy
from ..items import CoreItem
from scrapy_splash import SplashRequest


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
            categories3 = cat2.xpath("//div[@class='a-section octopus-pc-category-card-v2-subcategory']")
            print(len(categories3))
            for cat3 in categories3:
                cat3_name = cat3.xpath(".//a[@class='a-link-normal octopus-pc-category-card-v2-subcategory-link']/@title").get()
                # cat3_link = cat3.xpath(".//a/@href").get()
                yield {
                    'Sub-Category-2': cat2_name,
                    'Sub-Category-3': cat3_name,
                    # 'Sub-Category-3-Link': self.url_prefix + cat3_link
                }
            break
