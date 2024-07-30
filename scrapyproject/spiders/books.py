import csv
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
import os


class BooksSpider(scrapy.Spider):
    name = 'books'

    def start_requests(self):
        URL = 'https://books.toscrape.com/'
        yield scrapy.Request(url=URL, callback=self.response_parser)

    def response_parser(self, response):
        for selector in response.css('article.product_pod'):
            yield {
                'title': selector.css('h3 > a::attr(title)').extract_first(),
                'price': selector.css('.price_color::text').extract_first()
            }

        next_page_link = response.css('li.next a::attr(href)').extract_first()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.response_parser)


def book_spider_result():
    books_results = []

    def crawler_results(item):
        books_results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)
    crawler_process = CrawlerProcess()
    crawler_process.crawl(BooksSpider)
    crawler_process.start()
    return books_results


if __name__ == '__main__':
    # Get the current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")

    # Run the spider and collect the data
    books_data = book_spider_result()

    # Check if the books_data list is not empty
    if books_data:
        print(f"Number of books scraped: {len(books_data)}")

        # CSV Writing Logic
        try:
            keys = books_data[0].keys()
            csv_file_path = os.path.join(current_dir, 'books_data.csv')

            with open(csv_file_path, 'w', newline='') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(books_data)

            print(f"CSV file created successfully at: {csv_file_path}")

        except Exception as e:
            print(f"Error writing CSV: {e}")

    else:
        print("No data scraped.")
