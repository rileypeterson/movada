from django.db import models


class Sport(models.Model):
    # Football, Soccer, Basketball, Baseball, etc.
    name = models.CharField(max_length=30)
    is_team_sport = models.BooleanField()


class League(models.Model):
    # NFL, NCAAFB, EPL, La Liga, Ligue 1, NBA, WNBA, MLB, etc.
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)


class Team(models.Model):
    # Tennessee Titans, Manchester United, Memphis Grizzlies, Cleveland Indians
    name = models.CharField(max_length=50)


class Player(models.Model):
    name = models.CharField(max_length=50)


class Competitor(models.Model):
    # A team or a player
    pass


class Game(models.Model):
    # A game is an event between just two teams
    # Football game, baseball game, soccer game
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE)


class Event(models.Model):
    # An event is either a game, a contest, or a match
    pass


class Contest(models.Model):
    # A contest is an event between multiple competitors
    pass


class Match(models.Model):
    # A match is an event between just two players
    pass
