#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: linghanchujian

import re
import scrapy
from scrapy.http import response
from scrapy.http import Request
from xiuren_cosplay.items import XiurenCosplayItem
from xiuren_cosplay.spiders.public_fun import public_function  
# from xiuren_cosplay import settings

# http://www.27270.com 这是爬取的主域
# http://www.27270.com/game/cosplaymeitu/ 这是爬取的网址


class cosplaySpiders(scrapy.Spider):
    name = "cosplay"
    start_urls = ["http://www.27270.com/game/cosplaymeitu/"]

    def parse(self,response):
        # 获取图片url
        imgUrl = response.xpath("//ul[@class='pic_list']/li/a/@href").extract_first("")
        if imgUrl:
            yield Request(url=response.urljoin(imgUrl),callback=self.cosplayAnalysis)
            pass

        # 获取当前网站cosplay下一页url
        index_next_url = response.xpath("//div[@class='NewPages']/ul/li[last()-1]/a/@href").extract_first("")
        if index_next_url:
            yield Request(url=response.urljoin(index_next_url),callback=self.parse)

    # 解析函数
    def cosplayAnalysis(self,response):
        # 实例化对象items
        items = XiurenCosplayItem()
        # 实例化公共函数
        public_md5 = public_function()

        #解析子网站
        Name = response.xpath("//h1[@class='articleV4Tit']/text()").extract_first("").replace("(","").replace(")","")
        imgName = re.match(".*[^\d*]",Name).group()
        imgUrl = response.xpath("//p[@align='center']/a/img/@src").extract_first("")
        index_next_url = response.xpath("//ul[contains(@class,'articleV4Page')]/li[last()-1]/a/@href").extract_first("") 
        if index_next_url:
            yield Request(url=response.urljoin(index_next_url),callback=self.cosplayAnalysis)
        items["imgName_id"] = public_md5.get_md5(imgName)
        items["imgUrls"] = imgUrl
        items["imgName"] = imgName
        yield items