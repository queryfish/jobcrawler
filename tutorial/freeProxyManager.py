# -*- coding: utf-8 -*-
import logging
import requests
import json
import random

logger = logging.getLogger(__name__)

class FreeProxyManager(object):
    max_proxies = 2;
    switches = 0;
    proxy_pool = [];
    cur_proxy = {"proxy":"202.183.32.182:80", "good":0, "bad":0};
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
        filepath = './iptable.txt'
        proxies = []
        with open(filepath) as fp:
            line = fp.readline()
            cnt = 1
            while line:
                print("Line {}: {}".format(cnt, line.strip()))
                proxies.append(line.strip())
                line = fp.readline()
                cnt += 1
        for prx in proxies:
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
        self.cur_proxy = random.choice(self.proxy_pool)
        return self.cur_proxy['proxy'];

    def switch_proxy2(self):
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
        return
        # for p in self.proxy_pool:
        #     logger.info(p)

    def proxy(self):
        return self.cur_proxy['proxy'];

    def good(self):
        self.cur_proxy['good'] += 1;

    def bad(self):
        self.cur_proxy['good'] -= 1;
