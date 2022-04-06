import pandas as pd
import numpy as np
import scrapy
import os
from ncaab.constants import ROOT_DIR, SRCBB_COLUMNS, OUTLAWED_TEAMS
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
    Take a DataFrame with game_date, top_team, bottom_team columns
    Get stats from each of their last 7 games played
    add those stats to the DataFrame and optionally save
    the DataFrame as a csv to the output_path.
    """

    name = "srcbb"
    # If there is any error immediately close the spider
    custom_settings = {"CLOSESPIDER_ERRORCOUNT": 1}

    def __init__(
        self, stats, input_path="", output_path="", save=False, *args, **kwargs
    ):
        assert input_path, "input_path cannot be empty string"
        assert output_path, "output_path cannot be empty string"
        super().__init__(*args, **kwargs)
        self.stats = stats
        self.save = save
        self.input_path = os.path.join(ROOT_DIR, input_path)
        self.output_path = os.path.join(ROOT_DIR, output_path)
        self.master_df = pd.read_csv(self.input_path, index_col=0, dtype=str).set_index(
            ["game_datetime", "top_team", "bottom_team"], drop=True
        )
        self.today = pd.to_datetime(
            pd.to_datetime("now", utc=True)
            .tz_convert("America/Los_Angeles")
            .strftime("%Y-%m-%d")
        )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SrcbbSpider, cls).from_crawler(
            crawler, crawler.stats, *args, **kwargs
        )
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def edit_master_df(self):
        if "bottom_s_Opp_PF_1" not in self.master_df.columns:
            # Add on stats columns if not there already
            for col in SRCBB_COLUMNS:
                self.master_df[col] = np.nan

        # Remove teams that are not within the srcbb system
        outlaw_top = self.master_df.index.get_level_values("top_team").isin(
            OUTLAWED_TEAMS
        )
        outlaw_bottom = self.master_df.index.get_level_values("bottom_team").isin(
            OUTLAWED_TEAMS
        )
        self.master_df = self.master_df[~(outlaw_top | outlaw_bottom)]
        return self.master_df

    @staticmethod
    def srcbb_url(date, team):
        mk_url = (
            lambda t, sea: f"https://www.sports-reference.com/cbb/schools/{t}/{sea}-gamelogs.html"
        )
        season = pd.to_datetime(date).year + round(
            pd.to_datetime(date).day_of_year / 365
        )
        try:
            t1_slug = teams[team]["srcbb_slug"]
        except KeyError as e:
            print(f"Team: {team} not found in teams dict!")
            raise e
        start_url = mk_url(t1_slug, season)
        return start_url

    def start_requests(self):
        self.master_df = self.edit_master_df()
        self.stats.set_value("total_matchups", len(self.master_df.index.values))
        for date, t1, t2 in self.master_df.index.values:
            inds = [date, t1, t2]
            top_has_stats = pd.notnull(
                self.master_df.loc[tuple(inds), "top_s_Opp_PF_1"]
            )
            bottom_has_stats = pd.notnull(
                self.master_df.loc[tuple(inds), "bottom_s_Opp_PF_1"]
            )
            is_past = pd.to_datetime(date) < self.today
            # This fails for the first game in any season, i.e. it will always re-check
            # I'm okay with that
            if bottom_has_stats and top_has_stats and is_past:
                print(f"Skipping {date}, {t1}, {t2}")
                self.stats.inc_value("skipped_matchups")
                continue
            # Generate two requests per matchup, one for the top_team
            # and one for the bottom_team
            url = self.srcbb_url(date, t1)
            yield scrapy.Request(
                url,
                cb_kwargs=dict(
                    game_datetime=date, top_team=t1, bottom_team=t2, is_top=True
                ),
            )
            url = self.srcbb_url(date, t2)
            yield scrapy.Request(
                url,
                cb_kwargs=dict(
                    game_datetime=date, top_team=t2, bottom_team=t1, is_top=False
                ),
            )

    def spider_closed(self, spider):
        print(self.stats.get_stats())
        if self.save:
            print("Spider closed. Saving master_df...")
            assert len(self.master_df.columns) == 559
            self.master_df.astype(str).reset_index().to_csv(self.output_path)
            print("Saved.")
        else:
            print("Didn't save anything.")

    def check_score(self, is_top, master_scores, df_scores, inds, response):
        if is_top:
            tm = "Tm"
            opp = "Opp"
            top = "Top"
            bottom = "Bottom"
        else:
            tm = "Opp"
            opp = "Tm"
            top = "Bottom"
            bottom = "Top"

        if pd.isnull(master_scores["top_final"]) or pd.isnull(
            master_scores["bottom_final"]
        ):
            self.master_df.loc[tuple(inds), "top_final"] = df_scores[tm]
            self.master_df.loc[tuple(inds), "bottom_final"] = df_scores[opp]
            master_scores = self.master_df.loc[tuple(inds)]
        if master_scores["top_final"] != df_scores[tm]:
            self.stats.inc_value(f"{top}_score_wrong".lower())
            self.stats.inc_value(
                f"{top}_score_wrong_details",
                start=[],
                count=[
                    f"{master_scores['top_final']} vs. {df_scores[tm]}, {inds}, {response.url}"
                ],
            )
            print(
                f"{top} score wrong: {master_scores['top_final']} vs. {df_scores[tm]}, {inds}, {response.url}"
            )
            return False
        if master_scores["bottom_final"] != df_scores[opp]:
            self.stats.inc_value(f"{bottom}_score_wrong".lower())
            self.stats.inc_value(
                f"{top}_score_wrong_details",
                start=[],
                count=[
                    f"{master_scores['bottom_final']} vs. {df_scores[opp]}, {inds}, {response.url}"
                ],
            )
            print(
                f"{bottom} score wrong: {master_scores['bottom_final']} vs. {df_scores[opp]}, {inds}, {response.url}"
            )
            return False
        return True

    def get_past_scores(
        self, df, games_back, inds, game_datetime, top_team, bottom_team, is_top
    ):
        # Limit to last 7 games
        df = df.loc[pd.to_datetime(df["Date"]) < pd.to_datetime(game_datetime)].iloc[
            -games_back:
        ]
        if df.empty:
            # First game of the season
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

        # Retrieve the game log table
        df = pd.read_html(response.css("table")[0].get())[0]
        df = clean_df(df)

        # Find the relevant row in the master_df
        master_scores = self.master_df.loc[tuple(inds)]

        # Look to see if the game is included in the srcbb game log
        df_scores = df.loc[pd.to_datetime(game_datetime) == pd.to_datetime(df["Date"])]

        no_matching_game = len(df_scores) == 0
        is_future_game = pd.to_datetime(game_datetime) >= self.today

        # 4 Cases
        # Future game -> get past scores, but don't check current scores
        # Past game, but not in srcbb -> skip
        # Past game, but score doesn't match with srcbb -> skip
        # Past game, in srcbb with correct scores -> get past scores

        if no_matching_game:
            # Future Game
            if is_future_game:
                print(
                    f"Game hasn't happened yet {game_datetime}, {top_team}, {bottom_team}"
                )
                self.stats.inc_value("future_games")
                self.get_past_scores(
                    df, games_back, inds, game_datetime, top_team, bottom_team, is_top
                )
                return

            # Game is in the past, but not in srcbb :(
            print(f"No matching srcbb game: {game_datetime}, {top_team}, {bottom_team}")
            self.stats.inc_value("no_matching_games")
            self.stats.inc_value(
                "no_matching_games_matchups",
                start=[],
                count=[f"{game_datetime}, {top_team}, {bottom_team}"],
            )
            return

        # If there is a matching game, then we want to check the score.
        df_scores = df_scores.iloc[0]
        if self.check_score(is_top, master_scores, df_scores, inds, response):
            # If the score checks out fill the past stats
            self.get_past_scores(
                df, games_back, inds, game_datetime, top_team, bottom_team, is_top
            )
            if is_top:
                print(game_datetime, top_team, bottom_team, "\u2705")
        self.stats.inc_value("processed_matchups")
        f = lambda x: self.stats.get_value(x, default=0)
        num = (
            f("processed_matchups")
            + f("no_matching_games_matchups")
            + f("future_games")
            + f("bottom_score_wrong")
            + f("top_score_wrong")
            + f("skipped_matchups")
        )
        print(f"{round(num / self.stats.get_value('total_matchups'), 2)} %")


if __name__ == "__main__":
    # raise ValueError("Remove me to run.")
    process = CrawlerProcess(get_project_settings())
    process.crawl(
        SrcbbSpider,
        input_path="ncaab/data/sbro/past_events.csv",
        output_path="ncaab/data/past_events.csv",
        save=False,
    )
    # When I last ran this:
    # We skipped: 117.0 games due to data errors.

    # Which is fine by me.
    process.start()
