import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
import yaml
from urllib.parse import urlparse, parse_qs, urlencode
from ncaab.constants import ROOT_DIR


def retrieve_wiki_url(t):
    print(t)
    q = urlencode({"q": t + " Men's Basketball Wikipedia"})
    s = f"https://www.google.com/search?{q}"
    # print(s)
    r = requests.get(s)
    soup = BeautifulSoup(r.content, "html.parser")
    elm = "a[href*='/url?q=https://en.wikipedia.org']"
    href = [l["href"] for l in soup.select(elm)][0]
    parseable = urlparse("https://www.google.com" + href)
    wiki_link = parse_qs(parseable.query)["q"][0]
    print(t, wiki_link)


def get_team_slug(t):
    reps = [
        ("", ""),
        ("St.", "Saint"),
        ("CS", "Cal State"),
        ("St.", "St"),
    ]
    for rep in reps:
        try:
            s = t.replace(*rep)
            s = s.replace("'", "")
            s = "-".join(s.lower().split())
            v = srcbb_df.loc[srcbb_df["Slug"] == s, "Slug"]
            if len(v) >= 2:
                print(f"Failed to find team: {t}. Ambiguous slug: {s}")
                return None
            if len(v) == 1:
                return v.iloc[0]
            v = srcbb_df.loc[
                srcbb_df.apply(
                    lambda row: row.astype(str).str.contains(t).any(), axis=1
                ),
                "Slug",
            ]
            if len(v) >= 2:
                print(f"Failed to find team: {t}. Ambiguous slug: {s}")
                return None
            if len(v) == 1:
                return v.iloc[0]
        except IndexError:
            pass

    print(f"Failed to find team: {t}")
    return None


if __name__ == "__main__":
    pysbr_path = os.path.join(ROOT_DIR, "ncaab/data/pysbr_teams.yaml")
    srcbb_path = os.path.join(ROOT_DIR, "ncaab/data/srcbb_teams.csv")
    df_path = os.path.join(ROOT_DIR, "ncaab/data/bovada/last_events.csv")

    fixes = [
        ("LSU", "louisiana-state"),
        ("Texas A&M", "texas-am"),
        ("Va Commonwealth", "virginia-commonwealth"),
        ("Middle Tenn St", "middle-tennessee"),
        ("Middle Tennessee State", "middle-tennessee"),
        ("BYU", "brigham-young"),
        ("VMI", "virginia-military-institute"),
        ("SMU", "southern-methodist"),
        ("USC", "south-caroline-upstate"),
    ]

    with open(pysbr_path) as f:
        yaml_load = yaml.full_load(f)
        pysbr_df = pd.json_normalize(yaml_load["teams"])

    srcbb_df = pd.read_csv(srcbb_path, index_col=0)
    srcbb_df["Slug"] = srcbb_df["Link"].str.replace("/cbb/schools/", "").str[:-1]
    srcbb_df["Bovada Name"] = np.nan
    df = pd.read_csv(df_path, index_col=0)

    for t in srcbb_df.loc[(srcbb_df["To"] > 2010) & (srcbb_df["From"] <= 2010)][
        "School"
    ].values:
        retrieve_wiki_url(t)
    a = 1

    for t1 in df[["top_team", "bottom_team"]].values.flatten():
        slug = get_team_slug(t1)
        if slug:
            srcbb_df.loc[srcbb_df["Slug"] == slug, "Bovada Name"] = t1
    print(srcbb_df.to_string())
