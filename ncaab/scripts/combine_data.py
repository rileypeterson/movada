import os
import pandas as pd
from ncaab.constants import ROOT_DIR

if __name__ == "__main__":
    past_df = pd.read_csv(
        os.path.join(ROOT_DIR, "ncaab/data/odds_with_stats/sbro/past_events.csv"),
        index_col=0,
    )
    last_df = pd.read_csv(
        os.path.join(ROOT_DIR, "ncaab/data/odds_with_stats/bovada/last_events.csv"),
        index_col=0,
    )
    df = (
        pd.concat([last_df, past_df], axis=0)
        .sort_values("game_datetime", ascending=False)
        .reset_index(drop=True)
    )

    # to csv dtype str
    a = 1
