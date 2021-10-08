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
    name = models.CharField(max_length=50)


class Player(models.Model):
    class Meta:
        db_table = "player"

    name = models.CharField(max_length=50)


class GameType(models.Model):
    class Meta:
        db_table = "game_type"

    name = models.CharField(max_length=30)


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
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)


class StatSubCategory(models.Model):
    class Meta:
        db_table = "stat_sub_category"

    # Passing, Rushing, Receiving, etc.
    sub_category = models.CharField(max_length=30)


class StatCategory(models.Model):
    class Meta:
        db_table = "stat_category"

    # Offensive, Defensive, Special Teams, etc.
    category = models.CharField(max_length=30)


class PlayerGameStatType(models.Model):
    class Meta:
        db_table = "player_game_stat_type"

    full_name = models.CharField(max_length=50)
    stat = models.CharField(max_length=10)  # Abbreviation of stat name
    category = models.ForeignKey(StatCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(StatSubCategory, on_delete=models.CASCADE)


class PlayerGameStat(models.Model):
    class Meta:
        db_table = "player_game_stat"

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    type = models.ForeignKey(PlayerGameStatType, on_delete=models.CASCADE)
    value = models.FloatField()


class TeamGameStatType(models.Model):
    class Meta:
        db_table = "team_game_stat_type"

    full_name = models.CharField(max_length=50)
    stat = models.CharField(max_length=10)  # Abbreviation of stat name
    category = models.ForeignKey(StatCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(StatSubCategory, on_delete=models.CASCADE)


class TeamGameStat(models.Model):
    class Meta:
        db_table = "team_game_stat"

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    type = models.ForeignKey(TeamGameStatType, on_delete=models.CASCADE)
    value = models.FloatField()
