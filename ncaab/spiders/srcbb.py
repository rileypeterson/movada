import pandas as pd
import numpy as np
import scrapy
import os
from ncaab.constants import ROOT_DIR, SRCBB_COLUMNS, OUTLAWED_TEAMS
from ncaab.utils.teams import teams
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from pprint import pprint

CRAWLEDMSG = "Crawled (%(status)s) %(request)s%(request_flags)s (referer: %(referer)s)%(response_flags)s"

STDMSG = (
    "%(emoji)s %(progress)s %(success)s:%(reason)s [ %(status)s | %(cached)s ] : "
    "%(game_datetime)s - %(top_team)s vs. %(bottom_team)s ; %(request)s"
)
EMOJIS = {"skip": "\u23ED", "success": "\u2705", "future": "\u23F1"}


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
    custom_settings = {"CLOSESPIDER_ERRORCOUNT": 1, "LOG_LEVEL": "INFO"}

    def __init__(
        self,
        stats,
        input_path="",
        output_path="",
        save=False,
        games_back=7,
        *args,
        **kwargs,
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
        self.games_back = games_back

    @property
    def progress(self):
        f = lambda x: self.stats.get_value(x, default=0)
        num = (
            f("processed_matchup_count")
            + f("no_matching_game_count")
            + f("future_game_count")
            + f("incorrect_score_count")
            + f("already_has_stats_count")
        )
        percent_done = f"{round(100 * (num / self.stats.get_value('total_matchup_count')), 2): >6.2f}%"
        return percent_done

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SrcbbSpider, cls).from_crawler(
            crawler, crawler.stats, *args, **kwargs
        )
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        self.master_df = self.edit_master_df()
        self.stats.set_value("total_matchup_count", len(self.master_df.index.values))
        for date, t1, t2 in self.master_df.index.values:
            matchup_has_stats = self.already_has_stats(date, t1, t2)
            if matchup_has_stats:
                continue

            # Generate two requests per matchup, one for the top_team
            # and one for the bottom_team
            url = self.srcbb_url(date, t1)
            yield scrapy.Request(
                url,
                cb_kwargs=dict(
                    data=dict(
                        game_datetime=date, top_team=t1, bottom_team=t2, is_top=True
                    )
                ),
            )
            url = self.srcbb_url(date, t2)
            yield scrapy.Request(
                url,
                cb_kwargs=dict(
                    data=dict(
                        game_datetime=date, top_team=t2, bottom_team=t1, is_top=False
                    )
                ),
            )
            # break

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

    def already_has_stats(self, date, t1, t2):
        inds = [date, t1, t2]
        top_has_stats = pd.notnull(self.master_df.loc[tuple(inds), "top_s_Opp_PF_1"])
        bottom_has_stats = pd.notnull(
            self.master_df.loc[tuple(inds), "bottom_s_Opp_PF_1"]
        )
        is_past = pd.to_datetime(date) < self.today
        # This fails for the first game in any season, i.e. it will always re-check
        # I'm okay with that
        if bottom_has_stats and top_has_stats and is_past:
            args = {
                "emoji": EMOJIS["skip"],
                "progress": self.progress,
                "success": "SKIP",
                "reason": " Already has stats",
                "status": "",
                "cached": "",
                "game_datetime": date,
                "top_team": t1,
                "bottom_team": t2,
                "request": "",
            }
            self.logger.info(STDMSG, args)
            self.stats.inc_value("already_has_stats_count")
            return True
        return False

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

    def enhance_data(self, response, data):
        data["inds"] = [data["game_datetime"], data["top_team"], data["bottom_team"]]
        if not data["is_top"]:
            data["inds"] = [
                data["game_datetime"],
                data["bottom_team"],
                data["top_team"],
            ]
        data["response"] = response
        # Retrieve srcbb data (df) and master_df data (mdf)
        df, mdf = self.retrieve_data(data)
        data["df"] = df
        data["mdf"] = mdf
        data["cached"] = ""
        if "cached" in response.flags:
            data["cached"] = "cached"
        data["matchup"] = (
            f"{data['game_datetime']} | "
            f"{data['top_team']} vs. {data['bottom_team']}"
        )
        return data

    def parse(
        self,
        response,
        data=None,
    ):
        data = self.enhance_data(response, data)

        # Look to see if the game is included in the srcbb game log
        df_scores = data["df"].loc[
            pd.to_datetime(data["game_datetime"]) == pd.to_datetime(data["df"]["Date"])
        ]
        no_matching_game = len(df_scores) == 0
        is_future_game = pd.to_datetime(data["game_datetime"]) >= self.today

        # 4 Cases
        # Future game -> get past scores, but don't check current scores
        # Past game, but not in srcbb -> skip
        # Past game, but score doesn't match with srcbb -> skip
        # Past game, in srcbb with correct scores -> get past scores
        if no_matching_game and is_future_game:
            return self.handle_future_game(data)

        elif no_matching_game and not is_future_game:
            self.fail_stats_collect(data, "no_matching_game_matchup", data["matchup"])
            return self.msg(
                data, "SKIP", " No matching srcbb matchup", "no_matching_game_count"
            )

        has_correct_score, wrong_score_msg = self.check_score(data)
        if not has_correct_score:
            # wrong_score_msg = "Villanova 98 (srcbb) != Villanova 97 (master)"
            self.fail_stats_collect(
                data, "incorrect_score_matchup", data["matchup"] + f" {wrong_score_msg}"
            )
            return self.msg(
                data,
                "SKIP",
                f" Incorrect score: {wrong_score_msg}",
                "incorrect_score_count",
            )

        self.get_past_scores(data)
        return self.msg(data, "SUCCESS", "", "processed_matchup_count")

    def retrieve_data(self, d):
        # Retrieve the game log table
        df = pd.read_html(d["response"].css("table")[0].get())[0]
        df = clean_df(df)

        # Find the relevant row in the master_df
        mdf = self.master_df.loc[tuple(d["inds"])]
        return df, mdf

    def fail_stats_collect(self, d, stat, msg):
        if d["is_top"]:
            self.stats.inc_value(
                stat,
                start=[],
                count=[msg],
            )

    def msg(self, d, success, reason, cnt):
        args = {
            "emoji": EMOJIS[success.lower()],
            "progress": self.progress,
            "success": success,
            "reason": reason,
            "status": d["response"].status,
            "cached": d["cached"],
            "game_datetime": d["game_datetime"],
            "top_team": d["top_team"],
            "bottom_team": d["bottom_team"],
            "request": d["response"].request,
        }
        if d["is_top"]:
            self.logger.info(STDMSG, args)
            self.stats.inc_value(cnt, count=1)

    def handle_future_game(self, d):
        # TODO: Add check to make sure the game is the next game else skip.
        self.get_past_scores(d)
        self.msg(d, "FUTURE", "", "future_game_count")

    def spider_closed(self, spider):
        pprint(self.stats.get_stats())
        if self.save:
            print("Spider closed. Saving master_df...")
            assert len(self.master_df.columns) == 559
            self.master_df.astype(str).reset_index().to_csv(self.output_path)
            print("Saved.")
        else:
            print("Didn't save anything.")

    def check_score(self, d):
        # TODO: Rewrite

        if d["is_top"]:
            tm = "Tm"
            opp = "Opp"
        else:
            tm = "Opp"
            opp = "Tm"
        srcbb_scores = (
            d["df"]
            .loc[pd.to_datetime(d["game_datetime"]) == pd.to_datetime(d["df"]["Date"])]
            .iloc[0]
        )
        master_top_score = d["mdf"]["top_final"]
        master_bottom_score = d["mdf"]["bottom_final"]
        srcbb_top_score = srcbb_scores[tm]
        srcbb_bottom_score = srcbb_scores[opp]
        # wrong_score_msg = "Villanova 98 (srcbb) != Villanova 97 (master)"
        if not master_top_score or not master_bottom_score:
            # Insert score into mdf row
            self.master_df.loc[tuple(d["inds"]), "top_final"] = srcbb_scores[tm]
            self.master_df.loc[tuple(d["inds"]), "bottom_final"] = srcbb_scores[opp]
        if master_top_score != srcbb_top_score:
            return (
                False,
                f"{d['top_team']} {srcbb_top_score} (srcbb) != {master_top_score} (master)",
            )
        if master_bottom_score != srcbb_bottom_score:
            # Still want to skip, but don't need to record twice...
            return (
                False,
                f"{d['bottom_team']} {srcbb_bottom_score} (srcbb) != {master_bottom_score} (master)",
            )
        return True, ""

    def get_past_scores(self, d):
        df = d["df"]
        # Limit to last 7 games
        df = df.loc[
            pd.to_datetime(df["Date"]) < pd.to_datetime(d["game_datetime"])
        ].iloc[-self.games_back :]
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
        m, t = mk_joiner(
            t, d["game_datetime"], d["top_team"], d["bottom_team"], is_top=d["is_top"]
        )
        full_df = pd.concat([m, t], axis=1).set_index(
            ["game_datetime", "top_team", "bottom_team"], drop=True
        )
        self.master_df.loc[tuple(d["inds"]), list(full_df.columns)] = list(
            full_df.values[0]
        )


if __name__ == "__main__":
    # raise ValueError("Remove me to run.")
    process = CrawlerProcess(get_project_settings())
    process.crawl(
        SrcbbSpider,
        input_path="ncaab/data/sbro/past_events.csv",
        output_path="ncaab/data/past_events.csv",
        save=True,
    )
    # When I last ran this:
    # We skipped: 117.0 games due to data errors.

    # Which is fine by me.
    process.start()
