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
    cur_url = '';
    POOL = [];
    cursor = 0
    concur = 0;
    page = 1;
    score = {};
    # auth = kdl.Auth("yourorderid", "yourorderapikey")
    # client = kdl.Client(auth)

    def __init__(self):
        logger.info('init free proxy fetcher')
        self.get_proxy_from_cloud(1)
        settings = get_project_settings();
        self.concur = settings.get('CONCURRENT_REQUESTS');
        self.cur_url = self.nextProxy()
        # self.check_proxy_from_cloud(self.cur_url)

    def proxy(self):
        # mo = min(self.concur, len(self.POOL))
        # self.cursor = self.cursor % mo
        return self.POOL[self.cursor];

    def nextProxy(self):
        self.cursor += 1
        # mo = min(self.concur, len(self.POOL))
        mo = len(self.POOL);
        self.cursor = self.cursor % mo
        # self.cursor = self.cursor % len(self.POOL)
        return self.POOL[self.cursor];

    def get_proxy_from_cloud(self, count):
        # self.page = (self.page)%2
        # r = requests.get(self.get_proxy_url.format(self.page))
        r = requests.get(self.get_proxy_url)
        logger.error(r.status_code)
        # logger.error(r.text)
        # self.page += 1
        if r.status_code != 200:
            # time.sleep(60);
            # r = requests.get(self.get_proxy_url.format(self.page))
            # if r.status_code != 200:
                logger.error("fail to fetch proxy")
                logger.error(r.text)
                raise CloseSpider('no free proxies')
                return False
        IP_SELECTOR = '#list > table > tbody > tr';
        response = HtmlResponse(url='',body=r.text, encoding=r.encoding)
        items = response.css(IP_SELECTOR)
        for item in items:
            c = item.css('td::text').extract();
            d = {}
            d['ip'] = c[0]
            d['port'] = c[1]
            d['prot'] = c[3]
            proxy = "{}://{}:{}".format(d['prot'],d['ip'],d['port'])
            ascproxy = proxy.encode('ascii').lower()
            logger.info(ascproxy)
            if ascproxy not in self.POOL:
                self.POOL.append(ascproxy)
        return self.POOL

        # ips = content['data']['proxy_list']
        # left = content['data']['order_left_count']
        # for proxy in ips:
        #     ascproxy = proxy.encode('ascii')
        #     if ascproxy not in self.POOL:
        #         score[ascproxy] = 0;
        #         self.POOL.append(ascproxy)
        # return ips;

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
        # self.cursor += 1
        self.nextProxy();
        #1\ if proxy is in the pool, find the index
        #2\ validate the proxy from the cloud
        #3\ remove it from the pool if invalid
        #4\ get a new proxy from the api and append it to the

        if proxy in self.POOL:
            # self.POOL.remove(proxy);
            # self.POOL.append(proxy);
            valid = self.check_proxy_from_cloud(proxy)
            if valid == False:
                if proxy in self.POOL:
                    logger.warn("gonna remove it {}".format(proxy))
                    self.POOL.remove(proxy)
        #         self.get_proxy_from_cloud(1)
                    return
        else:
            logger.warn("Already removed {}".format(proxy))
        if len(self.POOL) == 0:
            self.get_proxy_from_cloud(1)
        return

    def banProxy(self, proxy):
        # self.cursor += 1
        self.nextProxy();
        #1\ if proxy is in the pool, find the index
        #2\ validate the proxy from the cloud
        #3\ remove it from the pool if invalid
        #4\ get a new proxy from the api and append it to the

        if proxy in self.POOL:
            self.POOL.remove(proxy);
        else:
            logger.warn("Already removed {}".format(proxy))
        if len(self.POOL) == 0:
            self.get_proxy_from_cloud(1)

        return

    def badProxy(self, proxy):
        # self.cursor += 1

        #1\ if proxy is in the pool, find the index
        #2\ validate the proxy from the cloud
        #3\ remove it from the pool if invalid
        #4\ get a new proxy from the api and append it to the
        d = self.score
        if d.has_key(proxy) :
            proxy_score = d[proxy];
            d[prxoy] = proxy_score +1;
            if d[proxy] > 10 :
                del d[proxy]
                if proxy in self.POOL:
                    self.POOL.remove(proxy);
        else:
            logger.warn("Already removed {}".format(proxy))
        if len(self.POOL) == 0:
            self.get_proxy_from_cloud(1)

        return
