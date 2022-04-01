import pandas as pd
import numpy as np
import scrapy
import os
from ncaab.constants import ROOT_DIR, SRCBB_COLUMNS
from ncaab.utils.teams import teams
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def clean_df(df):
    df = df.copy().dropna(axis=1, how="all")
    cols = []
    for col in df.columns:
        if col[0].startswith("Unnamed") or col[0].startswith("School"):
            c = col[1]
        elif col[0].startswith("Opponent"):
            c = "Opp_" + col[1]
        if c.startswith("Unnamed"):
            c = "H/A"
        cols.append(c)
    df.columns = cols
    df = df.loc[~(df["G"] == "G")].loc[pd.notnull(df["G"])]
    cols = list(df.columns)
    cols[cols.index("Opp")] = "Op"
    df.columns = cols
    df = df.astype(str)
    return df


def mk_joiner(t, game_datetime, bottom_team, top_team, is_top):
    pre = "top"
    if not is_top:
        pre = "bottom"
    cols = [f"{pre}_s_{c}" for c in t.columns]
    t.columns = cols
    m = pd.DataFrame(
        data=dict(
            game_datetime=[game_datetime],
            top_team=[bottom_team],
            bottom_team=[top_team],
        )
    )
    return m, t


class SrcbbSpider(scrapy.Spider):
    """
    Take a game_date, top_team, bottom_team
    Get stats from each of their last 7 games played
    """

    name = "srcbb"
    custom_settings = {"CLOSESPIDER_ERRORCOUNT": 1}

    def __init__(self, input_path="", output_path="", save=False, *args, **kwargs):
        assert input_path, "input_path cannot be empty string"
        assert output_path, "output_path cannot be empty string"
        super().__init__(*args, **kwargs)
        self.skips = 0
        self.save = save
        self.input_path = os.path.join(ROOT_DIR, input_path)
        self.output_path = os.path.join(ROOT_DIR, output_path)
        self.master_df = pd.read_csv(self.input_path, index_col=0, dtype=str).set_index(
            ["game_datetime", "top_team", "bottom_team"], drop=True
        )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SrcbbSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        mk_url = (
            lambda t, sea: f"https://www.sports-reference.com/cbb/schools/{t}/{sea}-gamelogs.html"
        )
        k = 0
        tot = len(self.master_df.index.values)
        if "bottom_s_Opp_PF_1" not in self.master_df.columns:
            for col in SRCBB_COLUMNS:
                self.master_df[col] = np.nan
        # We need to compile a list of these, there's about 5 and we need to remove them
        outlawed = {
            "Chaminade",
            "AlaskaAnchorage",
            "ConcordiaSt.Paul",
            "TXPanAmerican",
            "Texas-PanAmerican",
        }
        for date, t1, t2 in self.master_df.index.values:
            if t1 in outlawed:
                print(f"Skipping {t1}")
                self.skips += 1
                k += 1
                continue
            if t2 in outlawed:
                print(f"Skipping {t2}")
                self.skips += 1
                k += 1
                continue
            print(round(k / tot, 2))
            inds = [date, t1, t2]
            if pd.notnull(
                self.master_df.loc[tuple(inds), "bottom_s_Opp_PF_1"]
            ) and pd.notnull(self.master_df.loc[tuple(inds), "top_s_Opp_PF_1"]):
                print(f"Skipping {date}, {t1}, {t2}")
                k += 1
                continue
            season = pd.to_datetime(date).year + round(
                pd.to_datetime(date).day_of_year / 365
            )
            try:
                t1_slug = teams[t1]["srcbb_slug"]
            except KeyError as e:
                print(t1)
                raise e
            start_url = mk_url(t1_slug, season)
            yield scrapy.Request(
                start_url,
                cb_kwargs=dict(
                    game_datetime=date, top_team=t1, bottom_team=t2, is_top=True
                ),
            )
            try:
                t2_slug = teams[t2]["srcbb_slug"]
            except KeyError as e:
                print(t2)
                raise e
            start_url = mk_url(t2_slug, season)
            yield scrapy.Request(
                start_url,
                cb_kwargs=dict(
                    game_datetime=date, top_team=t2, bottom_team=t1, is_top=False
                ),
            )
            # if k > 50:
            #     break
            k += 1
            # break

    def spider_closed(self, spider):
        print(f"We skipped: {self.skips} games due to data errors.")
        if self.save:
            print("Spider closed. Saving master_df...")
            assert len(self.master_df.columns) == 559
            self.master_df.astype(str).reset_index().to_csv(self.output_path)
            print("Saved.")
        else:
            print("Didn't save anything.")

    def parse(
        self,
        response,
        game_datetime=None,
        top_team=None,
        bottom_team=None,
        games_back=7,
        is_top=True,
    ):
        inds = [game_datetime, top_team, bottom_team]
        if not is_top:
            inds = [game_datetime, bottom_team, top_team]
        df = pd.read_html(response.css("table")[0].get())[0]
        df = clean_df(df)
        master_scores = self.master_df.loc[tuple(inds)]
        df_scores = df.loc[pd.to_datetime(game_datetime) == pd.to_datetime(df["Date"])]
        has_scores = True
        if len(df_scores) == 0:
            if pd.to_datetime(game_datetime) >= pd.to_datetime(
                pd.to_datetime("now", utc=True)
                .tz_convert("America/Los_Angeles")
                .strftime("%Y-%m-%d")
            ):
                print(
                    f"Game hasn't happened yet {game_datetime}, {top_team}, {bottom_team}"
                )
                has_scores = False
            else:
                print(
                    f"No matching srcbb game: {game_datetime}, {top_team}, {bottom_team}"
                )
                self.skips += 0.5
                return
        if has_scores:
            df_scores = df_scores.iloc[0]

        if is_top and has_scores:
            if pd.isnull(master_scores["top_final"]) or pd.isnull(
                master_scores["bottom_final"]
            ):
                self.master_df.loc[tuple(inds), "top_final"] = df_scores["Tm"]
                self.master_df.loc[tuple(inds), "bottom_final"] = df_scores["Opp"]
                master_scores = self.master_df.loc[tuple(inds)]
            if master_scores["top_final"] != df_scores["Tm"]:
                self.skips += 0.5
                print(
                    f"Top score wrong: {master_scores['top_final']} vs. {df_scores['Tm']}, {inds}, {response.url}"
                )
                return
            if master_scores["bottom_final"] != df_scores["Opp"]:
                self.skips += 0.5
                print(
                    f"Bottom score wrong: {master_scores['bottom_final']} vs. {df_scores['Opp']}, {inds}, {response.url}"
                )
                return
        elif has_scores:
            if pd.isnull(master_scores["top_final"]) or pd.isnull(
                master_scores["bottom_final"]
            ):
                self.master_df.loc[tuple(inds), "top_final"] = df_scores["Opp"]
                self.master_df.loc[tuple(inds), "bottom_final"] = df_scores["Tm"]
                master_scores = self.master_df.loc[tuple(inds)]
            if master_scores["bottom_final"] != df_scores["Tm"]:
                self.skips += 0.5
                print(
                    f"Top score wrong: {master_scores['bottom_final']} vs. {df_scores['Tm']}, {inds}, {response.url}"
                )
                return
            if master_scores["top_final"] != df_scores["Opp"]:
                self.skips += 0.5
                print(
                    f"Bottom score wrong: {master_scores['top_final']} vs. {df_scores['Opp']}, {inds}, {response.url}"
                )
                return
        # Limit to last 7 games
        df = df.loc[pd.to_datetime(df["Date"]) < pd.to_datetime(game_datetime)].iloc[
            -games_back:
        ]
        if df.empty:
            return
        t = df.iloc[-1, :].to_frame().T.reset_index(drop=True)
        t.columns = [f"{c}_{1}" for c in t.columns]
        for i in range(2, len(df) + 1):
            r = df.iloc[-i, :].to_frame().T.reset_index(drop=True)
            r.columns = [f"{c}_{i}" for c in r.columns]
            t = pd.merge(
                t,
                r,
                left_index=True,
                right_index=True,
            )
        m, t = mk_joiner(t, game_datetime, top_team, bottom_team, is_top=is_top)
        full_df = pd.concat([m, t], axis=1).set_index(
            ["game_datetime", "top_team", "bottom_team"], drop=True
        )
        self.master_df.loc[tuple(inds), list(full_df.columns)] = list(full_df.values[0])


if __name__ == "__main__":
    raise ValueError("Remove me to run.")
    process = CrawlerProcess(get_project_settings())
    process.crawl(
        SrcbbSpider,
        input_path="ncaab/data/past_events.csv",
        output_path="ncaab/data/past_events.csv",
        save=True,
    )
    # When I last ran this:
    # We skipped: 117.0 games due to data errors.

    # Which is fine by me.
    process.start()
