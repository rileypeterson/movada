import scrapy
from scrapy_playwright.page import PageCoroutine


class NcaabbSpider(scrapy.Spider):
    name = "ncaabb"

    def start_requests(self):
        # GET request
        yield scrapy.Request(
            "https://www.bovada.lv/sports/basketball/college-basketball",
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_coroutines": {
                    "wait_for_selector": PageCoroutine(
                        "wait_for_selector",
                        "body > bx-site > ng-component > div > sp-sports-ui > div > main > div > section > main > sp-path-event > div > sp-next-events > div > div > div.bucket__collapsableSection > div > sp-coupon:nth-child(2) > sp-multi-markets > section > section > header > sp-competitor-coupon > a > div > h4:nth-child(1)",
                    ),
                },
            },
        )

    async def parse(self, response):
        # 'response' contains the page as seen by the browser
        page = response.meta["playwright_page"]
        await page.screenshot(path="quotes.png")
        await page.close()
        a = 1
        yield {"url": response.url}
