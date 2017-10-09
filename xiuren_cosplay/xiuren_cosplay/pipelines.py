# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# import requests
import re,os,json,MySQLdb
from scrapy.http import Request
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi 




class XiurenCosplayPipeline(object):
    def process_item(self, item, spider):
        return item


#写入json文件
class CosplayPipelineJsonItemExporter(object):
    def __init__(self):
        filePath = os.path.join(os.path.abspath(os.path.dirname(__file__)),'cosplay.json')
        self.filename = open(filePath,'wb')
    
    def process_item(self, item, spider):
         jsontext=json.dumps(dict(item),ensure_ascii=False) + ",\n"
         self.filename.write(jsontext.encode("utf-8"))
         return item

    def close_spider(self,spider):
        self.filename.close()

# 同步数据库写入 数据量小处理方式
class MysqlPipline(object):
    def __init__(self,parameter):
        # print(parameter['host'],parameter['user'])
        self.conn = MySQLdb.connect(parameter['host'],parameter['user'],parameter['password'],parameter['db'],charset='utf8',use_unicode = True)
        self.cursor = self.conn.cursor()

    @classmethod
    def from_crawler(cls,crawler):
        parameter = dict(
            host = crawler.settings["MYSQL_HOST"],
            user = crawler.settings["MYSQL_USER"],
            password = crawler.settings["MYSQL_PASSWD"],
            db = crawler.settings["MYSQL_DBNAME"],
        )
        # print(parameter)        
        return cls(parameter)

    def process_item(self, item, spider):
        SQL_Sentence = """
            INSERT INTO cosplay_sur (imgName_id,imgName,imgUrls,imgPath) VALUES (%s,%s,%s,%s)
        """
        self.cursor.execute(SQL_Sentence,(item["imgName_id"],item["imgName"],item["imgUrls"],item["imgPath"]))
        self.conn.commit()

# 异步数据库写入 数据量大处理方式
class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool
        pass

    @classmethod
    def from_crawler(cls,crawler):
        dbparm = dict(
            host = crawler.settings["MYSQL_HOST"],
            user = crawler.settings["MYSQL_USER"],
            password = crawler.settings["MYSQL_PASSWD"],
            db = crawler.settings["MYSQL_DBNAME"],
            charset = 'utf8',
            # cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )

        dbpool = adbapi.ConnectionPool('MySQLdb',**dbparm)
        return cls(dbpool)
    
    def process_item(self,item,spider):
        query = self.dbpool.runInteraction(self.do_inster,item)#插入数据库
        # print("----------------------{}--------------".format(query))
        query.addErrback(self.hamdle_err)#处理异步插入异常

    def do_inster(self,cursor,item):
        # print("------------------------{}".format(cursor))
        #执行插入
        SQL_Sentence = """
            INSERT INTO cosplay_sur (imgName_id,imgName,imgUrls,imgPath) VALUES (%s,%s,%s,%s)
        """
        cursor.execute(SQL_Sentence,(item["imgName_id"],item["imgName"],item["imgUrls"],item["imgPath"]))

    def hamdle_err(self,failure):
        print(failure)
    
#下载图片 
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
        item['imgPath'] = image_paths
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