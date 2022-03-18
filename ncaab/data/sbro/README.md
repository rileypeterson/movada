Reads data which I've downloaded from:

https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaabasketball/ncaabasketballoddsarchives.htm

It goes through each excel file and converts it into a standard format:

* data/sbro/ncaa basketball 2012-13.xlsx
* data/sbro/ncaa basketball 2013-14.xlsx  
.  
.  
.



```
    game_date     top_team  top_final  bottom_final bottom_team  top_spread  top_spread_odds  top_ml_odds  top_total  top_total_odds  bottom_spread  bottom_spread_odds  bottom_ml_odds  bottom_total  bottom_total_odds
0  2022-03-09    SetonHall         57            53  Georgetown        -9.5             -110         -700      142.0            -110            9.5                -110             500         142.0               -110
1  2022-03-09       Nevada         79            72   NewMexico        -6.0             -110         -195      151.5            -110            6.0                -110             165         151.5               -110
2  2022-03-09     St.Johns         92            73      Depaul        -4.5             -110         -210      156.0            -110            4.5                -110             175         156.0               -110
3  2022-03-09       Xavier         82            89      Butler        -6.5             -110         -225      131.5            -110            6.5                -110             185         131.5               -110
4  2022-03-09  WashingtonU         82            70       UtahU        -2.5             -110         -120      140.5            -110            2.5                -110             100         140.5               -110
```

