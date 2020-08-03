# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

class ArticlespiderPipeline():
    def process_item(self, item, spider):
        return item

# 自定义导出
class JsonWithEncodingPipeline():
    # 自定义json文件导出
    def __init__(self):
        self.file = codecs.open('article.json', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False)+'\n'
        self.file.write(lines)
        return item

    def spider_closed(self,spider):
        self.file.close()


# 使用scrapy自带的JsonItemExporter
class JsonExporterPipeline():
    def __init__(self):
        self.file = open('ArticleExport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self,spider):
        self.exporter.finish_exporting()
        self.file.close()


# 存储到数据库
class MysqlPipeline():
    def __init__(self):
        self.conn = MySQLdb.connect('cdb-qa8qz1t6.bj.tencentcdb.com',port=10169,user='root',passwd='wopashei11',db='article_spider',charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
            insert into cnblog_article(title,url,url_object_id,front_image_url,front_image_path,parise_nums,comment_nums,fav_nums,tags,content,create_date)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on DUPLICATE KEY UPDATE parise_nums=VALUES(parise_nums)
        '''
        params = list()
        params.append(item.get('title', ''))
        params.append(item.get('url', ''))
        params.append(item.get('url_object_id', ''))
        front_image_url = ''.join(item.get('front_image_url', []))
        params.append(front_image_url)
        params.append(item.get('front_image_path', ''))
        params.append(item.get('parise_nums', 0))
        params.append(item.get('comment_nums', 0))
        params.append(item.get('fav_nums', 0))
        params.append(item.get('tags', ''))
        params.append(item.get('content', ''))
        params.append(item.get('create_date', '1970-07-01'))
        self.cursor.execute(insert_sql, tuple(params))
        self.conn.commit()
        return item


# 使用异步方式存储到数据库
class MysqlTwistedPipeline():
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        from MySQLdb.cursors import DictCursor
        dpparms = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            db=settings['MYSQL_DBNAME'],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dpparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def do_insert(self, cursor, item):
        insert_sql = '''
                    insert into cnblog_article(title,url,url_object_id,front_image_url,front_image_path,parise_nums,comment_nums,fav_nums,tags,content,create_date)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on DUPLICATE KEY UPDATE parise_nums=VALUES(parise_nums)
                '''
        params = list()
        params.append(item.get('title', ''))
        params.append(item.get('url', ''))
        params.append(item.get('url_object_id', ''))
        front_image_url = ''.join(item.get('front_image_url', []))
        params.append(front_image_url)
        params.append(item.get('front_image_path', ''))
        params.append(item.get('parise_nums', 0))
        params.append(item.get('comment_nums', 0))
        params.append(item.get('fav_nums', 0))
        params.append(item.get('tags', ''))
        params.append(item.get('content', ''))
        params.append(item.get('create_date', '1970-07-01'))
        cursor.execute(insert_sql, tuple(params))


    def handle_error(self, failure, item, spider):
        print(failure)


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = 'no_image_file_path'
            for ok,value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item