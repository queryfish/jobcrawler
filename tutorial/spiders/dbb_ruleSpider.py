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
import re
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
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)   # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379

    # handle_httpstatus_list = [301, 302];
    # start_urls = ['https://book.douban.com/subject/1089243/']
    # start_urls = ['https://book.douban.com/review/best/']
    start_urls = ['https://book.douban.com/tag/?view=type&icn=index-sorttags-all']
    rules = (
        Rule(LinkExtractor(allow=(r'^https://book.douban.com/subject/\d+/$')), callback="parse_book", follow=True,process_links="link_filter", process_request="no_dupefilter"),
        # Rule(LinkExtractor(allow=(r'^https://book.douban.com/tag/')), callback="parse_tag", follow=True, process_links="link_filter"),
    )
    custom_settings = {
        "LOG_LEVEL": 'DEBUG',
        "LOG_STDOUT" : True,
        # "LOG_FILE": './dbb_logfile.log',
        # "DUPEFILTER_DEBUG": True,
        "LOGSTATS_INTERVAL" : 60.0,
        # Configure maximum concurrent requests performed by Scrapy (default: 16)
        # "CONCURRENT_REQUESTS": 2,
        # "DOWNLOAD_DELAY":0.9,
        # "DUPEFILTER_CLASS": 'scrapy.dupefilters.BaseDupeFilter',
        # Enable and configure HTTP caching (disabled by default)
        # See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
        # "HTTPCACHE_ENABLED": True,
        # "HTTPCACHE_EXPIRATION_SECS": 0,
        # "HTTPCACHE_DIR": 'httpcache',
        # "HTTPCACHE_IGNORE_HTTP_CODES":[],
        # "HTTPCACHE_STORAGE":'scrapy.extensions.httpcache.FilesystemCacheStorage',
        # "HTTP_PROXY": 'http://127.0.0.1:8123/',

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
        }
    }

    def getSomeUrls(self, count):
        # res = self.collection.find({"$and":[{"doubanUrl":{"$ne":None}},{"errorCode":{"$exists":False}},{"doubanCrawlDate":{"$exists":False}}]}).limit(count);
        # urls = [];
        # for post in res:
        #     # print(post)
        #     urls.append(post['doubanUrl']);
        # logger.info('fetch {} new url from mongo'.format(len(urls)));
        # return urls
        queueSet = 'bookQueueSet'
        urls = self.r.srandmember(queueSet, count)
        map(lambda x:self.r.srem(queueSet, x), urls)
        return urls

    def addSomeUrls(self, urls):
        for url in urls:
            res = self.collection.update({'doubanUrl':url}, {'$set':{'doubanUrl':url}}, upsert=True)

    def setupRedis(self):
        tmpSet = 'tmpUrlSet'
        formalSet = 'doubanBookUrlSet'
        if self.r.exists(tmpSet):
            self.r.delete(tmpSet)
        if self.r.exists(formalSet):
            self.r.delete(formalSet)
        res = self.collection.find({"$and":[{"doubanUrl":{"$ne":None}},{"doubanCrawlDate":{"$exists":True}}]},{"doubanUrl":1, "_id":0});
        l = list(res)
            # for i in l :
            #     logger.info(i)
        urls = list(map(lambda x:x['doubanUrl'], l))
        logger.info("SMOKING GUN")
            # logger.info(self.r.smembers(formalSet))
        self.r.sadd(formalSet, *urls)
        logger.info(self.r.scard(formalSet))
            # self.r.delete(formalSet)

        if self.r.exists('queueSet'):
            q = self.r.smembers('queueSet')
            for e in q:
                if re.match(r'^https://book.douban.com/subject/\d+/$', e) :
                    self.r.sadd('bookQueueSet', e)
                    self.r.srem('queueSet', e)
        # raise CloseSpider('being banned')

    def __init__(self, *a, **kw):
        logger = logging.getLogger('scrapy.core.scraper')
        logger.setLevel(logging.INFO)
        self.setupRedis()
        map(lambda x:self.start_urls.append(x), self.getSomeUrls(10))
        super(DoubanBookCrawlSpider, self).__init__(*a, **kw)

    def no_dupefilter(self, request):
        request.dont_filter = True
        return request;

    def link_filter(self, links):
        # logger.info("processing links : {}".format(links))
        if links == None or len(links) == 0:
            return links

        urls = {}
        for l in links:
            uniUrl = unicode(l.url, "utf-8")
            urls[uniUrl] = l

        tmpSet = 'tmpUrlSet'
        formalSet = 'doubanBookUrlSet'
        queueSet = 'bookQueueSet'
        self.r.delete(tmpSet)
        self.r.sadd(tmpSet, *urls.keys())
        diff = self.r.sdiff(tmpSet, formalSet, queueSet)
        if(len(diff) > 0):
            self.r.sadd(queueSet, *diff)
        logger.info('with the DIFF :{}'.format(len(diff)))
        return list(map(lambda x:urls[x], diff))
        # l = []
        # for i in diff:
        #     l.append(urls[i])
        # return l;
        # if len(diff) == 0 :
            # logger.info("not a match {}".format(diff))
            # return []
        # else:
            # logger.info('before UNION :{}'.format(self.r.scard(formalSet)))
            # self.r.sadd(formalSet, *diff)
            # self.r.delete(tmpSet)
            # logger.info('DIFF LINKS :{}'.format(diff))
            # logger.info('after UNION :{}'.format(self.r.scard(formalSet)))
            # raise CloseSpider('being banned')
            # return list(map(lambda x:urls[x], diff))

    def parse_tag(self, response):
        qsize = self.crawler.engine.slot.scheduler.__len__();
        running = len(self.crawler.engine.slot.inprogress);
        logger.info('PENDING_QUEUE_SIZE: {}, RUNNING QUEUE SIZE: {}'.format(qsize, running));
        formalSet = 'doubanBookUrlSet'
        queueSet = 'queueSet'
        url = response.request.url
        self.r.srem(formalSet, url)
        self.r.sadd(queueSet, url)

    def parse_book(self, response):
        formalSet = 'doubanBookUrlSet'
        queueSet = 'bookQueueSet'
        url = response.request.url
        self.r.srem(queueSet, url)
        self.r.sadd(formalSet, url)

        # self.r.sadd(formalSet, response.request.url)
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
            logger.error(response.body);
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
        logger.info(u'NO.{} {} [from {}]'.format(self.counter, bookItem['doubanBookName'], response.request.url));

        items = response.css(REC_SECTION_SEL);

        # for item in items:
        #     # print('extracting href from alink')
        #     # print(detail_url);
        #     href = (item.css('a::attr(href)').extract()[0]);
        #     urlOnly = doubanBookItem();
        #     # urlOnly['doubanUrl'] = href;
        #     self.addSomeUrls([href])

        qsize = self.crawler.engine.slot.scheduler.__len__();
        running = len(self.crawler.engine.slot.inprogress);
        logger.info('TOTAL Q_SIZE: {}, PENDING_QUEUE_SIZE: {}, RUNNING QUEUE SIZE: {}'.format(qsize+running, qsize, running));
        if(qsize+running < 100):
            for r in self.getSomeUrls(100):
                yield Request(r,callback=self.parse_book, dont_filter=True);
        yield  bookItem;
