# -*- coding: utf-8 -*-
import logging
import requests
import json
import random

logger = logging.getLogger(__name__)


class ProxyManager(object):
    orderid = '956231220141933'  # 订单号
    # 提取代理链接，以私密代理为例
    api_url = "https://dps.kdlapi.com/api/getdps/?orderid={}&num=1&pt=1&format=json&sep=1"
    reserved_proxy_count = 900;
    max_proxies = 2;
    switches = 0;
    proxy_pool = [];
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
        for prx in self.PROXIES:
            self.proxy_pool.append({"proxy":prx, "good":0});
        self.cur_proxy = random.choice(self.proxy_pool)
        print(self.proxy_pool)

    def threshold(self):
        good = self.cur_proxy['good'];
        if(good <= 0):
            return 1;
        else:
            if( good > 5):
                return 5;
            else:
                return good;

    def switch_proxy(self):
        # find the max goodness and the element except the current one ?
        n = len(self.proxy_pool)
        max = 0
        max_index = 0
        for i in range(1, n):
            p = self.proxy_pool[i];
            if(p['proxy'] == self.cur_proxy['proxy']):
                pass
            if p['good'] >= max:
                max_index = i
        # if(max == 0):
            # self.cur_proxy = random.choice(self.proxy_pool)
        # else:
        self.cur_proxy = self.proxy_pool[max_index];
        logger.info("SWITCHING PROXY : GOOD {}".format(max))
        self.prettyList();
        return self.cur_proxy['proxy'];

    def prettyList(self):
        for p in self.proxy_pool:
            logger.info(p)

    def proxy(self):
        return self.cur_proxy['proxy'];
        # if(self.cur_url == ""):
        #     self.cur_url = self.fetch_one_proxy_from_cloud();
        # return self.cur_url;

    def good(self):
        self.cur_proxy['good'] += 1;

    def bad(self):
        self.cur_proxy['good'] -= 1;

    def fetch_one_proxy_from_cloud2(self):
        """
            提取一个代理
        """
        if(self.switches >= self.max_proxies):
            logger.info("PROXY SWITCH TO 202.183.32.182:80");
            return "202.183.32.182:80";

        fetch_url = self.api_url.format(self.orderid)
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))

        ips = content['data']['proxy_list']
        left = content['data']['order_left_count']
        # if(left >= self.reserved_proxy_count):
        self.cur_url = ips[0];
        self.switches = self.switches + 1;
        logger.info("PROXY SWITCH TO"+self.cur_url);
        return self.cur_url;
