import scrapy
from scrapy_playwright.page import PageCoroutine


class NcaabbSpider(scrapy.Spider):
    name = "ncaabb"

    def start_requests(self):
        # GET request
        start_url = "https://www.bovada.lv/sports/basketball/college-basketball"
        wait_for_first_coupon_box = PageCoroutine(
            "wait_for_selector",
            "sp-next-events",
        )
        scroll_to_bottom = PageCoroutine(
            "evaluate", "window.scrollBy(0, document.body.scrollHeight)"
        )
        yield scrapy.Request(
            start_url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_coroutines": [
                    wait_for_first_coupon_box,
                    scroll_to_bottom,
                ],
            },
        )

    @staticmethod
    def parse_game_box(game_box):
        # Team Names
        top_team, bottom_team = game_box.css(".competitor-name>.name::text").extract()

        spread_col, ml_col, total_col = game_box.css("sp-two-way-vertical")

        # Spread
        top_spread, bottom_spread = spread_col.css(
            "sp-spread-outcome > .market-line,bet-handicap::text"
        ).extract()
        top_spread_odds, bottom_spread_odds = spread_col.css(
            ".bet-price::text"
        ).extract()

        # Moneyline
        top_ml_odds, bottom_ml_odds = ml_col.css(".bet-price::text").extract()

        # Over / Under
        (
            top_total_label,
            top_total,
            bottom_total_label,
            bottom_total,
        ) = total_col.css(".market-line,bet-handicap,both-handicaps::text").extract()
        top_total_odds, bottom_total_odds = total_col.css(".bet-price::text").extract()
        return (
            top_team,
            bottom_team,
            top_spread,
            bottom_spread,
            top_spread_odds,
            bottom_spread_odds,
            top_ml_odds,
            bottom_ml_odds,
            top_total_label,
            top_total,
            bottom_total_label,
            bottom_total,
            top_total_odds,
            bottom_total_odds,
        )

    async def parse(self, response):
        # 'response' contains the page as seen by the browser
        page = response.meta["playwright_page"]
        await page.screenshot(path="quotes.png")
        await page.close()
        game_boxes = response.css("sp-next-events").css("sp-coupon")
        for game_box in game_boxes:
            try:
                (
                    top_team,
                    bottom_team,
                    top_spread,
                    bottom_spread,
                    top_spread_odds,
                    bottom_spread_odds,
                    top_ml_odds,
                    bottom_ml_odds,
                    top_total_label,
                    top_total,
                    bottom_total_label,
                    bottom_total,
                    top_total_odds,
                    bottom_total_odds,
                ) = self.parse_game_box(game_box)
            except ValueError:
                pass

        a = 1
        yield {"url": response.url}


#
# "body > bx-site > ng-component > div > sp-sports-ui > div > main > div > section > main > sp-path-event > div > sp-next-events > div > div"
# "/html/body/bx-site/ng-component/div/sp-sports-ui/div/main/div/section/main/sp-path-event/div/sp-next-events/div/div"
# "/html/body/bx-site/ng-component/div/sp-sports-ui/div/main/div/section/main/sp-path-event/div/sp-next-events/div/div/div[2]/div/sp-coupon[1]"
