"""
Takes any team name and finds the correct ncaa team
"""
import re


def sanitize_team(team):
    team = re.sub("[^a-zA-Z,-.&']+", " ", team)
    team = team.strip()
    return team


def sanitize_odds(odds):
    team = re.sub("[^0-9a-zA-Z,-.+']+", "", odds)
    return team
