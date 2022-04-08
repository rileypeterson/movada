import os
import pandas as pd
import numpy as np
from ncaab.constants import ROOT_DIR, BOVADA_COLUMNS
from ncaab.utils.teams import teams
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ncaab.spiders.srcbb import SrcbbSpider
import subprocess
import tempfile


def convert_dt_to_pst(s):
    return pd.to_datetime(s, utc=True).dt.tz_convert("America/Los_Angeles")


def correct_bovada_df(df):
    # Convert the times to PST and make the game_datetime a date
    df["game_datetime"] = convert_dt_to_pst(df["game_datetime"]).dt.strftime("%Y-%m-%d")
    df["scrape_datetime"] = convert_dt_to_pst(df["scrape_datetime"]).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Find games where the scrape_datetime is the day of
    non_mistakes = df.loc[
        df["game_datetime"] == pd.to_datetime(df["scrape_datetime"]).dt.date.astype(str)
    ]
    mistakes = df[~df.index.isin(non_mistakes.index)]
    todays_date = pd.to_datetime(
        pd.to_datetime("now", utc=True)
        .tz_convert("America/Los_Angeles")
        .strftime("%Y-%m-%d")
    )
    equal_dates = df["game_datetime"] == pd.to_datetime(
        df["scrape_datetime"]
    ).dt.date.astype(str)
    # Only keep future games or games where the scrape_datetime is the day of the game
    df = df.loc[(pd.to_datetime(df["game_datetime"]) > todays_date) | equal_dates]

    # Check that we didn't exclude any games that aren't in there...
    # Kind of a dumb check since there's no date constraint, but good for quick sanity check
    # vals = []
    # for t, b in mistakes[["top_team", "bottom_team"]].values:
    #     vals.append(len(df.loc[(df["top_team"] == t) & (df["bottom_team"] == b)]))
    # assert all(v != 0 for v in vals)

    # Select latest (most recent) scrape_datetime
    df = (
        df.sort_values(by="scrape_datetime")
        .groupby(["game_datetime", "top_team", "bottom_team"])
        .last()
        .reset_index()
    )

    # Confirm no duplicates
    assert (
        len(
            df[["top_team", "bottom_team"]].loc[
                df[["top_team", "bottom_team"]].duplicated()
            ]
        )
        == 0
    )
    df = df[BOVADA_COLUMNS]

    # So at this point we've fixed the duplicate fixtures
    k = 0
    for top_team, bottom_team in df[["top_team", "bottom_team"]].values:
        srcbb_top_team = teams[top_team]["srcbb_school"]
        df.loc[k, "top_team"] = srcbb_top_team
        srcbb_bottom_team = teams[bottom_team]["srcbb_school"]
        df.loc[k, "bottom_team"] = srcbb_bottom_team
        k += 1

    return df


if __name__ == "__main__":
    # Update the teams first!
    subprocess.run(["python", os.path.join(ROOT_DIR, "ncaab/spiders/teams.py")])

    # We only need to get stats for rows that don't already have stats
    last_events_odds_path = os.path.join(
        ROOT_DIR, "ncaab/data/odds/bovada/last_events.csv"
    )
    last_events_odds_with_stats_path = os.path.join(
        ROOT_DIR, "ncaab/data/odds_with_stats/bovada/last_events.csv"
    )
    odds_df = correct_bovada_df(
        pd.read_csv(last_events_odds_path, index_col=0, dtype=str)
    )
    odds_ws_df = pd.read_csv(last_events_odds_with_stats_path, index_col=0, dtype=str)
    cols = ["game_datetime", "top_team", "bottom_team"]
    odds_inds = set(map(tuple, odds_df[cols].values.tolist()))
    odds_ws_inds = set(
        map(
            tuple,
            odds_ws_df[cols].values.tolist(),
        )
    )
    no_stats_inds = list(odds_inds - odds_ws_inds)
    df = odds_df.set_index(cols).loc[no_stats_inds].reset_index().astype(str)

    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT_DIR, "ncaab/data")) as d:
        f1 = os.path.join(d, "f1.csv")
        f2 = os.path.join(d, "f2.csv")
        df.to_csv(f1)
        process = CrawlerProcess(get_project_settings())
        process.crawl(
            SrcbbSpider,
            input_path=f1,
            output_path=f2,
            save=True,
        )
        process.start()
        new_odds_ws_df = pd.read_csv(f2, index_col=0, dtype=str)
        final_df = pd.concat([new_odds_ws_df, odds_ws_df], axis=0)
        final_df["game_datetime"] = pd.to_datetime(final_df["game_datetime"])
        final_df.sort_values(["game_datetime", "top_team"], ascending=False).astype(
            str
        ).reset_index(drop=True).to_csv(last_events_odds_with_stats_path)
