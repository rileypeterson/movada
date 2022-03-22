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
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, parse_qs, urlencode
from ncaab.constants import ROOT_DIR
import atexit
import pickle


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
                wiki_url = retrieve_wiki_url(item)
                try:
                    # New search term
                    r = self.__getitem__(wiki_url)
                    self.teams[item] = {"wiki_url": wiki_url}
                    if item not in self.teams[wiki_url]["aliases"]:
                        self.teams[wiki_url]["aliases"].append(item)
                    return r
                except KeyError:
                    # Completely new team (no srcbb entry)
                    self.teams[item] = {"wiki_url": wiki_url}
                    self.teams[wiki_url] = {"aliases": [item]}
                    return self.__getitem__(item)

    def as_dict(self):
        return self.teams


def retrieve_wiki_url(t):
    print(f"Searching for {t}")
    q = urlencode({"q": t + " Men's Basketball Wikipedia"})
    s = f"https://www.google.com/search?{q}"
    r = requests.get(s)
    soup = BeautifulSoup(r.content, "html.parser")
    elm = "a[href*='/url?q=https://en.wikipedia.org']"
    href = [l["href"] for l in soup.select(elm)][0]
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


if __name__ == "__main__":
    srcbb_path = os.path.join(ROOT_DIR, "ncaab/data/srcbb_teams.csv")
    df_path = os.path.join(ROOT_DIR, "ncaab/data/bovada/last_events.csv")

    # srcbb_df = pd.read_csv(srcbb_path, index_col=0)
    # srcbb_df["Slug"] = srcbb_df["Link"].str.replace("/cbb/schools/", "").str[:-1]
    # srcbb_df["Bovada Name"] = np.nan
    # df = pd.read_csv(df_path, index_col=0)

    # for t, slug in srcbb_df.loc[(srcbb_df["To"] > 2010) & (srcbb_df["From"] <= 2010)][
    #     ["School", "Slug"]
    # ].values:
    #     print(t)
    #     teams[t]["srcbb_school"] = t
    #     teams[t]["srcbb_slug"] = slug
