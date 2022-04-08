import os
import pandas as pd
from ncaab.constants import ROOT_DIR, BOVADA_COLUMNS
from ncaab.utils.teams import teams
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ncaab.spiders.srcbb import SrcbbSpider
import subprocess


def convert_dt_to_pst(s):
    return pd.to_datetime(s, utc=True).dt.tz_convert("America/Los_Angeles")


if __name__ == "__main__":
    # Update the teams first!
    subprocess.run(["python", os.path.join(ROOT_DIR, "ncaab/spiders/teams.py")])

    last_events_path = os.path.join(ROOT_DIR, "ncaab/data/odds/bovada/last_events.csv")
    df = pd.read_csv(last_events_path, index_col=0, dtype=str)

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
        print(top_team, bottom_team)
        srcbb_top_team = teams[top_team]["srcbb_school"]
        df.loc[k, "top_team"] = srcbb_top_team
        srcbb_bottom_team = teams[bottom_team]["srcbb_school"]
        df.loc[k, "bottom_team"] = srcbb_bottom_team
        k += 1

    path = os.path.join(ROOT_DIR, "ncaab/data/tmp/temp_df.csv")
    df.to_csv(path)

    process = CrawlerProcess(get_project_settings())
    process.crawl(
        SrcbbSpider,
        input_path="ncaab/data/tmp/temp_df.csv",
        output_path="ncaab/data/odds_with_stats/bovada/last_events.csv",
        save=True,
    )
    process.start()
