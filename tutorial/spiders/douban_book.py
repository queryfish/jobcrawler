#!/usr/bin/python
#coding:utf-8

import logging
import scrapy
import pymongo
from tutorial.items import doubanBookItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
import  json
import  time
import datetime
import  random
import redis
from scrapy.conf import settings

#zhipin 爬虫
class DoubanBookSpider(scrapy.Spider):

    name = "doubanbook"
    allowed_domains = ["douban.com"]
    client = pymongo.MongoClient(host="127.0.0.1", port=27017)
    db = client['sobooks']
    collection =  db['books']
    step = 2;
    counter = 0;

    # start_urls = ['https://book.douban.com/subject/26389895/']
    start_urls = []
    custom_settings = {
        "ITEM_PIPELINES":{
            'tutorial.pipelines.DoubanBookPipeline': 300,
        },
        # "DOWNLOADER_MIDDLEWARES":{
        #     'tutorial.middlewares.ScriptSlugMiddleware': 299,
        #  #   'tutorial.middlewares.ProxyMiddleware':301
        # },
        "DEFAULT_REQUEST_HEADERS":{
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent':'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Mobile Safari/537.36',
            'Referer':'https://www.douban.com/',
            'X-Requested-With':"XMLHttpRequest"
            # "cookie":"lastCity=101020100; JSESSIONID=""; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1532401467,1532435274,1532511047,1532534098; __c=1532534098; __g=-; __l=l=%2Fwww.zhipin.com%2F&r=; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fc101020100-p100103%2F; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1532581213; __a=4090516.1532500938.1532516360.1532534098.11.3.7.11"
        }
    }

    def getSomeUrls(self, count):
        print('fetch from mongo')
        res = self.collection.find({"$and":[{"doubanUrl":{"$ne":None}},{"doubanCrawlDate":{"$exists":False}}]}).limit(count);
        urls = [];
        for post in res:
            # print(post)
            urls.append(post['doubanUrl']);
        return urls

    def addSomeUrls(self, urls):
        for url in urls:
            res = self.collection.update({'doubanUrl':url}, {'$set':{'doubanUrl':url}}, upsert=True)


    def __init__(self, *a, **kw):
        super(DoubanBookSpider, self).__init__(*a, **kw)
        urls = self.getSomeUrls(self.step)
        for url in urls:
            self.start_urls.append(url)
            # print(url);


    def parse(self, response):
        DETAIL_BOOK_INFO_BLOCK_SEL = '#info';
        DETAIL_PAGE_BOOK_INFO_LEN_SEL = '#info';
        DETAIL_PAGE_BOOK_INFO_SEL = '#info > span:nth-child(INDEX';
        DETAIL_RATING_NUMBER_SEL = '#interest_sectl > div > div.rating_self.clearfix > strong';
        DETAIL_RATING_USER_NUMBER_SEL = '#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > span > a';
        DETAIL_BRIEF_SEL = '#link-report ';
        DETAIL_BRIEF_SEL = '#link-report > * > div.intro';
        DETAIL_BRIEF_SEL = '#link-report > span.short > div > p';
        # DETAIL_AUTHOR_BRIEF_SEL = 'div.related_info > div:nth-child(1) > * > div.intro';
        DETAIL_AUTHOR_BRIEF_SEL ='#content > div > div.article > div.related_info > div:nth-child(4) > span.short > div > p';

        DETAIL_TAGS_SEL = '#db-tags-section > div.indent  > span > a';
        DETAIL_TAGS_SEL2 = '#db-tags-section > div.indent  > span ';
        DETAIL_TAGS_LEN_SEL = '#db-tags-section > div.indent > span';
        DETAIL_COMMENTS = '#content > div > div.article > div.related_info > div.mod-hd > h2 > span.pl > a';
        SEARCH_URL_TEMPLATE = 'https://book.douban.com/subject_search?search_text=ISBN&cat=1001';
        REC_SECTION_SEL       = '#db-rec-section > div > dl > dd';
        REC_SECTION_ARRAY_SEL = '#db-rec-section > div > dl > dt > a';
        TITLE_SEL = '#wrapper > h1 > span';
        COVER_SEL = '#mainpic > a > img';

        bookbrief = response.css(DETAIL_BRIEF_SEL).css('::text').extract()
        authorInfo = (response.css(DETAIL_AUTHOR_BRIEF_SEL).css('::text').extract());
        bookInfo = (response.css(DETAIL_PAGE_BOOK_INFO_LEN_SEL).css('::text').extract());

        bookItem = doubanBookItem()
        bookItem['doubanUrl'] = response.request.url;
        bookItem['doubanBookName'] = response.css(TITLE_SEL).css('::text').extract_first();
        bookItem['doubanBookMeta'] = bookInfo
        bookItem['doubanTags'] = response.css(DETAIL_TAGS_SEL).css('::text').extract();
        bookItem['doubanRating'] = response.css(DETAIL_RATING_NUMBER_SEL).css('::text').extract_first();
        bookItem['doubanRatingUser'] = response.css(DETAIL_RATING_USER_NUMBER_SEL).css('::text').extract_first();
        bookItem['doubanBookBrief'] = bookbrief;
        bookItem['doubanAuthorBrief'] = authorInfo;
        bookItem['doubanCrawlDate'] = datetime.datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S");
        # bookItem['doubanISBN']=
        yield bookItem
        self.counter = self.counter+1
        print('NO.{} book crawled ..'.format(self.counter));
        print(bookItem['doubanBookName'])
        print(bookItem['doubanUrl'])

        # time.sleep(int(random.uniform(2, 5)))

        items = response.css(REC_SECTION_SEL);

        for item in items:
            # print('extracting href from alink')
            # print(detail_url);
            href = (item.css('a::attr(href)').extract()[0]);
            urlOnly = doubanBookItem();
            # urlOnly['doubanUrl'] = href;
            self.addSomeUrls([href])

        newUrls = self.getSomeUrls(self.step)
        # print('get new url')
        # print(newUrls)

        # for url in newUrls:
            # if(len(url) > 0):
            # yield Request(url ,callback=self.parse)
        for item in items:
            # print(item.css('a::text').extract()[0]);
            href = (item.css('a::attr(href)').extract()[0]);
            # print(href)
            yield Request(href ,callback=self.parse)
