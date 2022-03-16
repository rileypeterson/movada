from django.db import models


class Webpage(models.Model):
    class Meta:
        db_table = "webpage"

    url = models.CharField(max_length=255, primary_key=True)
    body = models.TextField()


class Sport(models.Model):
    class Meta:
        db_table = "sport"

    # Football, Soccer, Basketball, Baseball, etc.
    name = models.CharField(max_length=30, unique=True)
    # is_team_sport = models.BooleanField()


class League(models.Model):
    class Meta:
        db_table = "league"

    # NFL, NCAAFB, EPL, La Liga, Ligue 1, NBA, WNBA, MLB, etc.
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, unique=True)


class Team(models.Model):
    class Meta:
        db_table = "team"

    # Tennessee Titans, Manchester United, Memphis Grizzlies, Cleveland Indians
    abbrev = models.CharField(max_length=50)
    full_name = models.CharField(max_length=50)
    # Really "location"
    city = models.CharField(max_length=50)
    name = models.CharField(max_length=50)


class Player(models.Model):
    class Meta:
        db_table = "player"

    name = models.CharField(max_length=50)


class Venue(models.Model):
    class Meta:
        db_table = "venue"

    name = models.CharField(max_length=30)


class Game(models.Model):
    class Meta:
        db_table = "game"

    # A game is an event between just two teams
    # Football game, baseball game, soccer game
    team1 = models.ForeignKey(Team, related_name="team1", on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name="team2", on_delete=models.CASCADE)
    game_type = models.CharField(max_length=30)
    datetime = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)


class NflPlay(models.Model):
    class Meta:
        db_table = "nfl_play"

    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    offensive_team_id = models.ForeignKey(
        Team, related_name="offensive_team", on_delete=models.CASCADE
    )
    defensive_team_id = models.ForeignKey(
        Team, related_name="defensive_team", on_delete=models.CASCADE
    )
    description = models.TextField()
