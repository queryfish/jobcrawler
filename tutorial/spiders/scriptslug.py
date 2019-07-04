#!/usr/bin/python
#coding:utf-8

import scrapy
from tutorial.items import TutorialItem
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
import  json
import  time
import  random
import redis
from scrapy.conf import settings

#zhipin 爬虫
class ScriptSlug(scrapy.Spider):

    name = "scriptslug"
    allowed_domains = ["scriptslug.com"]

    current_page = 1 #开始页码
    max_page = 15 #最大页码
    start_urls = [
        "https://scriptslug.com/scripts?pg=1",
    ]
    custom_settings = {
        # "ITEM_PIPELINES":{
        #     'tutorial.pipelines.ScriptSlugPipeline': 300,
        # },
        # "DOWNLOADER_MIDDLEWARES":{
        #     'tutorial.middlewares.ScriptSlugMiddleware': 299,
        #  #   'tutorial.middlewares.ProxyMiddleware':301
        # },
        "DEFAULT_REQUEST_HEADERS":{
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent':'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Mobile Safari/537.36',
            'Referer':'https://scriptslug.com/',
            'X-Requested-With':"XMLHttpRequest",
            "cookie":"lastCity=101020100; JSESSIONID=""; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1532401467,1532435274,1532511047,1532534098; __c=1532534098; __g=-; __l=l=%2Fwww.zhipin.com%2F&r=; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fc101020100-p100103%2F; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1532581213; __a=4090516.1532500938.1532516360.1532534098.11.3.7.11"
        }
    }
    def parse(self, response):
        # js = json.loads(response.body)
        # html = js['html']
        items = response.xpath('//article/a/@href')
        print(items)
        host = 'https://scriptslug.com'
        x = 1
        y = 1
        for item in items:
            detail_url = item.extract()
            print('extracting href from alink')
            print(item.extract())
            # print(item.extract_first())

            # position_name = item.css('h4::text').extract_first() #职位名称
            # salary = item.css('.salary::text').extract_first() or  '' #薪资
            # work_year = item.css('.msg em:nth-child(2)::text').extract_first() or '不限' #工作年限
            # educational = item.css('.msg em:nth-child(3)::text').extract_first() #教育程度
            # meta = {
            #     "position_name":position_name,
            #     "salary":salary,
            #     "work_year":work_year,
            #     "educational":educational
            # }
            #
            # # time.sleep(int(random.uniform(50, 70)))
            # #初始化redis
            # pool= redis.ConnectionPool(host='localhost',port=6379,decode_responses=True)
            # r=redis.Redis(connection_pool=pool)
            # key = settings.get('REDIS_POSITION_KEY')
            # position_id = url.split("/")[-1].split('.')[0]
            # print('further url:', detail_url)
            # print('key:', key, "value:", position_id);
            # print('parsing item: ...\n')
            # print(meta)
            yield Request(detail_url,callback=self.parse_item)

            # if (r.sadd(key,position_id)) == 1:
            #     yield Request(url,callback=self.parse_item,meta=meta)

        if self.current_page < self.max_page:
            self.current_page += 1
            api_url = "https://scriptslug.com/scripts"+"?pg="+str(self.current_page)
            time.sleep(int(random.uniform(1, 5)))
            yield  Request(api_url,callback=self.parse)
        pass

    def parse_item(self,response):
        target = response.css('.script-single__download').xpath('./@href').extract_first()
        print('target pdf...')
        print(target)
        # item = TutorialItem()
        # q = response.css
        # # item['address'] = q('.location-address::text').extract_first()
        # # item['create_time'] = q('.job-tags .time::text').extract_first()
        # # item['body'] = q('.text').xpath('string(.)').extract_first()
        # # # item['body'] = item['body'].encode('utf-8')
        # # # print(item['body'])
        # # item['company_name']  = q('.business-info h4::text').extract_first()
        # # item['postion_id'] = response.url.split("/")[-1].split('.')[0]
        # # item = dict(item, **response.meta )
        # pdf_url = q('.script-single__download').extract_first()
        # print("parsing PDF...:")
        # print(item)
        # yield  item
        yield Request(
            url=target,
            callback=self.save_pdf
        )

    def save_pdf(self, response):
        path = response.url.split('/')[-1]
        self.logger.info('Saving PDF %s', path)
        with open(path, 'wb') as f:
            f.write(response.body)
