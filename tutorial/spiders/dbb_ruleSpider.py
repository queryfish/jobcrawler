#!/usr/bin/python
#coding:utf-8

import logging
import scrapy
import pymongo
from tutorial.items import doubanBookItem
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
import  json
import  time
import datetime
import  random
import redis
from scrapy.conf import settings

logger = logging.getLogger(__name__)


#zhipin 爬虫
class DoubanBookCrawlSpider(CrawlSpider):
    handle_httpstatus_list = [404, 403]
    name = "dbbCrawler"
    allowed_domains = ["douban.com"]
    client = pymongo.MongoClient(host="127.0.0.1", port=27017)
    db = client['sobooks']
    collection =  db['books']
    step = 10;
    counter = 0;
    banned = 0;
    # handle_httpstatus_list = [301, 302];

    # start_urls = ['https://book.douban.com/subject/1089243/']
    start_urls = []
    rules = (
        Rule(LinkExtractor(allow=(r'^https://book.douban.com/subject/\d+/$')), callback="parse_book", follow=True),
    )
    custom_settings = {
        "LOG_LEVEL": 'INFO',
        "LOG_STDOUT" : True,
        # "LOG_FILE": './dbb_logfile.log',
        "HTTPERROR_ALLOWED_CODES":[403,404],
        # Obey robots.txt rules
        #ROBOTSTXT_OBEY = True
        "RETRY_ENABLED": False,
        #RETRY_TIMES = 1
        "DOWNLOAD_TIMEOUT" : 7.5,
        # "DUPEFILTER_DEBUG": True,
        "LOGSTATS_INTERVAL" : 60.0,
        # Configure maximum concurrent requests performed by Scrapy (default: 16)
        # "CONCURRENT_REQUESTS": 2,
        "DOWNLOAD_DELAY":0.3,

        "AUTOTHROTTLE_ENABLED": True,
        # The initial download delay
        "AUTOTHROTTLE_START_DELAY": 1,
        # The maximum download delay to be set in case of high latencies
        "AUTOTHROTTLE_MAX_DELAY": 8,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 4.0,
        # Enable showing throttling stats for every response received:
        "AUTOTHROTTLE_DEBUG": True,

        "ITEM_PIPELINES":{
            'tutorial.pipelines.DoubanBookPipeline': 300,
        },
        "DOWNLOADER_MIDDLEWARES":{
            'tutorial.middlewares.RandomUserAgent': 2,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            'tutorial.middlewares_free_proxy.fixedProxyMiddleware': 100,
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'tutorial.middlewares_rotate_proxy.CustomRetryMiddleware': 500,
        },
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
        res = self.collection.find({"$and":[{"doubanUrl":{"$ne":None}},{"errorCode":{"$exists":False}},{"doubanCrawlDate":{"$exists":False}}]}).limit(count);
        urls = [];
        for post in res:
            # print(post)
            urls.append(post['doubanUrl']);
        logger.info('fetch {} new url from mongo'.format(len(urls)));
        return urls

    def addSomeUrls(self, urls):
        for url in urls:
            res = self.collection.update({'doubanUrl':url}, {'$set':{'doubanUrl':url}}, upsert=True)

    def __init__(self, *a, **kw):
        logger = logging.getLogger('scrapy.core.scraper')
        logger.setLevel(logging.INFO)
        super(DoubanBookCrawlSpider, self).__init__(*a, **kw)
        urls = self.getSomeUrls(10)
        for url in urls:
            self.start_urls.append(url)

    def parse_book(self, response):
        if response.status == 404 or response.status == 403:
            url = response.request.url
            errcode = response.status
            logger.warn("BAD STATUS {} @ {}".format(errcode, url))
            # bookItem = doubanBookItem()
            # res = self.collection.update({'doubanUrl':url}, {'$set':{'errorCode':errcode}}, upsert=True)
            # newUrls = self.getSomeUrls(5);
            # for url in newUrls:
            #     logger.info('gonna queue request {}'.format(url));
            #     yield Request(url ,callback=self.parse);
            return;

        TITLE_SEL = '#wrapper > h1 > span';
        bookTitle = response.css(TITLE_SEL).css('::text').extract_first();
        if bookTitle is None :
            #probably being banned
            logger.error("wrong page ...");
            logger.error(response.request.url);
            logger.error(repsonse.body);
            # self.banned+=1;
            # if(self.banned > 10):
            #     raise CloseSpider('being banned')
            return;

        DETAIL_BOOK_INFO_BLOCK_SEL = '#info';
        DETAIL_PAGE_BOOK_INFO_LEN_SEL = '#info';
        DETAIL_PAGE_BOOK_INFO_SEL = '#info > span:nth-child(INDEX';
        DETAIL_RATING_NUMBER_SEL = '#interest_sectl > div > div.rating_self.clearfix > strong';
        DETAIL_RATING_USER_NUMBER_SEL = '#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > span > a';
        DETAIL_BRIEF_SEL = '#link-report ';
        # DETAIL_BRIEF_SEL = '#link-report > * > div.intro';
        # DETAIL_BRIEF_SEL = '#link-report > span.short > div > p';
        DETAIL_BRIEF_SEL3 = '#link-report > * > div > p'

        # DETAIL_AUTHOR_BRIEF_SEL = 'div.related_info > div:nth-child(1) > * > div.intro';
        DETAIL_AUTHOR_BRIEF_SEL = '#content > div > div.article > div.related_info > div:nth-child(4) > span.short > div > p';
        DETAIL_AUTHOR_BRIEF_SEL2 = '#content > div > div > div.related_info > div:nth-child(4) > * > div > p'
        # DETAIL_AUTHOR_BRIEF_SEL3 = '#content > div > div > div.related_info > div:nth-child(4) '

        # DETAIL_AUTHOR_BRIEF_SEL = 'div.related_info > div:nth-child(1) > * > div.intro';
        DETAIL_AUTHOR_BRIEF_SEL3 ='#content > div > div.article > div.related_info > div:nth-child(4) > span.short > div > p';

        DETAIL_TAGS_SEL = '#db-tags-section > div.indent  > span > a';
        DETAIL_TAGS_SEL2 = '#db-tags-section > div.indent  > span ';
        DETAIL_TAGS_LEN_SEL = '#db-tags-section > div.indent > span';
        DETAIL_COMMENTS = '#content > div > div.article > div.related_info > div.mod-hd > h2 > span.pl > a';
        SEARCH_URL_TEMPLATE = 'https://book.douban.com/subject_search?search_text=ISBN&cat=1001';
        REC_SECTION_SEL       = '#db-rec-section > div > dl > dd';
        REC_SECTION_ARRAY_SEL = '#db-rec-section > div > dl > dt > a';
        COVER_SEL = '#mainpic > a > img';

        bookbrief = response.css(DETAIL_BRIEF_SEL3).css('::text').extract()
        authorInfo = (response.css(DETAIL_AUTHOR_BRIEF_SEL2).css('::text').extract());
        bookInfo = (response.css(DETAIL_PAGE_BOOK_INFO_LEN_SEL).css('::text').extract());

        bookItem = doubanBookItem()
        bookItem['doubanUrl'] = response.request.url;
        bookItem['doubanBookName'] = bookTitle;
        bookItem['doubanBookMeta'] = bookInfo
        bookItem['doubanTags'] = response.css(DETAIL_TAGS_SEL).css('::text').extract();
        bookItem['doubanRating'] = response.css(DETAIL_RATING_NUMBER_SEL).css('::text').extract_first();
        bookItem['doubanRatingUser'] = response.css(DETAIL_RATING_USER_NUMBER_SEL).css('::text').extract_first();
        bookItem['doubanBookBrief'] = bookbrief;
        bookItem['doubanAuthorBrief'] = authorInfo;
        bookItem['doubanCrawlDate'] = datetime.datetime.utcnow();
        # bookItem['doubanISBN']=
        self.counter += 1;
        proxy = response.request.meta.get('proxy','Bare')
        logger.info(u'NO.{} {} [from {}]'.format(self.counter, bookItem['doubanBookName'], proxy));

        items = response.css(REC_SECTION_SEL);

        for item in items:
            # print('extracting href from alink')
            # print(detail_url);
            href = (item.css('a::attr(href)').extract()[0]);
            urlOnly = doubanBookItem();
            # urlOnly['doubanUrl'] = href;
            self.addSomeUrls([href])

        # qsize = self.crawler.engine.slot.scheduler.__len__();
        # running = len(self.crawler.engine.slot.inprogress);
        # logger.info('PENDING_QUEUE_SIZE: {}, RUNNING QUEUE SIZE: {}'.format(qsize, running));
        yield  bookItem;
