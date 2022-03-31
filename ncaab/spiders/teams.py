import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, parse_qs, urlencode
from ncaab.utils.teams import teams


class TeamsSpider(scrapy.Spider):
    name = "teams"
    custom_settings = {"DOWNLOAD_DELAY": 2}

    def start_requests(self):
        for t in self.teams:
            print(f"Searching for {t}")
            q = urlencode({"search": t + " Men's Basketball"})
            s = f"https://en.wikipedia.org/w/index.php?{q}"
            yield scrapy.Request(s)

    def parse(self, response):
        rel_url = response.css(
            ".mw-search-result-heading > a::attr(href)"
        ).extract_first()
        yield response.urljoin(rel_url)
        a = 1


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(TeamsSpider, teams=["St. Peter's", "Gonzaga"])
    process.start()
