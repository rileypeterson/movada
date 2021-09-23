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