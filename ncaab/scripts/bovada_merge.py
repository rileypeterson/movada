import os
import pandas as pd
from ncaab.utils.team_names import sanitize_team


def gen_idx(df):
    idx = (
        df["game_date"].astype(str)
        + df["top_team"].astype(str)
        + df["bottom_team"].astype(str)
    )
    idx = idx.apply(lambda s: "".join(sorted([i for i in list(s)])).strip())
    df["idx"] = idx
    df.set_index("idx", drop=True, inplace=True)
    return df


if __name__ == "__main__":
    data_folder = os.path.dirname(__file__)
    data_folder = os.path.dirname(data_folder)
    data_folder = os.path.join(data_folder, "data", "bovada")
    df_next = pd.read_csv(os.path.join(data_folder, "next_events.csv"), index_col=0)

    df_last = pd.read_csv(os.path.join(data_folder, "last_events.csv"), index_col=0)

    # TODO: REMOVE ME
    df_next.top_team = [sanitize_team(t) for t in df_next.top_team]
    df_next.bottom_team = [sanitize_team(t) for t in df_next.bottom_team]
    df_last.top_team = [sanitize_team(t) for t in df_last.top_team]
    df_last.bottom_team = [sanitize_team(t) for t in df_last.bottom_team]

    # Make an index
    # There's a method to my madness
    # We do this so that should the underdog change, we would still join correctly
    df_next = gen_idx(df_next)
    df_last = gen_idx(df_last)

    df_last_copy = df_last.copy()
    df_last.update(df_next)

    # Append new rows not seen in df_last
    df = pd.concat([df_next[~df_next.index.isin(df_last.index)], df_last], axis=0)
