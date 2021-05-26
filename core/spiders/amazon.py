import scrapy
from ..items import CoreItem
from scrapy_splash import SplashRequest


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    url_prefix = 'https:'
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
        # featured_categories = response.xpath("//span[@class='a-declarative']/li")

        featured_categories = response.xpath("//span[@class='a-size-medium a-color-base a-text-bold']")
        for fea_cat in featured_categories:
            fea_cat_name = fea_cat.xpath(".//text()").get()
            sub_categories = fea_cat.xpath("//div[@class='a-section octopus-pc-category-card-v2-subcategory']/a")
            for sub_cat in sub_categories:
                sub_cat_link = sub_cat.xpath(".//@href").get()
                sub_cat_name = sub_cat.xpath("//span/text()").get()
                yield {
                    'Featured Category': fea_cat_name,
                    'Sub Category': sub_cat_name,
                    'Sub Category Link': sub_cat_link
                }
            yield {
                'fee_cat_name': fea_cat_name
            }
