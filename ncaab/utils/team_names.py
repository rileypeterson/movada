"""
Takes any team name and finds the correct ncaa team
"""
import re
from pysbr import NCAAB
from thefuzz import process

ncaab = NCAAB()
teams = ncaab._league["teams"]
d = dict()
for i, t in enumerate(teams):
    d[t["team id"]] = {
        "sbr abbreviation": t["sbr abbreviation"],
        "abbreviation": t["abbreviation"],
        "conference name": t["conference name"],
        "division name": t["division name"],
        "location": t["location"],
        "name": t["name"],
        "nickname": t["nickname"],
    }
teams = d.copy()


def resolve_team(term):
    # print("Trying:", term)
    og_term = term
    # Sanitize: Only allow actual letters
    term = re.sub(r"(\w.)([A-Z])", r"\1 \2", term)
    term = re.sub("[^a-zA-Z,-.&']+", " ", term)
    term = term.lower().strip()
    all_teams = []
    possibilities = []
    for k, v in ncaab._team_ids.items():
        if og_term in v:
            possibilities.append(teams[v[og_term]])
        elif term in v:
            possibilities.append(teams[v[term]])
            # return teams[v[term]]
        all_teams += list(v.keys())
    if possibilities:
        return possibilities
    # print(f"Original: {og_term}, Converted: {term}")
    return resolve_team(process.extractOne(term, all_teams)[0])


a = 1
