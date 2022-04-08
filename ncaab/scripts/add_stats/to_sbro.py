from ncaab.spiders.srcbb import SrcbbSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(
        SrcbbSpider,
        input_path="ncaab/data/odds/sbro/past_events.csv",
        output_path="ncaab/data/odds_with_stats/sbro/past_events.csv",
        save=True,
    )
    process.start()
