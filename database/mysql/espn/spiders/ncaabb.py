import pandas as pd
import numpy as np
import scrapy
from scrapy_playwright.page import PageCoroutine
from thefuzz import process


def org_df(df):
    # Put favorite on left side
    df["top_ml_odds"] = df["top_ml_odds"].astype(int)
    df["bottom_ml_odds"] = df["bottom_ml_odds"].astype(int)
    top_df = df[[c for c in df.columns if "top_" in c]]
    bottom_df = df[[c for c in df.columns if "bottom_" in c]]
    top_copy = top_df.copy()

    # Moneyline
    top_df = top_df.where(
        top_df["top_ml_odds"] < bottom_df["bottom_ml_odds"], other=bottom_df.values
    )
    bottom_df = bottom_df.where(
        top_copy["top_ml_odds"] < bottom_df["bottom_ml_odds"], top_copy.values
    )
    df = pd.concat([df[["game_date"]], top_df, bottom_df], axis=1)
    return df


class NcaabbSpider(scrapy.Spider):
    name = "ncaabb"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = None
        self.schools = None

    def start_requests(self):
        # GET request
        start_url = "https://www.bovada.lv/sports/basketball/college-basketball"
        wait_for_first_coupon_box = PageCoroutine(
            "wait_for_selector",
            "sp-next-events",
        )
        scroll_to_bottom = PageCoroutine(
            "evaluate", "window.scrollBy(0, document.body.scrollHeight)"
        )
        yield scrapy.Request(
            start_url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_coroutines": [
                    wait_for_first_coupon_box,
                    scroll_to_bottom,
                ],
            },
        )

    @staticmethod
    def parse_game_box(game_box):
        # ONLY WORKS IF ML IS PRESENT
        # Game Date and Time
        game_date_elm = "span.period.hidden-xs"
        game_date = game_box.css(f"{game_date_elm}::text").getall()[0]
        game_time = game_box.css(f"{game_date_elm} > time.clock::text").getall()[0]

        # Team Names
        top_team, bottom_team = game_box.css(".competitor-name>.name::text").getall()

        spread_col, ml_col, total_col = game_box.css("sp-two-way-vertical")

        # Spread
        top_spread, bottom_spread = (
            spread_col.css("sp-spread-outcome > .market-line,bet-handicap")
            .css("::text")
            .getall()
        )
        top_spread_odds, bottom_spread_odds = spread_col.css(
            ".bet-price::text"
        ).extract()

        # Moneyline
        top_ml_odds, bottom_ml_odds = ml_col.css(".bet-price::text").extract()

        # Over / Under
        (top_total_label, top_total, bottom_total_label, bottom_total,) = (
            total_col.css(".market-line,bet-handicap,both-handicaps")
            .css("::text")
            .extract()
        )
        top_total_odds, bottom_total_odds = total_col.css(".bet-price::text").extract()
        d = dict(
            game_date=game_date,
            game_time=game_time,
            top_team=top_team,
            bottom_team=bottom_team,
            top_spread=top_spread,
            bottom_spread=bottom_spread,
            top_spread_odds=top_spread_odds,
            bottom_spread_odds=bottom_spread_odds,
            top_ml_odds=top_ml_odds,
            bottom_ml_odds=bottom_ml_odds,
            top_total_label=top_total_label,
            top_total=top_total,
            bottom_total_label=bottom_total_label,
            bottom_total=bottom_total,
            top_total_odds=top_total_odds,
            bottom_total_odds=bottom_total_odds,
        )
        return d

    def parse_bovada(self, response):
        game_boxes = response.css("sp-next-events").css("sp-coupon")
        bovada_list = []
        for game_box in game_boxes:
            try:
                bd = self.parse_game_box(game_box)
                bovada_list.append(bd)
            except ValueError:
                pass
        bovada_df = pd.DataFrame(data=bovada_list, columns=bovada_list[0].keys())
        return bovada_df

    def parse_teams(self, response):
        prefix = "/cbb/schools/"
        self.schools = [
            s.replace(prefix, "")[:-1]
            for s in response.css("td > a::attr(href)").getall()
        ]
        a = 1

        yield response.css("a").getall()

    def parse(self, response):
        bovada_df = self.parse_bovada(response)
        bovada_df["top_final"] = np.nan
        bovada_df["bottom_final"] = np.nan
        bovada_df = org_df(bovada_df)
        # TODO: Use relative path here
        master_df = pd.read_pickle("/Users/riley/Documents/movada/sbro/master.df")
        # Let's join these here
        final_cols = list(master_df.columns)
        self.df = pd.concat(
            [
                bovada_df[final_cols],
                master_df.sort_values(by="game_date", ascending=False),
            ],
            axis=0,
        )
        url = "https://www.sports-reference.com/cbb/schools/"
        yield scrapy.Request(url, callback=self.parse_teams)
        # b = self.fetch_teams()
        #
        # "https://www.sports-reference.com/cbb/schools/iowa-state/2016-gamelogs.html"
        # a = 1
        # yield {"url": response.url}


#
# "body > bx-site > ng-component > div > sp-sports-ui > div > main > div > section > main > sp-path-event > div > sp-next-events > div > div"
# "/html/body/bx-site/ng-component/div/sp-sports-ui/div/main/div/section/main/sp-path-event/div/sp-next-events/div/div"
# "/html/body/bx-site/ng-component/div/sp-sports-ui/div/main/div/section/main/sp-path-event/div/sp-next-events/div/div/div[2]/div/sp-coupon[1]"
