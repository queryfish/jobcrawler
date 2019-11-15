# -*- coding: utf-8 -*-

import base64
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from .freeRotateProxyManager import freeRotateProxyManager

# proxy = fetch_one_proxy() # 获取一个代理

THRESHOLD = 5  # 换ip阈值
fail_time = 0  # 此ip异常次数
retry_time = 0  # 此ip异常次数

logger = logging.getLogger(__name__)

class fixedProxyMiddleware(object):
        exception_count = 0;
        proxyManager = freeRotateProxyManager();

        def process_request(self, request, spider):
            url = request.url
            # if url.startswith('https://book.douban.com/tag/'):
                # return
            proxy  = self.proxyManager.proxy()
            request.meta['proxy'] = proxy  # 设置代理
            logger.info("REQ {} <- [{}]".format(request.url, request.meta['proxy']))

        def process_response(self, request, response, spider):
            proxy = request.meta.get('proxy', '')
            if not(200 <= response.status < 300):
                url = request.url
                errcode = response.status
                logger.warn("BAD STATUS {} @ {}".format(errcode, url))
                self.proxyManager.badProxy(proxy)
            elif(response.status == 200):
                TITLE_SEL = '#wrapper > h1 > span';
                bookTitle = response.css(TITLE_SEL).css('::text').extract_first();
                banner = '<script>var d=[navigator.platform,navigator.userAgent,navigator.vendor].join'
                if bookTitle is None and response.body.startswith(banner):
                    logger.error("STR.");
                    logger.error(request.url);
                    logger.error(response.body);
                #     #actually should be banned proxy
                    self.proxyManager.badProxy(proxy)
                else:
                    logger.info('GOOD for [{}]'.format(request.url))
                    self.proxyManager.goodProxy(proxy)

            return response

        def process_exception(self, request, exception, spider):
            proxy = request.meta.get('proxy', '')
            self.proxyManager.badProxy(proxy)
            logger.warn('EXP [{}] @ [{}]'.format(exception, request.url));
            return request

# class freeRotateProxyMiddleware(object):
#         proxyManager = freeRotateProxyManager();
#         def process_request(self, request, spider):
#             proxy  = self.proxyManager.nextProxy()
#             # username = 'marrowsky'
#             # password = 'fuckingkuaidaili'
#             # # proxy = proxyManager.proxy()
#             # proxy_url = 'http://%s:%s@%s' % (username, password, proxy)
#             request.meta['proxy'] = proxy  # 设置代理
#             logger.info("using proxy: {}".format(request.meta['proxy']))
#             # 设置代理身份认证
#             # Python3 写法
#             # auth = "Basic %s" % (base64.b64encode(('%s:%s' % (username, password)).encode('utf-8'))).decode('utf-8')
#             # Python2 写法
#             # auth = "Basic " + base64.b64encode('%s:%s' % (username, password))
#             # request.headers['Proxy-Authorization'] = auth
#
#         def process_response(self, request, response, spider):
#             if not(200 <= response.status < 300):
#                 url = request.url
#                 errcode = response.status
#                 logger.warn("BAD STATUS {} @ {}".format(errcode, url))
#                 req_proxy = request.meta.get('proxy', '')
#                 if response.status == 404 or response.status == 403:
#                     self.proxyManager.banProxy(req_proxy)
#                 else:
#                     self.proxyManager.invalidProxy(req_proxy)
#             return response
#
#         def process_exception(self, request, exception, spider):
#             req_proxy = request.meta.get('proxy', '')
#             logger.warn("Get exception with proxy: {}".format(req_proxy))
#             logger.warn(exception)
#             # qsize = spider.crawler.engine.slot.scheduler.__len__();
#             # running = len(spider.crawler.engine.slot.inprogress);
#             # logger.info('PENDING_QUEUE_SIZE: {}, RUNNING QUEUE SIZE: {}'.format(qsize, running));
#             self.proxyManager.invalidProxy(req_proxy)
#             return request



class AgentMiddleware(UserAgentMiddleware):
        """
            User-Agent中间件, 设置User-Agent
        """
        def __init__(self, user_agent=''):
            self.user_agent = user_agent

        def process_request(self, request, spider):
            ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'
            request.headers.setdefault('User-Agent', ua)
