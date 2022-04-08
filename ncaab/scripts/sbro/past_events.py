import pandas as pd
import os
from ncaab.constants import ROOT_DIR
from ncaab.utils.teams import teams

skips = [
    "Chaminade",
    "AlaskaAnchorage",
    "ConcordiaSt.Paul",
    "TXPanAmerican",
    "Texas-PanAmerican",
]

if __name__ == "__main__":
    sbro_path = os.path.join(ROOT_DIR, "ncaab/data/odds/sbro/ncaab_history_init.csv")
    past_path = os.path.join(ROOT_DIR, "ncaab/data/odds/sbro/past_events.csv")
    sbro_df = pd.read_csv(sbro_path)
    for i in range(len(sbro_df)):
        top_team = sbro_df.loc[i, "top_team"]
        bottom_team = sbro_df.loc[i, "bottom_team"]
        c = False
        for skip in skips:
            if top_team == skip or bottom_team == skip:
                c = True
        if c:
            continue
        sbro_df.loc[i, "top_team"] = teams[top_team]["srcbb_school"]
        sbro_df.loc[i, "bottom_team"] = teams[bottom_team]["srcbb_school"]
    sbro_df.to_csv(past_path)
