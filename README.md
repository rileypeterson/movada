# Introduction

TODO

# Sports Database Queries
* [Team Average Points Scored/Surrendered in their last 3 games](https://sportsdatabase.com/nba/query?output=default&sdql=date%2C+1*round%28A%28points%2C+N%3D3%29%2C+2%29%2C+1*round%28A%28o%3Apoints%2C+N%3D3%29%2C+2%29+%40+team+and+season%3E2005&submit=++S+D+Q+L+%21++)

# Resources
* https://www.nbastuffer.com/analytics101/four-factors/
* https://kenpom.com/blog/national-efficiency/

# Goal
* My goal is to use past performance between two teams to predict the expected return of an O/U or spread bet in an upcoming match up.
* Said differently, we want a function `P` which takes features from previous games of team 1 `X1(n-1, n-2, ...)` and team 2 `X2(n-1, n-2, ...)` and predicts the probability of a specific outcome, e.g.: `P(s1=34, s2=30 | X1(n-1, n-2, ...) & X2(n-1, n-2, ...)) = 0.07`

# Setup
1. Start mysql and django:
    ```
    cd database/mysql
    docker-compose up --build -d
    ```
2. Enter active container (either mysql or django/web):
    ```
    docker exec -it `docker ps | awk 'FNR == 2 {print $1}'` /bin/bash
    ```
3. Make migrations:
    ```
    python manage.py makemigrations sports_app
    python manage.py migrate
    ```
4. Run scraper:
    ```
    cd espn
    scrapy crawl nfl
    ```
5. Sample query:
    ```
    select game.id, team.name, team_game_stat_type.stat, value as score from game
    join team_game_stat on team_game_stat.game_id = game.id
    join team on team_game_stat.team_id = team.id
    join team_game_stat_type on team_game_stat_type.id = team_game_stat.type_id
    where team_game_stat_type.stat like "%score"
    ```
   Gives:
   ![image](https://user-images.githubusercontent.com/29719483/136532863-d655e02b-95de-475a-8600-80ef361c0c24.png)

# Other nice commands
```
# Nuke db
python manage.py reset_db
# Truncate db
python manage.py flush
# Stop containers
docker-compose down

# When using inspect_response you can do this to use self essentially
home_team_obj, away_team_obj = spider.parse_teams(response)

```

### Websites
* https://www.oddsportal.com/basketball/usa/ncaa-2016-2017/ohio-bobcats-kent-state-GE3ZgmWp/#ah;1
* https://www.sportsbookreview.com/betting-odds/ncaa-basketball/matchups/?date=20170310
* https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaabasketball/ncaabasketballoddsarchives.htm


# Thoughts
1. Github action (which runs every hour) initiates movada pipeline
2. Goes to bovada and consumes all the upcoming fixtures (including lines and spreads). Uploads to github.
3. For each team get the data from their previous 7 non-preseason games (recurse) including historical odds. 
4. Also get the odds data from [here](https://github.com/JeMorriso/PySBR).
5. Post to dataframe in repo on github. 