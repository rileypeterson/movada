"""
Scrape available nfl stats from ESPN.

"""
import pandas as pd
import scrapy
from sports_app.models import (
    Team,
    Venue,
    GameType,
    Game,
    StatCategory,
    StatSubCategory,
    TeamGameStatType,
    TeamGameStat,
)


class NFLSpider(scrapy.Spider):
    name = "nfl"
    start_urls = [
        "https://www.espn.com/nfl/schedule",
    ]

    def parse(self, response):
        print(self.settings.get("CONCURRENT_REQUESTS"))
        year_links = response.css('li[data-type="year"]').css("a::attr(href)").extract()
        for year_link in year_links[::-1]:
            print(year_link)
            yield response.follow(year_link, self.parse_weeks)
            break

    def parse_weeks(self, response):
        week_links = (
            response.css('li[data-type="week"][data-season="reg"]')
            .css("a::attr(href)")
            .extract()
        )
        for week_link in week_links:
            print(week_link)
            yield response.follow(week_link, self.parse_games)
            break

    def parse_games(self, response):
        game_links = response.css(
            'td a[name="&lpos=nfl:schedule:score"]::attr(href)'
        ).extract()
        for game_link in game_links:
            print(game_link)
            yield response.follow(game_link, self.find_box_score_link)
            break

    def find_box_score_link(self, response):
        box_score_links = response.css(
            'li a[name="&lpos=nfl:game:post:subnav:box score"]::attr(href)'
        ).extract()
        for box_score_link in box_score_links:
            print(box_score_link)
            yield response.follow(box_score_link, self.parse_box_score)
            break

    def _parse_team_div(self, response, h_or_a="home"):
        team_city = response.css(
            f'div[class="team {h_or_a}"] span[class="long-name"]::text'
        ).get()
        team_name = response.css(
            f'div[class="team {h_or_a}"] span[class="short-name"]::text'
        ).get()
        team_abbrev = response.css(
            f'div[class="team {h_or_a}"] span[class="abbrev"]::text'
        ).get()
        return team_city, team_name, team_abbrev

    def parse_box_score(self, response):
        home_team_city, home_team_name, home_team_abbrev = self._parse_team_div(
            response, h_or_a="home"
        )
        away_team_city, away_team_name, away_team_abbrev = self._parse_team_div(
            response, h_or_a="away"
        )
        ht_obj, _ = Team.objects.update_or_create(
            name=f"{home_team_city} {home_team_name}"
        )
        at_obj, _ = Team.objects.update_or_create(
            name=f"{away_team_city} {away_team_name}"
        )

        linescore_df = pd.read_html(response.css('table[id="linescore"]').get())[0]
        linescore_df.rename(columns={"Unnamed: 0": "team"}, inplace=True)
        linescore_df.set_index("team", inplace=True)
        home_1q = linescore_df.at[home_team_abbrev, "1"]
        home_2q = linescore_df.at[home_team_abbrev, "2"]
        home_3q = linescore_df.at[home_team_abbrev, "3"]
        home_4q = linescore_df.at[home_team_abbrev, "4"]
        home_score = linescore_df.at[home_team_abbrev, "T"]
        away_1q = linescore_df.at[away_team_abbrev, "1"]
        away_2q = linescore_df.at[away_team_abbrev, "2"]
        away_3q = linescore_df.at[away_team_abbrev, "3"]
        away_4q = linescore_df.at[away_team_abbrev, "4"]
        away_score = linescore_df.at[away_team_abbrev, "T"]
        gt_obj, _ = GameType.objects.update_or_create(name="regular")
        v_obj, _ = Venue.objects.update_or_create(name="Stadium")
        g_obj, _ = Game.objects.update_or_create(
            team1=at_obj,
            team2=ht_obj,
            game_type=gt_obj,
            datetime="2019-04-01 20:30:00",
            venue=v_obj,
        )
        quarters = ["first", "second", "third", "fourth"]
        h_scores = [home_1q, home_2q, home_3q, home_4q]
        a_scores = [away_1q, away_2q, away_3q, away_4q]
        for i in range(1, 5):
            sc_obj, _ = StatCategory.objects.update_or_create(category=f"score")
            ssc_obj, _ = StatSubCategory.objects.update_or_create(sub_category=f"q{i}")
            tgst_obj, _ = TeamGameStatType.objects.update_or_create(
                full_name=f"{quarters[i-1]} quarter score",
                stat=f"q{i} score",
                category=sc_obj,
                sub_category=ssc_obj,
            )
            tgs_hs_obj, _ = TeamGameStat.objects.update_or_create(
                game=g_obj, team=ht_obj, type=tgst_obj, value=h_scores[i - 1]
            )
            tgs_as_obj, _ = TeamGameStat.objects.update_or_create(
                game=g_obj, team=at_obj, type=tgst_obj, value=a_scores[i - 1]
            )

        sc_obj, _ = StatCategory.objects.update_or_create(category=f"score")
        ssc_obj, _ = StatSubCategory.objects.update_or_create(sub_category=f"final")
        tgst_obj, _ = TeamGameStatType.objects.update_or_create(
            full_name="final score",
            stat="score",
            category=sc_obj,
            sub_category=ssc_obj,
        )
        tgs_hs_obj, _ = TeamGameStat.objects.update_or_create(
            game=g_obj, team=ht_obj, type=tgst_obj, value=home_score
        )
        tgs_as_obj, _ = TeamGameStat.objects.update_or_create(
            game=g_obj, team=at_obj, type=tgst_obj, value=away_score
        )

        blue

        # tables = response.css("table")
        # for table in tables[:-1]:
        #     d = defaultdict(list)
        #     for td in table.css("td"):
        #         col_name = td.css("::attr(class)").extract()
        #         if len(col_name) == 0:
        #             continue
        #         col_name = col_name[0]
        #
        #         if col_name == "name":
        #             v = td.css("::text").extract()
        #             if len(v) == 1:
        #                 d["name"] += ["TEAM"]
        #                 d["abbr"] += ["TEAM"]
        #             if len(v) == 2:
        #                 d["name"] += [v[0]]
        #                 d["abbr"] += [v[1]]
        #         else:
        #             col_value = td.css(f'[class="{col_name}"]::text').extract()
        #             d[col_name] += col_value
        #     # pprint.pprint(d)
        # raise CloseSpider("bandwidth_exceeded")
