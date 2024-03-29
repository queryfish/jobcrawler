# -*- coding: utf-8 -*-
import logging
import requests
import json
import random
import kdl
logger = logging.getLogger(__name__)


class RotateProxyManager(object):
    orderid = '977309259542981'  # 订单号
    get_proxy_url = "https://dps.kdlapi.com/api/getdps/?orderid={}&num={}&pt=1&format=json&sep=1"
    signature = 'exw3mf50r22o5v79w6a04b1kmey0r40f'
    # fetch_url = self.check_proxy_url.format(self.orderid, proxy,signature)

    # reserved_proxy_count = 900;
    # max_proxies = 10;
    # switches = 0;
    # proxy_pool = [];
    # cloud_times = 0;
    # cur_proxy = {"proxy":"202.183.32.182:80", "good":0, "bad":0};
    cur_url = '';
    POOL = [];
    cursor = 0
    auth = kdl.Auth("977309259542981", "exw3mf50r22o5v79w6a04b1kmey0r40f")
    client = kdl.Client(auth)

    def __init__(self):
        self.get_proxy_from_cloud(1)
        self.cur_url = self.nextProxy()
        # self.check_proxy_from_cloud(self.cur_url)

    def prettyList(self):
        for p in self.proxy_pool:
            logger.info(p)

    def nextProxy(self):
        self.cursor += 1
        self.cursor = self.cursor % len(self.POOL)
        return self.POOL[self.cursor];

    def get_proxy_from_cloud(self, count):
        # fetch_url = self.get_proxy_url.format(self.orderid, count)
        # r = requests.get(fetch_url)
        r = self.client.get_dps(count, sign_type='hmacsha1', format='json')
        # print("dps proxy: ", r)
        # if r.status_code != 200:
        #     logger.error("fail to fetch proxy")
        #     return False
        # content = json.loads(r.content.decode('utf-8'))
        # logger.info(content);
        # ips = content['data']['proxy_list']
        # left = content['data']['order_left_count']
        ips = r;
        if len(ips) == 0:
            logger.info("should stop the spider")
            logger.info(ips)
            from scrapy.exceptions import CloseSpider
            raise CloseSpider('no more proxies')

        for proxy in ips:
            ascproxy = proxy.encode('ascii')
            if ascproxy not in self.POOL:
                self.POOL.append(ascproxy)
        # return ips;

    def check_proxy_from_cloud(self, proxy):
        # check_proxy_url = "https://dps.kdlapi.com/api/checkdpsvalid/?orderid={}&proxy={}&signature
        r = self.client.check_dps_valid(proxy)
        # logger.info('check from result {}'.format(r))
        # r = requests.get(fetch_url)
        # if r.status_code != 200:
        #     logger.error("fail to fetch proxy")
        #     return False
        # content = json.loads(r.content.decode('utf-8'))
        # logger.info(content);
        # statusDict = content['data']
        # valid = statusDict[proxy]
        valid  = r[proxy]
        return valid

    def invalidProxy(self, proxy):
        #1\ if proxy is in the pool, find the index
        logger.info(self.POOL)
        ipport = proxy.replace("http://","")
        logger.warn("gonna check it in the pool {}".format(ipport))
        if ipport in self.POOL:
            # logger.warn("gonna revalid it {}".format(ipport))
            valid = self.check_proxy_from_cloud(ipport)
            if valid == False:
                logger.warn("gonna remove it {}".format(ipport))
                self.POOL.remove(ipport)
                self.get_proxy_from_cloud(1)
        if len(self.POOL) ==  0:
            self.get_proxy_from_cloud(1)
        #2\ validate the proxy from the cloud
        #3\ remove it from the pool if invalid
        #4\ get a new proxy from the api and append it to the pool

        return
