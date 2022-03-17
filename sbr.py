from pysbr import NCAAB, Sportsbook, EventsByParticipants
from thefuzz import process

ncaab = NCAAB()
sb = Sportsbook()
teams = list(ncaab._team_ids["name"].keys())


def team_name_to_id(name):
    name = name.lower()
    try:
        return ncaab.team_id(name)
    except ValueError:
        # TODO: Check score here ?
        sbr_name = process.extractOne(name, teams)[0]
        return ncaab.team_id(sbr_name)
