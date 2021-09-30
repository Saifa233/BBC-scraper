import scrapy
import time
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from scrapy import Selector

class BbcNewsSpider(scrapy.Spider):
    name = 'bbc_news'
    allowed_domains = ['www.google.com']
    start_urls = ['https://www.google.com/']

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.63'

    ua = UserAgent()

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'BBC-Data.csv',
        'FEED_EXPORT_ENCODING':'utf-8'
    }
    

    def __init__(self):
        self.options = ChromeOptions()
        self.options.add_argument("--disable-blink-features")
        self.options.add_argument("start-maximized")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--incognito')
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--use-fake-ui-for-media-stream")
        self.options.add_argument(
            f'--user-agent={self.ua.chrome}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=self.options)
    
    def parse(self, response):
        self.driver.get('https://www.bbc.com/news/topics/c008ql15vpyt/pakistan/')
        time.sleep(5)
        resp = Selector(text=self.driver.page_source)
        for news in resp.xpath('//article[@class="qa-post gs-u-pb-alt+ lx-stream-post gs-u-pt-alt+ gs-u-align-left"]'):
            title = news.xpath('.//span[@class="lx-stream-post__header-text gs-u-align-middle"]/text()').get()
            description = news.xpath('.//p[@class="lx-stream-related-story--summary qa-story-summary"]/text()').get()
            author = news.xpath('.//p[@class="qa-contributor-name lx-stream-post__contributor-name gel-long-primer gs-u-m0"]/text()').get()
            date = news.xpath('.//span[@class="qa-post-auto-meta"]/text()').get()
            yield{
                'title' : title,
                'description' : description,
                'author' : author,
                'date' : date,
            }
        while True:
            try:
                go_next = self.driver.find_element_by_xpath('//a[@class="lx-pagination__btn gs-u-mr+ qa-pagination-next-page lx-pagination__btn--active"]')
                time.sleep(5)
                self.logger.info('Sleeping for 5 seconds.')
                go_next.click()
                resp = Selector(text=self.driver.page_source)
                for news in resp.xpath('//article[@class="qa-post gs-u-pb-alt+ lx-stream-post gs-u-pt-alt+ gs-u-align-left"]'):
                    title = news.xpath('.//span[@class="lx-stream-post__header-text gs-u-align-middle"]/text()').get()
                    description = news.xpath('.//p[@class="lx-stream-related-story--summary qa-story-summary"]/text()').get()
                    author = news.xpath('.//p[@class="qa-contributor-name lx-stream-post__contributor-name gel-long-primer gs-u-m0"]/text()').get()
                    date = news.xpath('.//span[@class="qa-post-auto-meta"]/text()').get()
                    yield{
                        'title' : title,
                        'description' : description,
                        'author' : author,
                        'date' : date,
                    }
            except:
                self.logger.info('No more pages to load')
                self.driver.quit()
                break    

process = CrawlerProcess()
process.crawl(BbcNewsSpider)
process.start()