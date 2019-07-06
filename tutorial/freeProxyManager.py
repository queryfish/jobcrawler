# -*- coding: utf-8 -*-
import logging
import requests
import json
import random

logger = logging.getLogger(__name__)

class FreeProxyManager(object):
    api_url = "https://proxyapi.mimvp.com/api/fetchopen.php?orderid=869080659322570605&num=20&country_group=1&http_type=1,2&result_fields=1,2&result_format=json"
    max_proxies = 2;
    cloud_times = 0;
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
        self.renew_proxy_pool()
        # filepath = './iptable.txt'
        # proxies = []
        # with open(filepath) as fp:
        #     line = fp.readline()
        #     cnt = 1
        #     while line:
        #         print("Line {}: {}".format(cnt, line.strip()))
        #         proxies.append(line.strip())
        #         line = fp.readline()
        #         cnt += 1
        # for prx in proxies:
        #     self.proxy_pool.append({"proxy":prx, "good":0});
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

    def renew_proxy_pool(self):
        self.cloud_times += 1;
        if(self.cloud_times > 2):
            self.proxy_pool = ['202.183.32.185:80']
            return self.proxy_pool

        fetch_url = self.api_url
        r = requests.get(fetch_url)
        if r.status_code != 200:
            logger.error("fail to fetch proxy")
            return False
        content = json.loads(r.content.decode('utf-8'))
        logger.info(content);
        ips = content['result']
        num = content['result_count']
        if(num > 0 ):
            self.proxy_pool = []
            for ip_port in ips:
                prx = ip_port['ip:port']
                self.proxy_pool.append({"proxy":prx, "good":0});
        # if(left >= self.reserved_proxy_count):
        logger.info(self.proxy_pool)
        return self.proxy_pool
