import scrapy
from scrapy.crawler import CrawlerProcess
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

# Отключаем вывод логов Scrapy в консоль
logging.getLogger('scrapy').propagate = False


class MySpider(scrapy.Spider):
    name = 'qa_crawler'
    start_urls = []

    def __init__(self,
                 start_url='https://ru.wikipedia.org/wiki/',
                 links_lim=10,
                 *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls += [start_url]
        self.links_lim = links_lim
        self.processed_links = 0
        self.allowed_domain = urlparse(self.start_urls[0]).netloc  # Получаем домен из начальной ссылки

    def parse(self, response):
        # Используем BeautifulSoup для извлечения текста без тегов
        soup = BeautifulSoup(response.text, 'html.parser')

        # Проверяем наличие элемента <article>
        article = soup.select_one('article')
        if article:
            text = article.text
        else:
            text = soup.get_text()
        text = soup.get_text()

        # Записываем текст в файл
        with open('pages.txt', 'a') as f:
            # Выводим ссылку на страницу родительскую
            f.write("Page URL: " + response.url + "\n")
            f.write(text)
            f.write('\n')

        # Получаем ссылки со страницы
        links = soup.find_all('a', href=True)
        for link in links:
            url = urljoin(response.url, link['href'])
            parsed_url = urlparse(url)
            # Проверяем, что ссылка начинается с нужного домена
            if parsed_url.netloc == self.allowed_domain:
                yield scrapy.Request(url, callback=self.parse, meta={
                    'parent_url': response.url})  # Передаем ссылку родительской страницы через метаданные
                self.processed_links += 1
                if self.processed_links >= self.links_lim:
                    break


class MyDownloaderMiddleware:
    def process_exception(self, request, exception, spider):
        spider.logger.error(f"Error processing link {request.url}: {exception}")
        return None  # Возвращаем None, чтобы сообщить Scrapy, что исключение обработано


def spider_closed(spider, reason):
    print(f"Total processed links: {spider.processed_links}")


def update_pages(url, lim):
    # Проверяем существует ли файл, если да, удаляем его
    with open('pages.txt', 'w') as f:
        f.write('')

    process = CrawlerProcess(settings={
        'LOG_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'crawler.MyDownloaderMiddleware': 543,  # Поднимаем приоритет middleware выше, чем у стандартных middleware
        }
    })
    process.crawl(MySpider, url, lim)
    for crawler in process.crawlers:
        crawler.signals.connect(spider_closed,
                                signal=scrapy.signals.spider_closed)  # Связываем обратный вызов события завершения краулинга для каждого краулера
    process.start()
    process.join()
    process.stop()

# if __name__ == '__main__':
#     update_pages('https://ru.stardewvalleywiki.com/Начало', 10)