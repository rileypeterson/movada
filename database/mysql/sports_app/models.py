from django.db import models


class Webpage(models.Model):
    url = models.CharField(max_length=255, primary_key=True)
    body = models.TextField()


class Sport(models.Model):
    # Football, Soccer, Basketball, Baseball, etc.
    name = models.CharField(max_length=30)
    # is_team_sport = models.BooleanField()


class League(models.Model):
    # NFL, NCAAFB, EPL, La Liga, Ligue 1, NBA, WNBA, MLB, etc.
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)


class Team(models.Model):
    # Tennessee Titans, Manchester United, Memphis Grizzlies, Cleveland Indians
    name = models.CharField(max_length=50)


class Player(models.Model):
    name = models.CharField(max_length=50)


class GameType(models.Model):
    name = models.CharField(max_length=30)


class Venue(models.Model):
    name = models.CharField(max_length=30)


class Game(models.Model):
    # A game is an event between just two teams
    # Football game, baseball game, soccer game
    team1 = models.ForeignKey(Team, related_name="team1", on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name="team2", on_delete=models.CASCADE)
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)


class StatSubCategory(models.Model):
    # Passing, Rushing, Receiving, etc.
    sub_category = models.CharField(max_length=30)


class StatCategory(models.Model):
    # Offensive, Defensive, Special Teams, etc.
    category = models.CharField(max_length=30)


class PlayerGameStatType(models.Model):
    full_name = models.CharField(max_length=50)
    stat = models.CharField(max_length=10)  # Abbreviation of stat name
    category = models.ForeignKey(StatCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(StatSubCategory, on_delete=models.CASCADE)


class PlayerGameStat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    type = models.ForeignKey(PlayerGameStatType, on_delete=models.CASCADE)
    value = models.FloatField()
