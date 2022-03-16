"""
Scrape available nfl stats from ESPN.

"""
import scrapy


class NFLSpider(scrapy.Spider):
    name = "nfl"
    start_urls = [
        "https://www.espn.com/nfl/schedule",
    ]

    def parse(self, response):
        # Start at: https://www.espn.com/nfl/schedule
        # Yield links to: https://www.espn.com/nfl/schedule/_/year/20XX links
        links = response.css('li[data-type="year"]>a::attr(href)').extract()
        for link in links:
            yield response.follow(link, self.parse_weeks)
            break

    def parse_weeks(self, response):
        # Start at: https://www.espn.com/nfl/schedule/_/year/20XX
        # Yield links to: https://www.espn.com/nfl/schedule/_/week/Y/year/20XX/seasontype/2
        week_links = response.css(
            'li[data-type="week"][data-season="reg"]>a::attr(href)'
        ).extract()
        for week_link in week_links:
            yield response.follow(week_link, self.parse_games)
            break

    def parse_games(self, response):
        # Start at: https://www.espn.com/nfl/schedule/_/week/Y/year/20XX/seasontype/2
        # Yield links to: https://www.espn.com/nfl/game/_/gameId/ZZZZZZZZZ
        game_links = response.css(
            'td a[name="&lpos=nfl:schedule:score"]::attr(href)'
        ).extract()
        for game_link in game_links:
            yield response.follow(game_link, self.parse_gamecast)
            break

    def parse_gamecast(self, response):
        top_scorebox = response.css("#gamepackage-matchup-wrap > header > div")
        away_team_info = top_scorebox.css(
            "div.team.away > div > div.team-container > div.team-info"
        )
        away_long_name = away_team_info.css(
            "div.team-info-wrapper > a > span.long-name::text"
        ).extract_first()
        away_short_name = away_team_info.css(
            "div.team-info-wrapper > a > span.short-name::text"
        ).extract_first()
        away_abbrev_name = away_team_info.css(
            "div.team-info-wrapper > a > span.abbrev::text"
        ).extract_first()
        print(away_long_name, away_short_name)
