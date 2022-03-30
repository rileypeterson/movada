import os
import pandas as pd
from ncaab.constants import ROOT_DIR
from ncaab.utils.teams import teams


def convert_dt_to_pst(s):
    return pd.to_datetime(s, utc=True).dt.tz_convert("America/Los_Angeles")


if __name__ == "__main__":
    last_events_path = os.path.join(ROOT_DIR, "ncaab/data/bovada/last_events.csv")
    df = pd.read_csv(last_events_path, index_col=0, dtype=str)

    # Convert the times to PST and make the game_datetime a date
    df["game_datetime"] = convert_dt_to_pst(df["game_datetime"]).dt.strftime("%Y-%m-%d")
    df["scrape_datetime"] = convert_dt_to_pst(df["scrape_datetime"]).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    df.loc[
        df["game_datetime"] == pd.to_datetime(df["scrape_datetime"]).dt.date.astype(str)
    ]
    a = 1
