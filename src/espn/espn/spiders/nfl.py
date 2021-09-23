"""
Scrape available nfl stats from ESPN
"""
import scrapy
import pandas as pd
from collections import defaultdict
from scrapy.exceptions import CloseSpider


def pp(d, td):
    col_name = td.css("::attr(class)").extract()[0]
    if col_name == "name":
        d["name"] += td.css("* > span")[0].css("::text").extract()[0]
        d["abbr"] += td.css("* > span")[1].css("::text").extract()[0]
    else:
        col_value = td.css(f'[class="{col_name}"]::text').extract()[0]
        d[col_name] = col_value
    return d


class NFLSpider(scrapy.Spider):
    name = "nfl"
    start_urls = [
        "https://www.espn.com/nfl/schedule",
    ]

    def parse(self, response):
        print(self.settings.get("CONCURRENT_REQUESTS"))
        year_links = response.css('li[data-type="year"]').css("a::attr(href)").extract()
        for year_link in year_links[::-1]:
            print(year_link)
            yield response.follow(year_link, self.parse_weeks)
            break

    def parse_weeks(self, response):
        week_links = (
            response.css('li[data-type="week"][data-season="reg"]')
            .css("a::attr(href)")
            .extract()
        )
        for week_link in week_links:
            print(week_link)
            yield response.follow(week_link, self.parse_games)
            break

    def parse_games(self, response):
        game_links = response.css(
            'td a[name="&lpos=nfl:schedule:score"]::attr(href)'
        ).extract()
        for game_link in game_links:
            print(game_link)
            yield response.follow(game_link, self.find_box_score_link)
            break

    def find_box_score_link(self, response):
        box_score_links = response.css(
            'li a[name="&lpos=nfl:game:post:subnav:box score"]::attr(href)'
        ).extract()
        for box_score_link in box_score_links:
            print(box_score_link)
            yield response.follow(box_score_link, self.parse_game_stats)
            break

    def parse_game_stats(self, response):
        print("parse_game_stats")
        tables = response.css("table")
        for table in tables[:-1]:
            d = defaultdict(list)
            for td in table.css("td"):
                col_name = td.css("::attr(class)").extract()
                if len(col_name) == 0:
                    continue
                col_name = col_name[0]

                if col_name == "name":
                    v = td.css("::text").extract()
                    if len(v) == 1:
                        d["name"] += ["TEAM"]
                        d["abbr"] += ["TEAM"]
                    if len(v) == 2:
                        d["name"] += [v[0]]
                        d["abbr"] += [v[1]]
                else:
                    col_value = td.css(f'[class="{col_name}"]::text').extract()
                    d[col_name] += col_value
            print(pd.DataFrame(d))
        raise CloseSpider("bandwidth_exceeded")
