# -*- coding: utf-8 -*-
import logging
import requests
import json
import random

logger = logging.getLogger(__name__)


class PaidProxyManager(object):
    orderid = '907089398818285'  # 订单号
    # orderid = '957092713770940'
    # 提取代理链接，以私密代理为例
    api_url = "https://dps.kdlapi.com/api/getdps/?orderid={}&num=1&pt=1&format=json&sep=1"
    tunnel_url = "https://tps.kdlapi.com/api/gettpsip/?orderid={}&signature=s0hwg7zopaalk51at1i2zf9ltc80zwet"
    reserved_proxy_count = 900;
    max_proxies = 10;
    switches = 0;
    proxy_pool = [];
    cloud_times = 0;
    cur_proxy = {"proxy":"202.183.32.182:80", "good":0, "bad":0};
    cur_url = '';
    PROXIES = [
        '202.183.32.185:80',
        '93.190.137.63:8080',
        '93.190.137.58:8080',
        '202.183.32.181:80',
        '79.114.6.86:8080',
        '134.119.188.153:8080',
        '134.119.188.154:8080',
        '134.119.188.152:8080',
        '134.119.188.151:8080',
        '134.119.188.147:8080',
        '134.119.188.158:8080',
        '134.119.188.148:8080',
        '134.119.188.150:8080',
    ]
    def __init__(self):
        self.cur_url = self.get_proxy_from_cloude()

    def threshold(self):
        return 1;
        # good = self.cur_proxy['good'];
        # if(good <= 0):
        #     return 1;
        # else:
        #     if( good > 5):
        #         return 5;
        #     else:
        #         return good;

    def prettyList(self):
        for p in self.proxy_pool:
            logger.info(p)

    def proxy(self):
        if(self.cur_url == ""):
            self.cur_url = self.switch_proxy();
        return self.cur_url;

    def good(self):
        self.cur_proxy['good'] += 1;

    def bad(self):
        self.cur_proxy['good'] -= 1;

    def switch_proxy(self):
        """
            提取一个代理
        """
        self.switches = self.switches + 1;
        # if(self.switches%2 == 0):
            # self.cur_url  = '202.183.32.185:80'
        # else :
        self.cur_url = self.get_proxy_from_cloude();
        # if(self.switches >= self.max_proxies):
        #     self.switches = 0;
        #     self.cur_url = self.get_proxy_from_cloude();
        #     logger.info("PROXY SWITCH TO"+self.cur_url);
        #     return self.cur_url;
        # else :
        return self.cur_url;

    def get_proxy_from_cloude(self):
        fetch_url = self.api_url.format(self.orderid)
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))
        logger.info(content);
        ips = content['data']['proxy_list']
        left = content['data']['order_left_count']
        # if(left >= self.reserved_proxy_count):
        return ips[0];

    def get_proxy_from_cloud_complex(self):
        self.cloud_times += 1;
        if(self.cloud_times > 10):
            self.cur_url = '202.183.32.185:80'
            return self.cur_url;
        fetch_url = self.api_url.format(self.orderid)
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))
        logger.info(content);
        ips = content['data']['proxy_list']
        left = content['data']['order_left_count']
        # if(left >= self.reserved_proxy_count):
        return ips[0];

    # def get_tunnel_proxy(self):
    #     self.cloud_times += 1;
    #     fetch_url = self.tunnel_url.format(self.orderid)
    #     r = requests.get(fetch_url)
    #     if r.status_code != 200:
    #         logger.error("fail to fetch proxy")
    #         return False
    #     content = json.loads(r.content.decode('utf-8'))
    #     logger.info(content);
    #     ip = content['data']['current_ip']
    #     return ip;
