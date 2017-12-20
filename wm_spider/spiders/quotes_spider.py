#!/usr/bin/python
# -*- coding:utf-8 -*- 

import scrapy
#爬虫的demo，为了熟悉爬虫做演示
class QuotesSpider(scrapy.Spider):
    #指定爬虫的名称，用于执行
    name = "quotes"
    #入口函数
    def start_requests(self):
        #指定待抓取的连接池，可以从调度器中获取
        urls = [ 
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]   
        for url in urls:
            #执行抓取，指定url和回调函数parse
            yield scrapy.Request(url=url, callback=self.parse)
    #抓取结果处理
    def parse(self, response):
         for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
