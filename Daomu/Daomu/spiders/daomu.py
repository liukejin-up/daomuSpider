import scrapy
from ..items import DaomuItem
import os
class DaomuSpider(scrapy.Spider):
    name = 'daomu'
    allowed_domains = ['www.daomubiji.com']
    start_urls = ['http://www.daomubiji.com/']

    def parse(self, response):
        """一级页面解析函数,提取：大标题、大链接"""
        a_list = response.xpath('//li[contains(@id, "menu-item-")]/a')

        for a in a_list:
            item = DaomuItem()

            # get获取字符串格式，序列化提取第一个
            item['parent_title'] = a.xpath('./text()').get()
            parent_href = a.xpath('./@href').get()

            # 创建对应的目录结构
            directory = './novel/{}/'.format(item['parent_title'])
            if not os.path.exists(directory):
                os.makedirs(directory)

            # 将parent_href继续交给调度器入队列
            yield scrapy.Request(url=parent_href, meta={'item': item}, callback=self.parse_second_page)

    def parse_second_page(self, response):
        """二级页面解析函数,提取：小标题、小链接"""
        meta1 = response.meta['item']
        a_list = response.xpath('//article/a')

        for a in a_list:

            # 创建全新的item对象,避免在给对象赋值时一直被覆盖
            item = DaomuItem()
            item['son_title'] = a.xpath('./text()').get()
            item['parent_title'] = meta1['parent_title']
            son_href = a.xpath('./@href').get()

            # 将son_href继续交给调度器入队列
            yield scrapy.Request(url=son_href, meta={'item': item}, callback=self.parse_third_page)

    def parse_third_page(self, response):
        """三级页面解析函数：提取具体小说内容"""
        item = response.meta['item']
        # extract是序列化提取所有选择器中的内容
        p_list = response.xpath('//article/p/text()').extract()
        item['novel_content'] = '\n'.join(p_list)

        # 至此,一本完整的小说数据抓取完成,交给管道文件处理
        yield item

















