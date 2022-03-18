import os
import time
import traceback
import pandas as pd
import numpy as np
import scrapy
from scrapy_playwright.page import PageCoroutine
from ncaab.utils.team_names import sanitize_team


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


class BovadaSpider(scrapy.Spider):
    name = "bovada"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = None
        self.schools = None

    def start_requests(self):
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
        game_datetime = (
            pd.to_datetime(game_date + game_time + time.strftime("%z"))
            .tz_convert("UTC")
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        # Team Names
        top_team, bottom_team = game_box.css(".competitor-name>.name::text").getall()
        top_team = sanitize_team(top_team)
        bottom_team = sanitize_team(bottom_team)

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
            game_datetime=game_datetime,
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
        scrape_datetime = pd.to_datetime("now", utc=True).round("s")
        for game_box in game_boxes:
            try:
                bd = self.parse_game_box(game_box)
                bovada_list.append(bd)
            except (ValueError, IndexError):
                # TODO: Make these better
                # Value Error for when there is no ML or missing lines
                # Index Error when the date says "Second Half"
                traceback.print_exc()
        bovada_df = pd.DataFrame(data=bovada_list, columns=bovada_list[0].keys())
        bovada_df["scrape_datetime"] = scrape_datetime.strftime("%Y-%m-%d %H:%M:%S")
        return bovada_df

    def parse(self, response):
        bovada_df = self.parse_bovada(response)
        bovada_df["top_final"] = np.nan
        bovada_df["bottom_final"] = np.nan
        # We don't want to do this here, later in the processing
        # bovada_df = org_df(bovada_df)
        cols = [
            "scrape_datetime",
            "game_datetime",
            "top_team",
            "top_final",
            "bottom_final",
            "bottom_team",
            "top_spread",
            "top_spread_odds",
            "top_ml_odds",
            "top_total",
            "top_total_odds",
            "bottom_spread",
            "bottom_spread_odds",
            "bottom_ml_odds",
            "bottom_total",
            "bottom_total_odds",
        ]
        bovada_df = bovada_df[cols]
        output_file = os.path.dirname(__file__)
        output_file = os.path.dirname(output_file)
        output_file = os.path.join(output_file, "data", "bovada", "next_events.csv")
        bovada_df.to_csv(output_file)
