# -*- coding: utf-8 -*-

import base64
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
# from .paidProxyManager import PaidProxyManager
from .rotateProxyManager import RotateProxyManager

# proxy = fetch_one_proxy() # 获取一个代理

THRESHOLD = 5  # 换ip阈值
fail_time = 0  # 此ip异常次数
retry_time = 0  # 此ip异常次数

logger = logging.getLogger(__name__)

proxyManager = RotateProxyManager();
# proxyManager = RotateProxyManager();

class CustomRetryMiddleware(RetryMiddleware):
        def _retry(self, request, reason, spider):
            global proxyManager
            proxy  = proxyManager.nextProxy()
            retryreq = request.copy()
            username = 'marrowsky'
            password = '0krbqw3g'
            # proxy = proxyManager.proxy()
            proxy_url = 'http://%s:%s@%s' % (username, password, proxy)
            retryreq.meta['proxy'] = proxy_url  # 设置代理
            logger.info("using proxy: {}".format(retryreq.meta['proxy']))
            # 设置代理身份认证
            # Python3 写法
            auth = "Basic %s" % (base64.b64encode(('%s:%s' % (username, password)).encode('utf-8'))).decode('utf-8')
            # Python2 写法
            # auth = "Basic " + base64.b64encode('%s:%s' % (username, password))
            retryreq.headers['Proxy-Authorization'] = auth
            return retryreq


    # 代理中间件
class RegularProxyMiddleware(object):

        def process_request(self, request, spider):
            global proxyManager
            proxy  = proxyManager.nextProxy()

            username = 'marrowsky'
            password = '0krbqw3g'
            # proxy = proxyManager.proxy()
            proxy_url = 'http://%s:%s@%s' % (username, password, proxy)
            request.meta['proxy'] = proxy_url  # 设置代理
            logger.info("using proxy: {}".format(request.meta['proxy']))
            # 设置代理身份认证
            # Python3 写法
            auth = "Basic %s" % (base64.b64encode(('%s:%s' % (username, password)).encode('utf-8'))).decode('utf-8')
            # Python2 写法
            # auth = "Basic " + base64.b64encode('%s:%s' % (username, password))
            request.headers['Proxy-Authorization'] = auth

        # def process_response(self, request, response, spider):
        #     """
        #         如果状态码异常，则增加ip异常次数
        #         当异常次数达到阈值, 则更换ip,
        #         此换ip策略比较简略, 仅供参考
        #     """
        #     global fail_time, proxy, THRESHOLD, proxyManager
        #     if not(200 <= response.status < 300):
        #         fail_time += 1
        #         proxyManager.bad()
        #         logger.warn("Request failed {}".format(fail_time));
        #         if fail_time >= proxyManager.threshold():
        #             # proxy = fetch_one_proxy()
        #             # if(THRESHOLD < 5):
        #             #     THRESHOLD += 1;
        #             # proxy = proxyManager.switch_proxy()
        #             # proxy = proxyManager.fetch_one_proxy_from_cloud();
        #             fail_time = 0
        #     else:
        #         proxyManager.good()
        #     return response

        def process_exception(self, request, exception, spider):
            global proxyManager
            req_proxy = request.meta.get('proxy', '')
            logger.warn("Get exception with proxy: {}".format(req_proxy))
            logger.warn(exception)
            proxyManager.invalidProxy(req_proxy)
            return request


class AgentMiddleware(UserAgentMiddleware):
        """
            User-Agent中间件, 设置User-Agent
        """
        def __init__(self, user_agent=''):
            self.user_agent = user_agent

        def process_request(self, request, spider):
            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'
            request.headers.setdefault('User-Agent', ua)
