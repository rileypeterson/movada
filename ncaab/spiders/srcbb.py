import pandas as pd
import scrapy


class SrcbbSpider(scrapy.Spider):
    """
    Take a game_date, top_team, bottom_team
    Get stats from each of their last 7 games played
    """

    name = "srcbb"

    def start_requests(self):
        df = pd.read_csv("/ncaab/data/sbro/ncaab_history_init.csv")
        a = 1

    def parse(self, response):
        pass
