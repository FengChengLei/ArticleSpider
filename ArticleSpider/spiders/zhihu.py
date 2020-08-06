import time
from mouse import move,click

import scrapy
from selenium import webdriver

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    def start_requests(self):
        '''
        1. 启动chrome(启动之前确保所有的chrome示例已经关闭),由于知乎会检测到webdrive
        /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
        :return:
        '''
        # 手动启动后webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')

        browser = webdriver.Chrome(executable_path='/Users/fengchenglei/OneDrive/项目/chromedriver', chrome_options=chrome_option)
        browser.get('https://www.zhihu.com/signin')

        # 输入用户名和密码
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys(Keys.COMMAND,'a')
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('545776081@qq.com')
        browser.find_element_by_css_selector('.SignFlow-passwordInput.Input-wrapper input').send_keys(Keys.COMMAND+'a')
        browser.find_element_by_css_selector('.SignFlow-passwordInput.Input-wrapper input').send_keys('Wopashei11')

        # 点击登录
        move(962, 631)
        click()
        # browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
        time.sleep(60)


