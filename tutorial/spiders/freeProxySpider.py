#!/usr/bin/python
#coding:utf-8

import logging
import scrapy
import pymongo
from tutorial.items import doubanBookItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider
import  json
import  time
import datetime
import  random
# import redis
from scrapy.conf import settings

logger = logging.getLogger(__name__)


#zhipin 爬虫
class DoubanBookSpider(scrapy.Spider):
    handle_httpstatus_list = [404, 403]
    name = "freeproxy"
    allowed_domains = ["douban.com"]
    client = pymongo.MongoClient(host="127.0.0.1", port=27017)
    db = client['sobooks']
    collection =  db['books']
    step = 10;
    counter = 0;
    banned = 0;
    # handle_httpstatus_list = [301, 302];
    # get_proxy_url = "https://www.kuaidaili.com/free/inha"
    # get_proxy_url = "https://www.kuaidaili.com/free/intr/"
    free1 = 'https://www.xicidaili.com/'
    free2 = 'http://www.xiladaili.com/'
    start_urls = [free2]
    custom_settings = {
        "LOG_LEVEL": 'DEBUG',
        "LOG_STDOUT": True,
        # "LOG_FILE": './{}_logfile.log'.format(name),
        "HTTPERROR_ALLOWED_CODES":[403,404],
        # Obey robots.txt rules
        #ROBOTSTXT_OBEY = True
        "RETRY_ENABLED": False,
        #RETRY_TIMES = 1
        "DOWNLOAD_TIMEOUT" : 7.5,
        "DUPEFILTER_DEBUG": True,
        "LOGSTATS_INTERVAL" : 300.0,
        # Configure maximum concurrent requests performed by Scrapy (default: 16)
        "CONCURRENT_REQUESTS": 2,
        "DOWNLOAD_DELAY":.1,

        "AUTOTHROTTLE_ENABLED": True,
        # The initial download delay
        "AUTOTHROTTLE_START_DELAY": 0.1,
        # The maximum download delay to be set in case of high latencies
        "AUTOTHROTTLE_MAX_DELAY": 5,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 5.0,
        # Enable showing throttling stats for every response received:
        "AUTOTHROTTLE_DEBUG": True,

        "ITEM_PIPELINES":{
            'tutorial.pipelines.DoubanBookPipeline': 300,
        },
        "DOWNLOADER_MIDDLEWARES":{
            'tutorial.middlewares.RandomUserAgent': 2,
            # 'tutorial.middlewares.RandomProxy':301,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            # 'tutorial.middlewares_proxy.TunnelProxyMiddleware': 100,
            # 'tutorial.middlewares_rotate_proxy.RegularProxyMiddleware': 100,
            # 'tutorial.middlewares_rotate_proxy.fixedProxyMiddleware': 100,
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'tutorial.middlewares_rotate_proxy.CustomRetryMiddleware': 500,
            # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware':2 ,
            # 'tutorial.middlewares_proxy.AgentMiddleware': 1,
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

    def __init__(self, *a, **kw):
        super(DoubanBookSpider, self).__init__(*a, **kw)

    def parse(self, response):
        logger.info(response)
        # logger.info(response.body)
        if(response.status >200 and repsonse.status < 300 ):
            return

        # IP_SELECTOR = '#scroll > table > tbody > tr:nth-child(1) > td:nth-child(1)'
        # '#scroll > table > tbody > tr:nth-child(1) > td:nth-child(1)'
        LIST_SELECTOR = '#scroll > table > tbody > tr';
        IP_SELECTOR = '#list > table > tbody > tr';
        items = response.css(LIST_SELECTOR)
        logger.info('get some proxies {}'.format(len(items)))
        for item in items:
            c = item.css('td::text').extract();
            # logger.info('extracted ip {}'.format(c))
            #1.免费ip代理,2.IP匿名度,3.IP类型,4.IP位置,5.响应速度,6.存活时间,7.最后验证时间,8.打分
            d = {}
            d['ipandport'] = c[0]
            d['score'] = c[7]
            d['speed'] = c[4]
            # proxy = "{}://{}:{}".format(d['prot'],d['ip'],d['port'])
            proxy = d['ipandport']
            ascproxy = proxy.encode('ascii').lower()
            logger.info(d)

        # if response.status == 404 or response.status == 403:
