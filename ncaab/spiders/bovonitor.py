import scrapy
from scrapy_playwright.page import PageCoroutine
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import traceback
import zmq
import asyncio


os.environ["PWDEBUG"] = "0"


class BovonitorSpider(scrapy.Spider):
    name = "bovonitor"

    custom_settings = {
        "HTTPCACHE_ENABLED": False,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_ABORT_REQUEST": lambda req: req.resource_type in {"image"}
        or req.url.endswith(".gif"),
    }

    def start_requests(self):
        start_url = "https://www.bovada.lv/sports/basketball"
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

    async def parse_sp_multi_market(self, l):
        competitors = await l.locator(".competitors").all_inner_texts()
        competitors = competitors[0].splitlines()

        # Spread
        spread = await l.locator(".market-type").nth(0).all_inner_texts()
        spread = spread[0].splitlines()

        # ML
        ml = await l.locator(".market-type").nth(1).all_inner_texts()
        ml = ml[0].splitlines()

        # Total
        total = await l.locator(".market-type").nth(2).all_inner_texts()
        total = total[0].splitlines()
        d = {"competitors": competitors, "spread": spread, "ml": ml, "total": total}
        return d

    async def open_plus_boxes(self, page):
        # Open all plus boxes
        for _ in range(100):
            try:
                await page.click(
                    "i.icon.header-collapsible__icon.icon-plus", timeout=1000
                )
            except Exception:
                # print(traceback.format_exc())
                break

    async def read_data(self, page):
        urls = await page.eval_on_selector_all(
            "sp-multi-markets a.game-view-cta",
            "elements => elements.map(element => element.href)",
        )
        data = dict()
        for url in urls:
            u = url.replace("https://www.bovada.lv", "")
            l = page.locator(f"sp-multi-markets:has(a[href='{u}'])")
            data[url] = await self.parse_sp_multi_market(l)
        return data

    async def parse(self, response):
        page = response.meta["playwright_page"]

        await self.open_plus_boxes(page)

        data = await self.read_data(page)

        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:5556")
        i = 0
        while True:
            print(i)
            data_new = await self.read_data(page)
            for k_new, v_new in data_new.items():
                if k_new not in data or v_new != data[k_new]:
                    socket.send_json(data_new[k_new])
            data = data_new
            await asyncio.sleep(0.1)
            i += 1

        # Other stuff
        # await elm.get_attribute("class")

        # await (await (await page.locator("sp-multi-markets").nth(3).element_handle()).wait_for_selector(
        #     "* > .price-increased", timeout=5000)).inner_text()


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(BovonitorSpider)
    process.start()
