# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
from scrapy import signals
from scrapy.conf import settings
from tutorial.resource import USER_AGENT_LIST
from tutorial.resource import PROXIES
import random

logger = logging.getLogger(__name__)

class RandomProxy(object):
    def process_request(self,request, spider):
        proxy = random.choice(PROXIES)
        print('SWITCH PROXI');
        print(proxy);
        request.meta['proxy'] = 'http://%s'% proxy

class RandomUserAgent(object):
    def process_request(self, request, spider):
        ua = random.choice(USER_AGENT_LIST)
        # logger.warn("SWITCHING UA \n{}".format(ua));
        request.headers.setdefault('User-Agent', ua)


class TutorialSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('HTTP_PROXY')
        pass


class LagouMiddleware(object):

    def process_request(self,request,spider):
        request.headers['cookie'] = settings.get('LAGOU_COOKIE')

class ZhipinMiddleware(object):

    def process_request(self,request,spider):
        request.headers['cookie'] = settings.get('BOSS_COOKIE')
