# -*- coding: utf-8 -*-
import logging
import requests
import json

orderid = '956231220141933'  # 订单号
# 提取代理链接，以私密代理为例
api_url = "https://dps.kdlapi.com/api/getdps/?orderid={}&num=1&pt=1&format=json&sep=1"
logger = logging.getLogger(__name__)
cur_proxy = "202.183.32.182:80";
reserved_proxy_count = 900;
max_proxies = 2;
switches = 0;

def fetch_one_proxy2():
        return "202.183.32.182:80";

def fetch_one_proxy():
        """
            提取一个代理
        """
        global switches, max_proxies
        if(switches >= max_proxies):
            logger.info("PROXY SWITCH TO 202.183.32.182:80");
            return "202.183.32.182:80";

        fetch_url = api_url.format(orderid)
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))

        ips = content['data']['proxy_list']
        left = content['data']['order_left_count']
        if(left >= reserved_proxy_count):
            cur_proxy = ips[0];
            switches = switches + 1;
        logger.info("PROXY SWITCH TO"+cur_proxy);
        return cur_proxy;
