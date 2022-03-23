import pandas as pd
import os
from ncaab.constants import ROOT_DIR
from ncaab.utils.teams import teams
import time
import random

skips = [
    "Chaminade",
    "AlaskaAnchorage",
    "ConcordiaSt.Paul",
    "TXPanAmerican",
    "Texas-PanAmerican",
]

if __name__ == "__main__":
    sbro_path = os.path.join(ROOT_DIR, "ncaab/data/sbro/ncaab_history_init.csv")
    past_path = os.path.join(ROOT_DIR, "ncaab/data/sbro/past_events.csv")
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
        # for tt, ttt in replacements:
        #     if top_team == tt:
        #         top_team = ttt
        #     if bottom_team == tt:
        #         bottom_team = ttt
        sbro_df.loc[i, "top_team"] = teams[top_team]["srcbb_school"]
        print(bottom_team)
        sbro_df.loc[i, "bottom_team"] = teams[bottom_team]["srcbb_school"]
    sbro_df.to_csv(past_path)
