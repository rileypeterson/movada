import scrapy


class SampleSpider(scrapy.Spider):
    name = "sample"

    start_urls = ["https://quotes.toscrape.com/"]

    road = [
        'a[class="tag"][href*=inspirational]::attr(href)',
        'a[class="tag"][href*=life]::attr(href)',
        'a[class="tag"][href*=yourself]::attr(href)',
    ]

    def start_requests(self):
        """Run starting URL with full road."""
        for url in self.start_urls:
            yield scrapy.Request(
                url, callback=self.parse_recurse, cb_kwargs={"road": self.road}
            )

    def parse_recurse(self, response, road):
        """If road is not empty then send to parse_recurse with smaller road.
        If road is empty then send to parse."""

        first = road[0]
        rest = road[1:]

        links = response.css(first).extract()

        if rest:
            # repeat recursion
            for link in links:
                yield response.follow(
                    link, callback=self.parse_recurse, cb_kwargs={"road": rest}
                )
        else:
            # exit recursion
            for link in links:
                yield response.follow(link, callback=self.parse)

    def parse(self, response):
        for resp in response.css('span[itemprop="text"]::text').extract():
            print(resp)
