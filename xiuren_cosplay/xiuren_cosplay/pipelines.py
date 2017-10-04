# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# import requests
import re,os
from scrapy.http import Request
from scrapy.contrib.pipeline.images import ImagesPipeline
# from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

class XiurenCosplayPipeline(object):
    def process_item(self, item, spider):
        return item

class CosplayPipeline(ImagesPipeline):
    
    def get_media_requests(self, item, info):
        # print("{}-------------".format(item))
        imgUrl = item["imgUrls"]
        yield Request(imgUrl,meta={"item":item})
    
    def item_completed(self, results, item, info):
        # print("{}-------------{}".format(results,self.IMAGES_URLS_FIELD))        
        image_paths = [x['path'] for ok, x in results if ok]
        # print("{}-------------".format(image_paths))                
        if not image_paths:
            print('{}/{}------文件保存失败'.format(item['imgName'], item['imgUrls']))
            raise DropItem("Item contains no images")
        else:
            print('{}/{}------文件保存成功'.format(item['imgName'], item['imgUrls']))
        # item['image_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        """
        :param request: 每一个图片下载管道请求
        :param response:
        :param info:
        :param path :清洗Windows系统的文件夹非法字符，避免无法创建目录
        :return: 每套图的分类目录
        """
        item = request.meta['item']
        imgName = item["imgName"]
        imgUrl = item["imgUrls"]
        print(imgName,imgUrl)
        path = re.sub(r'[？\\*|“<>:/]', '', str(imgName))
        base_name = os.path.basename(imgUrl)
        filename = u'{0}/{1}'.format(imgName, base_name)
        return filename