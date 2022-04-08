import os
import pandas as pd
from ncaab.constants import ROOT_DIR

if __name__ == "__main__":
    past_df = pd.read_csv(
        os.path.join(ROOT_DIR, "ncaab/data/odds_with_stats/sbro/past_events.csv"),
        index_col=0,
        dtype=str,
    )
    last_df = pd.read_csv(
        os.path.join(ROOT_DIR, "ncaab/data/odds_with_stats/bovada/last_events.csv"),
        index_col=0,
        dtype=str,
    )
    df = (
        pd.concat([last_df, past_df], axis=0)
        .sort_values(["game_datetime", "top_team"], ascending=False)
        .reset_index(drop=True)
    )
    dataset_path = os.path.join(ROOT_DIR, "ncaab/data/dataset.csv")
    df.to_csv(dataset_path)
