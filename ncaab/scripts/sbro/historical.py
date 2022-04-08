"""
See README.md

"""
import pandas as pd
import glob
import os
import pathlib
import numpy as np
from ncaab.constants import BOVADA_COLUMNS, ROOT_DIR


if __name__ == "__main__":
    dir_path = pathlib.Path(
        os.path.dirname(
            os.path.join(ROOT_DIR, "ncaab/data/odds/sbro/ncaa basketball 2012-13.xlsx")
        )
    )
    pat = os.path.join(dir_path, "ncaa basketball 20??-??.xlsx")
    files = sorted(glob.glob(pat))[::-1]
    dfs = []

    for file in files:
        # Get correct date
        start_year, end_year = (
            pathlib.Path(file).parts[-1].split(" ")[-1].split(".")[0][2:].split("-")
        )
        start_year = "20" + start_year
        end_year = "20" + end_year

        # Read raw file
        df = pd.read_excel(file, usecols="A:K")
        cols = ["Date", "Team", "Final", "Close", "ML"]
        df = df.loc[:, cols]

        # Fix the date
        df["Date"] = df["Date"].apply(lambda x: "{:0>4d}".format(x))
        # If date greater than August 1st it must be the start year, else the end year
        df["Date"] = np.where(
            df["Date"].astype(int) > 800,
            start_year + df["Date"],
            end_year + df["Date"],
        )
        df["Date"] = pd.to_datetime(df["Date"], infer_datetime_format=True)

        # Flatten
        even_df = df.iloc[df.index % 2 == 0]
        odd_df = df.iloc[df.index % 2 != 0]
        odd_df = odd_df.drop(columns=["Date"])
        odd_df.columns = [f"bottom_{c}".lower() for c in odd_df.columns]
        even_df.columns = ["game_date"] + [
            f"top_{c}".lower() for c in even_df.columns[1:]
        ]
        df = pd.concat(
            [even_df.reset_index(drop=True), odd_df.reset_index(drop=True)], axis=1
        )

        # Fix NaNs
        df["bottom_ml"] = df["bottom_ml"].replace({"NL": np.nan, "-": np.nan})
        df["top_ml"] = df["top_ml"].replace({"NL": np.nan, "-": np.nan})
        df = df.dropna()
        df["bottom_ml"] = df["bottom_ml"].astype(int)
        df["top_ml"] = df["top_ml"].astype(int)

        # Put favorite on left side
        top_df = df[[c for c in df.columns if "top_" in c]]
        bottom_df = df[[c for c in df.columns if "bottom_" in c]]
        top_copy = top_df.copy()

        # Moneyline
        top_df = top_df.where(
            top_df["top_ml"] < bottom_df["bottom_ml"], other=bottom_df.values
        )
        bottom_df = bottom_df.where(
            top_copy["top_ml"] < bottom_df["bottom_ml"], top_copy.values
        )
        df = pd.concat([df[["game_date"]], top_df, bottom_df], axis=1)

        # Total
        df["bottom_close"] = df["bottom_close"].replace({"pk": 0.0, "PK": 0.0})
        df["top_close"] = df["top_close"].replace({"pk": 0.0, "PK": 0.0})
        df["bottom_close"] = df["bottom_close"].replace({"NL": np.nan})
        df["top_close"] = df["top_close"].replace({"NL": np.nan})
        df = df.dropna()
        df["top_total"] = df[["top_close", "bottom_close"]].max(axis=1)
        df["bottom_total"] = df[["top_close", "bottom_close"]].max(axis=1)
        # Assume odds were -110 each side...
        df["top_total_odds"] = -110
        df["bottom_total_odds"] = -110

        # Spread
        df["top_spread"] = -df["top_close"]
        df["bottom_spread"] = df["top_close"]
        # Assume odds were -110 each side...
        df["top_spread_odds"] = -110
        df["bottom_spread_odds"] = -110

        final_cols = [
            "game_date",
            "top_team",
            "top_final",
            "bottom_final",
            "bottom_team",
            "top_spread",
            "top_spread_odds",
            "top_ml",
            "top_total",
            "top_total_odds",
            "bottom_spread",
            "bottom_spread_odds",
            "bottom_ml",
            "bottom_total",
            "bottom_total_odds",
        ]
        df = df[final_cols]
        df = df.rename(columns={"top_ml": "top_ml_odds", "bottom_ml": "bottom_ml_odds"})
        # print(f"Making {file.replace('.xlsx', '.df')}")
        # df.to_pickle(file.replace(".xlsx", ".df"))
        dfs.append(df)
    master_df = pd.concat(dfs, axis=0)
    master_df.sort_values(by="game_date", ascending=False, inplace=True)
    master_df["scrape_datetime"] = master_df["game_date"].values[0]
    master_df.rename(columns={"game_date": "game_datetime"}, inplace=True)
    master_df = master_df[BOVADA_COLUMNS]
    master_df.to_csv(
        os.path.join(ROOT_DIR, "ncaab/data/odds/sbro/ncaab_history_init.csv"),
        index=False,
    )
