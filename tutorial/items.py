# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    address = scrapy.Field()
    salary =scrapy.Field()
    create_time =scrapy.Field()
    body =scrapy.Field()
    company_name = scrapy.Field()
    postion_id = scrapy.Field()
    position_name = scrapy.Field()
    work_year = scrapy.Field()
    educational =scrapy.Field()
    pass

class doubanBookItem(scrapy.Item):
    # define the fields for your item here like:
    doubanId = scrapy.Field()
    doubanBookBrief =scrapy.Field()
    doubanAuthorBrief =scrapy.Field()
    doubanTags =scrapy.Field()
    doubanRating = scrapy.Field()
    doubanRatingUser = scrapy.Field()
    doubanBookMeta = scrapy.Field()
    doubanUrl = scrapy.Field()
    doubanCrawlDate =scrapy.Field()
    doubanBookName =scrapy.Field()
    doubanBookCover =scrapy.Field()
    doubanISBN =scrapy.Field()

    pass
