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
    PROXIES = [
        # '193.112.128.212:8118',
        '202.183.32.182:80',
        '183.129.244.16:11161',
        '60.13.42.34:9999',
        '119.254.94.71:39053',
        '175.44.158.15:9000',
        '112.111.98.176:9000',
        '27.203.142.151:8060',
        '27.188.65.244:8060',
        '183.129.207.80:12608',
        '114.234.83.79:9000',
        '117.87.178.88:9000',
        '117.90.137.65:9999',
        '117.90.252.143:9000',
        '183.129.207.86:13974',
        '121.232.194.251:9000',
        # '1.85.220.195:8118',
        # '60.255.186.169:8888',
        # '118.187.58.34:53281',
        # '116.224.191.141:8118',
        # '120.27.5.62:9090',
        # '119.132.250.156:53281',
        # '139.129.166.68:3128'
    ]
    def __init__(self):
        for prx in self.PROXIES:
            self.proxy_pool.append({"proxy":prx, "good":0});
        self.cur_proxy = random.choice(self.proxy_pool)
        print(self.proxy_pool)


    def switch_proxy(self):
        # find the max goodness and the element except the current one ?
        n = len(self.proxy_pool)
        max = 0
        max_index = 0
        for i in range(1, n):
            p = self.proxy_pool[i];
            if p['good'] >= max:
                max_index = i
        self.cur_proxy = self.proxy_pool[max_index];
        return self.cur_proxy['proxy'];

    def proxy(self):
        return self.cur_proxy['proxy'];

    def good(self):
        self.cur_proxy['good'] += 1;

    def bad(self):
        self.cur_proxy['good'] -= 1;

    def fetch_one_proxy_from_cloud(self):
        """
            提取一个代理
        """
        if(self.switches >= self.max_proxies):
            logger.info("PROXY SWITCH TO 202.183.32.182:80");
            return "202.183.32.182:80";

        fetch_url = self.api_url.format(orderid)
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))

        ips = content['data']['proxy_list']
        left = content['data']['order_left_count']
        if(left >= self.reserved_proxy_count):
            self.cur_proxy = ips[0];
            self.switches = self.switches + 1;
        logger.info("PROXY SWITCH TO"+self.cur_proxy);
        return self.cur_proxy;
