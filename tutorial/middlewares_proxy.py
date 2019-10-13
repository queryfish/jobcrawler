# -*- coding: utf-8 -*-

import base64
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from .freeProxyManager import FreeProxyManager
from .paidProxyManager import PaidProxyManager

# proxy = fetch_one_proxy() # 获取一个代理

THRESHOLD = 5  # 换ip阈值
fail_time = 0  # 此ip异常次数
retry_time = 0  # 此ip异常次数

logger = logging.getLogger(__name__)
# proxyManager = FreeProxyManager();
proxyManager = PaidProxyManager();

# tunnel proxys
# 隧道服务器
tunnel_host = "tps136.kdlapi.com"
tunnel_port = "15818"

# 隧道id和密码
tid = "t17092713770940"
password = "4rmms5f5"

class CustomRetryMiddleware(RetryMiddleware):

    def _retry(self, request, reason, spider):
        global retry_time, proxy, THRESHOLD, proxyManager
        logger.info("retrying on request {} with proxy {}".format(request.url, request.meta['proxy']))
        retries = request.meta.get('retry_times', 0) + 1
        req_proxy = request.meta.get('proxy', '')
        logger.info(req_proxy)
        logger.info(proxyManager.proxy())
        if(req_proxy == "https://"+proxyManager.proxy()):
            retry_time += 1;
            proxyManager.bad()
        # request.meta['retry_times'] = retries
        # logger.info("trying {} times".format(retries))

        logger.info("Retring {} times, due to {}".format(retry_time, reason))
        if retry_time % 1 == 0 :
            proxy = proxyManager.switch_proxy()
            retryreq = request.copy()
            retryreq.meta['proxy'] = "https://"+proxy  # 设置代理
            return retryreq
        else:
            retryreq = request.copy()
            retryreq.dont_filter = True
            return retryreq

        if retry_time <= 5 : #proxyManager.threshold():
        # if retry_time <= 5:
            logger.info("Retring {} times, due to {}".format(retry_time, reason))
            # logger.info(format="Retrying %(request)s (failed %(retries)d times): %(reason)s",
                    # level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason)
            retryreq = request.copy()
            retryreq.dont_filter = True
            # retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            retry_time = 0;
            # if(THRESHOLD < 5):
            #     THRESHOLD += 1;
            proxy = proxyManager.switch_proxy()
            # proxy = proxyManager.fetch_one_proxy_from_cloud();
            logger.info("Gave up retring ...SWITCH PROXY to {}".format(proxy))
            retryreq = request.copy()
            retryreq.meta['proxy'] = "https://"+proxy  # 设置代理
            return retryreq



    # 代理中间件
class ProxyMiddleware(object):

        def process_request(self, request, spider):
            # global proxyManager
            # # proxy_url = 'http://%s:%s@%s' % (username, password, proxy)
            # # print(proxyManager.proxy())
            # # logger.info("processing request retry times, max {}".format(request.meta['max_retry_times']))
            # request.meta['proxy'] = "https://"+proxyManager.proxy()  # 设置代理
            # logger.info("using proxy: {}".format(request.meta['proxy']))
            # # 设置代理身份认证
            # # Python3 写法
            # # auth = "Basic %s" % (base64.b64encode(('%s:%s' % (username, password)).encode('utf-8'))).decode('utf-8')
            # # Python2 写法
            # # auth = "Basic " + base64.b64encode('%s:%s' % (username, password))
            # # request.headers['Proxy-Authorization'] = auth

            proxy_url = 'http://%s:%s@%s:%s' % (tid, password, tunnel_host, tunnel_port)
            request.meta['proxy'] = proxy_url  # 设置代理
            logger.debug("using proxy: {}".format(request.meta['proxy']))
            # 设置代理身份认证
            # Python3 写法
            auth = "Basic %s" % (base64.b64encode(('%s:%s' % (tid, password)).encode('utf-8'))).decode('utf-8')
            # Python2 写法
            # auth = "Basic " + base64.b64encode('%s:%s' % (tid, password))
            request.headers['Proxy-Authorization'] = auth


        def process_response(self, request, response, spider):
            """
                如果状态码异常，则增加ip异常次数
                当异常次数达到阈值, 则更换ip,
                此换ip策略比较简略, 仅供参考
            """
            global fail_time, proxy, THRESHOLD, proxyManager
            if not(200 <= response.status < 300):
                fail_time += 1
                proxyManager.bad()
                logger.warn("Request failed {}".format(fail_time));
                if fail_time >= proxyManager.threshold():
                    # proxy = fetch_one_proxy()
                    # if(THRESHOLD < 5):
                    #     THRESHOLD += 1;
                    proxy = proxyManager.switch_proxy()
                    # proxy = proxyManager.fetch_one_proxy_from_cloud();
                    fail_time = 0
            else:
                proxyManager.good()
            return response

        def process_exception(self, request, exception, spider):
            global fail_time, proxy, THRESHOLD,proxyManager
            req_proxy = request.meta.get('proxy', '')
            logger.warn("Get exception with proxy: {}".format(req_proxy))
            logger.warn(exception)
            # if not(200 <= response.status < 300):
            # fail_time += 1
            proxyManager.bad()
            # logger.warn("Request failed {}".format(fail_time));
            # if fail_time >= 1:
            proxy = proxyManager.switch_proxy()
            # fail_time = 0
            return request

class TunnelProxyMiddleware(object):

        def process_request(self, request, spider):
            proxy_url = 'http://%s:%s@%s:%s' % (tid, password, tunnel_host, tunnel_port)
            request.meta['proxy'] = proxy_url  # 设置代理
            logger.debug("using proxy: {}".format(request.meta['proxy']))
            # 设置代理身份认证
            # Python3 写法
            auth = "Basic %s" % (base64.b64encode(('%s:%s' % (tid, password)).encode('utf-8'))).decode('utf-8')
            # Python2 写法
            # auth = "Basic " + base64.b64encode('%s:%s' % (tid, password))
            request.headers['Proxy-Authorization'] = auth


class AgentMiddleware(UserAgentMiddleware):
        """
            User-Agent中间件, 设置User-Agent
        """
        def __init__(self, user_agent=''):
            self.user_agent = user_agent

        def process_request(self, request, spider):
            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'
            request.headers.setdefault('User-Agent', ua)
