# -*- coding: utf-8 -*-
import logging
import requests
import json
import random

logger = logging.getLogger(__name__)


class RotateProxyManager(object):
    orderid = '907089398818285'  # 订单号
    get_proxy_url = "https://dps.kdlapi.com/api/getdps/?orderid={}&num={}&pt=1&format=json&sep=1"
    check_proxy_url = "https://dps.kdlapi.com/api/checkdpsvalid/?orderid={}&proxy={}&signature={}"
    # reserved_proxy_count = 900;
    # max_proxies = 10;
    # switches = 0;
    # proxy_pool = [];
    # cloud_times = 0;
    # cur_proxy = {"proxy":"202.183.32.182:80", "good":0, "bad":0};
    cur_url = '';
    POOL = [];
    cursor = 0
    # [
    #     '202.183.32.185:80',
    #     '93.190.137.63:8080',
    #     '93.190.137.58:8080',
    #     '202.183.32.181:80',
    #     '79.114.6.86:8080',
    #     '134.119.188.153:8080',
    #     '134.119.188.154:8080',
    #     '134.119.188.152:8080',
    #     '134.119.188.151:8080',
    #     '134.119.188.147:8080',
    #     '134.119.188.158:8080',
    #     '134.119.188.148:8080',
    #     '134.119.188.150:8080',
    # ]
    def __init__(self):
        self.get_proxy_from_cloud(2)
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
        fetch_url = self.get_proxy_url.format(self.orderid, count)
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))
        logger.info(content);
        ips = content['data']['proxy_list']
        left = content['data']['order_left_count']
        for proxy in ips:
            ascproxy = proxy.encode('ascii')
            if ascproxy not in self.POOL
                self.POOL.append(ascproxy)
        return ips;

    def check_proxy_from_cloud(self, proxy):
        signature = '7xwlkipjspls4gaqm00b0bpyrojc13u3'
        fetch_url = self.check_proxy_url.format(self.orderid, proxy,signature)
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))
        logger.info(content);
        statusDict = content['data']
        valid = statusDict[proxy]
        # ips = content['data']['proxy_list']
        # left = content['data']['order_left_count']
        return valid

    def invalidProxy(self, proxy):
        #1\ if proxy is in the pool, find the index
        ipport = proxy.replace("http://","")
        print(self.POOL)
        logger.warn("gonna check it in the pool {}".format(ipport))
        if ipport in self.POOL:
            logger.warn("gonna revalid it {}".format(ipport))
            valid = self.check_proxy_from_cloud(ipport)
            if valid == False:
                logger.warn("gonna remove it {}".format(ipport))
                self.POOL.remove(ipport)
                self.get_proxy_from_cloud(1)
        #2\ validate the proxy from the cloud
        #3\ remove it from the pool if invalid
        #4\ get a new proxy from the api and append it to the pool

        return
