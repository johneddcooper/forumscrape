# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class ForumSpiderPipeline(object):
    # the DB collection to use (within the database name)
    collection_name = 'threads'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    # the from_crawler class method is used by Scrapy to make the pipelines for Spider instances. 
    # it is a way for the pipeline to hook into the Spider settings and functionality, in this case the Spider settings file.
    # see the scrapy documentation for more on the from_crawler method. 
    @classmethod
    def from_crawler(cls, crawler):
        # return cls with mongo_uri and mongo_db settings set from the settings file
        return cls(
            # pull the URI and database to connect to from the project settings.py file, which can be accessed from the crawler
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB')
        )

    def open_spider(self, spider):
        # on spider opening, create our database client for future use
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        # on spider ending, close the connection to the database
        self.client.close()

    def process_item(self, item, spider):
        # for every page that is parsed into an item (in this case Thread objects) add them to the database
        self.db[self.collection_name].insert_one(dict(item))
        return item