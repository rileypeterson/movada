import os
import pandas as pd
from ncaab.constants import ROOT_DIR


def gen_idx(df):
    idx = (
        pd.to_datetime(df["game_datetime"]).dt.strftime("%Y-%m-%d")
        + df["top_team"].astype(str)
        + df["bottom_team"].astype(str)
    )
    idx = idx.apply(lambda s: "".join(sorted([i for i in list(s)])).strip())
    df["idx"] = idx
    df.set_index("idx", drop=True, inplace=True)
    return df


if __name__ == "__main__":
    next_events_file = os.path.join(ROOT_DIR, "ncaab/data/odds/bovada/next_events.csv")
    last_events_file = os.path.join(ROOT_DIR, "ncaab/data/odds/bovada/last_events.csv")
    df_next = pd.read_csv(next_events_file, index_col=0, dtype=str)
    df_last = pd.read_csv(last_events_file, index_col=0, dtype=str)

    # Make an index
    # There's a method to my madness
    # We do this so that should the underdog change, we would still join correctly
    df_next = gen_idx(df_next)
    df_last = gen_idx(df_last)

    df_last_copy = df_last.copy()
    df_last.update(df_next)

    # Append new rows not seen in df_last
    df = pd.concat([df_next[~df_next.index.isin(df_last.index)], df_last], axis=0)
    df = df.reset_index(drop=True)
    df["game_datetime"] = pd.to_datetime(df["game_datetime"])
    df["scrape_datetime"] = pd.to_datetime(df["scrape_datetime"])

    # A little worried about this because bovada datetime are notoriously weird
    df = df.sort_values(by=["game_datetime", "scrape_datetime"])
    df["game_datetime"] = df["game_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["scrape_datetime"] = df["scrape_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Safety check so I don't accidentally upload something too large
    if len(df) >= 10000:
        raise ValueError("DataFrame too large!!")

    # All dtypes are object, write output to last_events.csv
    output_file = os.path.join(ROOT_DIR, "ncaab/data/odds/bovada/last_events.csv")
    df.to_csv(output_file)
