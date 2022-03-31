"""
Looks like:
teams = {
    "VMI": {"wiki_url": "https://en.wikipedia.org/wiki/VMI_Keydets_basketball"},
    "https://en.wikipedia.org/wiki/VMI_Keydets_basketball": {
        "aliases": ["VMI"],
        "srcbb_school": "Virginia Military Institute Keydets",
        "srcbb_slug": "virginia-military-institute",
    },
}
"""
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, parse_qs, urlencode
from ncaab.constants import ROOT_DIR
import atexit
import signal
import pickle
import time
import random
from requests_html import HTMLSession

session = HTMLSession()


class Teams(object):
    def __init__(self, teams):
        self.teams = teams

    def __getitem__(self, item):
        if item.startswith("https://en.wikipedia.org"):
            # We always end up here eventually
            assert self.teams[item]["srcbb_school"], "No srcbb_school"
            assert self.teams[item]["srcbb_slug"], "No srcbb_slug"
            return self.teams[item]
        else:
            try:
                # Recognized search term
                return self.teams[self.teams[item]["wiki_url"]]
            except KeyError:
                raise NotImplementedError("Use spider")
                wiki_url = retrieve_wiki_url(item)
                try:
                    # New search term
                    r = self.__getitem__(wiki_url)
                    self.teams[item] = {"wiki_url": wiki_url}
                    if item not in self.teams[wiki_url]["aliases"]:
                        self.teams[wiki_url]["aliases"].append(item)
                    return r
                except KeyError:
                    raise ValueError(f"Unrecognized team: {item}")
                    # Completely new team (no srcbb entry)
                    # self.teams[item] = {"wiki_url": wiki_url}
                    # self.teams[wiki_url] = {"aliases": [item]}
                    # return self.__getitem__(item)

    def as_dict(self):
        return self.teams

    def fix(self, team, alias):
        correct_wiki = self.teams[alias]["wiki_url"]
        self.remove(team)
        self.teams[team] = {}
        self.teams[team]["wiki_url"] = correct_wiki
        if team not in self.teams[self.teams[team]["wiki_url"]]["aliases"]:
            self.teams[self.teams[team]["wiki_url"]]["aliases"].append(team)

    def clean(self):
        j = 0
        for k, v in self.teams.items():
            # print(k, v)
            aliases = v.get("aliases", None)
            if aliases:
                print(j, aliases)
                j += 1

    def remove(self, team):
        try:
            print(f"Removing {team}")
            self.teams[self.teams[team]["wiki_url"]]["aliases"] = [
                t
                for t in self.teams[self.teams[team]["wiki_url"]]["aliases"]
                if t != team
            ]
            del self.teams[team]
        except KeyError:
            print(f"Already removed {team}")


def retrieve_wiki_url(t):
    # TODO: Fix me
    time.sleep(random.random() * 15)
    print(f"Searching for {t}")
    q = urlencode({"q": t + " Men's Basketball Wikipedia"})
    s = f"https://www.google.com/search?{q}"
    r = requests.get(s)
    soup = BeautifulSoup(r.content, "html.parser")
    elm = "a[href*='/url?q=https://en.wikipedia.org']"
    try:
        href = [l["href"] for l in soup.select(elm)][0]
    except IndexError as e:
        print(soup)
        raise e
    parseable = urlparse("https://www.google.com" + href)
    wiki_link = parse_qs(parseable.query)["q"][0]
    return wiki_link


def save_teams():
    with open(teams_path, "wb") as f:
        pickle.dump(teams.as_dict(), f)


teams_path = os.path.join(ROOT_DIR, "ncaab/data/teams.pkl")
with open(teams_path, "rb") as f:
    teams = pickle.load(f)
teams = Teams(teams)


atexit.register(save_teams)
signal.signal(signal.SIGTERM, save_teams)
signal.signal(signal.SIGINT, save_teams)


if __name__ == "__main__":
    # Note "zzzzNDakotaSt" was linked to teams["Providence Friars"] somehow
    # teams.fix("AlabamaAM", "Alabama A&M Bulldogs")
    # teams.fix("ArkansasLR", "ArkansasLittleRock")
    # teams.fix("CalSantaBarb", "UC Santa Barbara Gauchos")
    # teams.fix("SoCarolinaSt", "South Carolina State Bulldogs")
    # teams.fix("FloridaAM", "Florida A&M Rattlers")
    #
    # teams.fix("NoIllinois", "Northern Illinois Huskies")
    # teams.fix("SoIllinois", "Southern Illinois Salukis")
    # teams.fix("JacksonvilleSt", "Jacksonville State Gamecocks")
    # teams.fix("MississippiSt", "Mississippi State Bulldogs")
    # teams.fix("MissouriSt", "Missouri State Bears")
    # teams.fix("NorthCarolinaAT", "North Carolina A&T Aggies")
    # teams.fix("N.CarolinaAT", "North Carolina A&T Aggies")
    # teams.fix("NorthwesternSt", "Northwestern State Demons")
    # teams.fix("TennesseeChat", "Chattanooga Mocs")
    # teams.fix("ETennesseeSt", "East Tennessee State Buccaneers")
    # teams.fix("SouthDakotaSt", "South Dakota State Jackrabbits")
    #
    # teams.remove("Chaminade")
    # teams.remove("AlaskaAnchorage")
    # teams.remove("ConcordiaSt.Paul")
    # teams.remove("TXPanAmerican")
    # teams.remove("Texas-PanAmerican")

    teams.clean()

    # teams.remove("zzzzNDakotaSt")
    # srcbb_path = os.path.join(ROOT_DIR, "ncaab/data/srcbb_teams.csv")
    # df_path = os.path.join(ROOT_DIR, "ncaab/data/bovada/last_events.csv")
    #
    # # retrieve_wiki_url("StThomas")
    #
    # srcbb_df = pd.read_csv(srcbb_path, index_col=0)
    # srcbb_df["Slug"] = srcbb_df["Link"].str.replace("/cbb/schools/", "").str[:-1]
    # srcbb_df["Bovada Name"] = np.nan
    # df = pd.read_csv(df_path, index_col=0)
    #
    # for t, slug in srcbb_df.loc[(srcbb_df["To"] > 2010)][["School", "Slug"]].values:
    #     print(teams[t])
    #     teams[t]["srcbb_school"] = t
    #     teams[t]["srcbb_slug"] = slug
