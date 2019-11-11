# -*- coding: utf-8 -*-
import logging
import requests
import json
import random
# import kdl
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider
logger = logging.getLogger(__name__)

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class freeRotateProxyManager(object):
    __metaclass__ = Singleton
    # get_proxy_url = "https://www.kuaidaili.com/free/inha"
    get_proxy_url = "https://www.kuaidaili.com/free/intr/"
    free2 = 'http://www.xiladaili.com/'
    POOL = [];
    cursor = 0
    concur = 0;
    page = 1;
    scorePool = {};
    goodness = {};
    badness = {};
    tolerance = 3;

    def __init__(self):
        self.get_free_prox(1)
        settings = get_project_settings();
        self.concur = settings.get('CONCURRENT_REQUESTS');

    def proxy(self):
        # return self.POOL[0];
        # logger.info('PROXY CUROSOR ---> {}'.format(self.cursor))
        if len(self.POOL) < self.concur:
            self.get_free_prox(1);
            self.cursor = 0;
        else:
            self.cursor += 1;
        self.cursor = self.cursor % (self.concur)
        return self.POOL[self.cursor];

    # def nextProxy(self):
    #     self.cursor += 1
    #     # mo = min(self.concur, len(self.POOL))
    #     mo = len(self.POOL);
    #     self.cursor = self.cursor % mo
    #     # self.cursor = self.cursor % len(self.POOL)
    #     return self.POOL[self.cursor];

    def get_free_prox(self, count):
        # r = requests.get(self.get_proxy_url.format(self.page))
        get_proxy_url = "https://www.kuaidaili.com/free/intr/"
        free2 = 'http://www.xiladaili.com/'
        r = requests.get(free2)
        logger.error(r.status_code)
        # logger.error(r.text)
        if r.status_code != 200:
                logger.error("fail to fetch proxy")
                logger.error(r.text)
                raise CloseSpider('no free proxies')
                return False
        response = HtmlResponse(url='',body=r.text, encoding=r.encoding)
        self.POOL = self.responseParser_xila(response)
        # self.POOL.insert(0,'None')
        v = {}
        for k in self.POOL :
            v[k] = 0
        self.scorePool = v;
        self.badness = v.copy()
        self.goodness = v.copy()


    def responseParser_kdl(self, response):
        IP_SELECTOR = '#list > table > tbody > tr';
        items = response.css(IP_SELECTOR)
        pool = []
        for item in items:
            c = item.css('td::text').extract();
            d = {}
            d['ip'] = c[0]
            d['port'] = c[1]
            d['prot'] = c[3]
            proxy = "{}://{}:{}".format(d['prot'],d['ip'],d['port'])
            ascproxy = proxy.encode('ascii').lower()
            logger.info(ascproxy)
            # pool[ascproxy] = 0;
            pool.append(ascproxy)
        return pool

    def responseParser_xila(self, response):
        LIST_SELECTOR = '#scroll > table > tbody > tr';
        items = response.css(LIST_SELECTOR)
        logger.info('get some proxies {}'.format(len(items)))
        pool = {}
        for item in items:
            c = item.css('td::text').extract();
            # logger.info('extracted ip {}'.format(c))
            #1.免费ip代理,2.IP匿名度,3.IP类型,4.IP位置,5.响应速度,6.存活时间,7.最后验证时间,8.打分
            d = {}
            d['ipandport'] = c[0]
            d['score'] = c[7]
            d['speed'] = c[4]
            d['protocol'] = c[2]
            logger.info(d)
            p = d['ipandport'].encode('ascii').lower()
            pool["http://{}".format(p)] = int(c[7].encode('ascii'))
        a = []
        for key, value in sorted(pool.items(), key=lambda item: item[1]):
            a.append(key)
        a.reverse()
        return a

    def check_proxy_from_cloud(self, proxy):
        return False
        # try:
        #     r = requests.get('https://www.baidu.com', timeout = 10, proxies = {"http":proxy})
        #     logger.info("Proxy status code {}".format(r.status_code))
        #     if r.status_code != 200:
        #         return False;
        #     return True;
        # except requests.exceptions.RequestException as e:
        #     logger.error(e);
        #     return False

    def invalidProxy(self, proxy):
        #1\ if proxy is in the pool, find the index
        #2\ validate the proxy from the cloud
        #3\ remove it from the pool if invalid
        #4\ get a new proxy from the api and append it to the
        if proxy in self.POOL:
            # self.POOL.remove(proxy);
            # self.POOL.append(proxy);
            valid = self.check_proxy_from_cloud(proxy)
            if valid == False:
                if len(self.POOL) <= 1:
                    self.get_free_prox(1)
                else:
                    logger.warn("gonna remove it {}".format(proxy))
                    self.POOL.remove(proxy)
        else:
            logger.warn("Already removed {}".format(proxy))

    def badProxy(self, proxy):
        # self.cursor += 1
        #1\ if proxy is in the pool, find the index
        #2\ validate the proxy from the cloud
        #3\ remove it from the pool if invalid
        #4\ get a new proxy from the api and append it to the
        d = self.scorePool
        if d.has_key(proxy):
            d[proxy] += 1;

        if proxy in self.POOL:
            if d[proxy] > self.tolerance :
                logger.info('BOOKING GOOD.{} BAD.{} for [{}]'.format(self.badness[proxy], self.goodness[proxy], proxy))
                if len(self.POOL) <= 1:
                    self.get_free_prox(1)
                else:
                    # del d[proxy]
                    self.POOL.remove(proxy)
        else:
            logger.warn("Already removed {}".format(proxy))

        if self.badness.has_key(proxy):
            self.badness[proxy] += 1
            logger.info('BAD.{} for [{}]'.format(self.badness[proxy], proxy))
        return

    def goodProxy(self, proxy):
        d = self.scorePool
        if d.has_key(proxy) :
            d[proxy] = 0;
        if self.goodness.has_key(proxy):
            self.goodness[proxy] += 1
            logger.info('GOOD.{} for [{}]'.format(self.goodness[proxy], proxy))
