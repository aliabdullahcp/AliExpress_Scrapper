from scrapy.exporters import CsvItemExporter
from scrapy import signals
from pydispatch import dispatcher


def item_type(item):
    # The CSV file names are used (imported) from the scrapy spider.
    return type(item)


class CorePipeline(object):
    # For simplicity, I'm using the same class def names as found in the,
    # main scrapy spider and as defined in the items.py
    fileNamesCsv = ['dresses', 't-shirts', 'blouses-shirts']

    def __init__(self):
        self.files = {}
        self.exporters = {}
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        self.files = dict([(name, open("Ali_Express_" + name + '.csv', 'wb')) for name in self.fileNamesCsv])
        for name in self.fileNamesCsv:
            self.exporters[name] = CsvItemExporter(self.files[name])

            self.exporters[name].fields_to_export = ['Product_Category', 'Product_Title', 'Product_Rating',
                                                     'Product_Reviews', 'Product_Orders', 'Product_Image']
            self.exporters[name].start_exporting()



    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        typesItem = item['Product_Category']
        if typesItem in set(self.fileNamesCsv):
            self.exporters[typesItem].export_item(item)
        return item

# class CorePipeline:
#     def process_item(self, item, spider):
#         return item
