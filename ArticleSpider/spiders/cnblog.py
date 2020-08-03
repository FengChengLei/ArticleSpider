import scrapy
from scrapy import Selector
from scrapy import Request
from ArticleSpider.items import CnBlogArticleItem
from ArticleSpider.utils import common
from scrapy.loader import ItemLoader
from ArticleSpider.items import ArticleItemLoader

import requests
import re
import json
from urllib import parse

class CnblogSpider(scrapy.Spider):
    name = 'cnblog'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        '''
        1. 获取新闻列表页中新闻url并交给scrapy进行下载后调用相应的解析方法
        2. 获取下一页的url并交给scrapy进行下载，喜爱在完成后交给parse继续跟进
        :param response:
        :return:
        '''
        # extract_first("no_data")如果列中没有值，则返回no_data
        # url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()

        # 如果只有html文本信息，可以使用Selector类
        # sel = Selector(text=response.text)
        # url = sel.css('div#new_list h2 a::attr(href)').extract()

        # url = response.css('div#new_list h2 a::attr(href)').extract()

        post_nodes = response.css('#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first('')
            if image_url.startswith('//'):
                image_url = 'https:'+image_url
            post_url = post_node.css('h2 a::attr(href)').extract_first('no_post_url')

            # 方式一：
            # if post_url.startswith('http'):
            #     yield Request(url='{}{}'.format('http://news.cnblogs.com/',post_url))

            # 方式二：
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url': image_url}, callback=self.parse_detail)

        # 提取下一页并交给scarpy进行下载

        # 方式一
        # next_url = response.css('div.pager a:last-child::text').extract_first('no_next_url')
        # if next_url == 'Next >':
        #     next_url = response.css('div.paper a:last-child::text').extract_first('no_next_url')
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

        # 方式二
        # next_url = response.xpath("//a[contains(text(),'Next >')]/@href").extract_first('no_next_url')
        # yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def parse_detail(self,response):
        '''
        对当前页面进行爬取
        :param response:
        :return:
        '''
        match_re = re.match('.*?(\d+)',response.url)
        if match_re:
            # xpath解析方式
            # title = response.xpath('//*[@id="news_title"]//a/text()').extract_first('no_title')
            # create_date = response.xpath('//*[@id="news_info"]//*[@class="time"]/text()').extract_first('no_title')
            # content = response.xpath('//*[@id="news_content"]').extract()[0]
            # tag_list = response.xpath('//*[@class="news_tags"]//a/text()').extract()[0]

            post_id = match_re.group(1)

            # css解析方法
            # title = response.css('#news_title a::text').extract_first('no_title')
            # create_date = response.css('#news_info .time::text').extract_first('no_create_date')
            # match_re = re.match('.*?(\d+.*)',create_date)
            # if match_re:
            #     create_date = match_re.group(1)
            # content = response.css('#news_content').extract()[0]
            # tag_list = response.css('.news_tags a::text').extract()
            # tags = ','.join(tag_list)
            #
            # # 由于评论数可能是js异步加载，所以获取值为空
            # # comments = response.css('#news_info span.comments a::text').extract()
            #
            #
            #
            # # 同步代码
            # # html = requests.get(parse.urljoin(response.url,'/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)))
            # # j_data = json.loads(html.text)
            # # praise_nums = j_data['DiggCount']
            # # fav_nums = j_data['TotalView']
            # # comment_nums = j_data['CommentCount']
            #
            # article_item = CnBlogArticleItem()
            # article_item['title'] = title
            # article_item['create_date'] = create_date
            # article_item['content'] = content
            # article_item['tags'] = tags
            # article_item['url'] = response.url
            # # 对于图片需要使用list
            # if response.meta.get('front_image_url',''):
            #     article_item['front_image_url'] = [response.meta.get('front_image_url','')]
            # else:
            #     article_item['front_image_url'] = []

            # 使用itemloader提取信息

            # 使用自带的ItemLoader
            # item_loader = ItemLoader(item=CnBlogArticleItem(), response=response)

            # 使用自定义的ArticleItemLoader
            item_loader = ArticleItemLoader(item=CnBlogArticleItem(), response=response)

            item_loader.add_css('title', '#news_title a::text')
            item_loader.add_css('content', '#news_content')
            item_loader.add_css('tags', '.news_tags a::text')
            item_loader.add_css('create_date', '#news_info .time::text')
            item_loader.add_value('url',response.url)
            if response.meta.get('front_image_url', ''):
                item_loader.add_value('front_image_url', response.meta.get('front_image_url', ''))

            # load_item函数会自动将item_loader中的值添加到article_item中
            # article_item = item_loader.load_item()

            # 改为异步代码
            # yield Request(url=parse.urljoin(response.url,'/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)), meta={'article_item':article_item}, callback=self.parse_nums)

            # 使用item_loader
            yield Request(url=parse.urljoin(response.url,'/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)), meta={'item_loader':item_loader,'url':response.url}, callback=self.parse_nums)

    def parse_nums(self, response):
        j_data = json.loads(response.text)
        # article_item = response.meta.get('article_item', 'no_article_item')
        # praise_nums = j_data['DiggCount']
        # fav_nums = j_data['TotalView']
        # comment_nums = j_data['CommentCount']
        # article_item['praise_nums'] = praise_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['url_object_id'] = common.get_md5(article_item['url'])

        # 使用item_loader
        item_loader = response.meta.get('item_loader', 'no_item_loader')
        item_loader.add_value('praise_nums', j_data['DiggCount'])
        item_loader.add_value('fav_nums', j_data['TotalView'])
        item_loader.add_value('comment_nums', j_data['CommentCount'])
        item_loader.add_value('url_object_id', common.get_md5(response.meta.get('url', '')))
        article_item = item_loader.load_item()

        yield article_item