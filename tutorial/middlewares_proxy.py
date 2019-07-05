# -*- coding: utf-8 -*-

import base64
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from .utils import fetch_one_proxy

# 非开放代理且未添加白名单，需用户名密码认证
username = "yourusername"
password = "yourpassword"
proxy = fetch_one_proxy() # 获取一个代理

THRESHOLD = 10  # 换ip阈值
fail_time = 0  # 此ip异常次数

logger = logging.getLogger(__name__)

class CustomRetryMiddleware(RetryMiddleware):

    def _retry(self, request, reason, spider):
        global fail_time, proxy, THRESHOLD
        retries = request.meta.get('retry_times', 0) + 1
        if retries <= THRESHOLD:
            logger.info("Retring {} times, due to {}".format(retries, reason))
            # logger.info(format="Retrying %(request)s (failed %(retries)d times): %(reason)s",
                    # level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason)
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            # retryreq.dont_filter = True
            # retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:

            # do something with the request: inspect request.meta, look at request.url...

            # logger.info(format="Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
            #         level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason)
            proxy = fetch_one_proxy()
            logger.info("Gave up retring ...SWITCH PROXY to {}".format(proxy))
            retryreq = request.copy()
            retryreq.meta['proxy'] = "http://"+proxy  # 设置代理
            return retryreq


    # 代理中间件
class ProxyMiddleware(object):

        def process_request(self, request, spider):
            proxy_url = 'http://%s:%s@%s' % (username, password, proxy)
            request.meta['proxy'] = "http://"+proxy  # 设置代理
            logger.debug("using proxy: {}".format(request.meta['proxy']))
            # 设置代理身份认证
            # Python3 写法
            auth = "Basic %s" % (base64.b64encode(('%s:%s' % (username, password)).encode('utf-8'))).decode('utf-8')
            # Python2 写法
            # auth = "Basic " + base64.b64encode('%s:%s' % (username, password))
            # request.headers['Proxy-Authorization'] = auth


        def process_response(self, request, response, spider):
            """
                如果状态码异常，则增加ip异常次数
                当异常次数达到阈值, 则更换ip,
                此换ip策略比较简略, 仅供参考
            """
            global fail_time, proxy, THRESHOLD
            if not(200 <= response.status < 300):
                fail_time += 1
                logger.warn("Request failed {}".format(fail_time));
                if fail_time >= THRESHOLD:
                    proxy = fetch_one_proxy()
                    fail_time = 0
            return response

        def process_exception(self, request, exception, spider):
            global fail_time, proxy, THRESHOLD
            logger.warn(exception)
            # if not(200 <= response.status < 300):
            fail_time += 1
            logger.warn("Request failed {}".format(fail_time));
            if fail_time >= THRESHOLD:
                proxy = fetch_one_proxy()
                fail_time = 0
            return response


class AgentMiddleware(UserAgentMiddleware):
        """
            User-Agent中间件, 设置User-Agent
        """
        def __init__(self, user_agent=''):
            self.user_agent = user_agent

        def process_request(self, request, spider):
            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'
            request.headers.setdefault('User-Agent', ua)