# Introduction
Compile publicly available sports data.

# Websites
* https://www.nbastuffer.com/analytics101/four-factors/
* https://kenpom.com/blog/national-efficiency/
* https://www.oddsportal.com/basketball/usa/ncaa-2016-2017/ohio-bobcats-kent-state-GE3ZgmWp/#ah;1
* https://www.sportsbookreview.com/betting-odds/ncaa-basketball/matchups/?date=20170310
* https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaabasketball/ncaabasketballoddsarchives.htm

# Goals
* [x] Github action (which runs every hour) initiates movada pipeline.
* [x] Goes to bovada and consumes all the upcoming ncaab fixtures (including lines and spreads). [Uploads to Github](https://github.com/rileypeterson/movada/blob/main/ncaab/data/bovada/next_events.csv).
* [x] Synchronize next events into historical data, once they pass. [Uploads to Github](https://github.com/rileypeterson/movada/blob/main/ncaab/data/bovada/last_events.csv).
* [ ] For each team get the stats from their previous 7 non-preseason games (recurse) including historical odds. 

# Set PYTHONPATH (run before running `pytest`)
```commandline
PYTHONPATH="`pwd`:$PYTHONPATH"
export PYTHONPATH
```