import pandas as pd
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from urllib.parse import urlparse, parse_qs, urlencode
from ncaab.utils.teams import teams
from ncaab.constants import ROOT_DIR
from scrapy.utils.project import get_project_settings


class TeamsSpider(scrapy.Spider):
    name = "teams"
    custom_settings = {"DOWNLOAD_DELAY": 2}

    def start_requests(self):
        self.master = dict()
        for t in self.teams:
            if t in teams.as_dict().keys():
                print(f"Already recognize {t}")
                continue
            print(f"Searching for {t}")
            self.master[t] = []
            q = urlencode({"search": t + " Men's Basketball"})
            s = f"https://en.wikipedia.org/w/index.php?{q}"
            yield scrapy.Request(
                s, callback=self.parse_wikipedia, cb_kwargs=dict(team=t)
            )
            q = urlencode(
                {"q": t + " Men's " + '"' + "Basketball" + '"' + " Wikipedia"}
            )
            s = f"https://www.bing.com/search?{q}"
            yield scrapy.Request(s, callback=self.parse_bing, cb_kwargs=dict(team=t))
            q = urlencode(
                {"p": t + " Men's " + '"' + "Basketball" + '"' + " Wikipedia"}
            )
            s = f"https://search.yahoo.com/search?{q}"
            yield scrapy.Request(s, callback=self.parse_yahoo, cb_kwargs=dict(team=t))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TeamsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse_yahoo(self, response, team=None):
        url = response.css("#web > ol").css("h3 > a::attr(href)").get()
        assert url.startswith("https://en.wikipedia.org/wiki/")
        self.master[team].append(url)

    def parse_bing(self, response, team=None):
        url = response.css("ol[id='b_results']").css("a::attr(href)").get()
        assert url.startswith("https://en.wikipedia.org/wiki/")
        self.master[team].append(url)

    def parse_wikipedia(self, response, team=None):
        rel_url = response.css(
            ".mw-search-result-heading > a::attr(href)"
        ).extract_first()
        url = response.urljoin(rel_url)
        self.master[team].append(url)

    def spider_closed(self, spider):
        for k, v in self.master.items():
            df = pd.DataFrame({"urls": v})
            v_counts = df.value_counts(normalize=True)
            if v_counts.iloc[0] > 0.5:
                max_url = v_counts.to_frame().reset_index()["urls"].iloc[0]
                teams.add(k, max_url)
            else:
                print(f"Urls: {v}" f"\n do not agree for {k}.")


if __name__ == "__main__":
    last_events_path = os.path.join(ROOT_DIR, "ncaab/data/odds/bovada/last_events.csv")
    df = pd.read_csv(last_events_path, index_col=0)
    all_teams = sorted(set(df["top_team"]).union(df["bottom_team"]))
    process = CrawlerProcess(get_project_settings())
    process.crawl(TeamsSpider, teams=all_teams)
    process.start()
