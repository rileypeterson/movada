from scrapy.extensions.httpcache import DummyPolicy
import pandas as pd


class DataPolicy(DummyPolicy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_cached_response_fresh(self, cachedresponse, request):
        date_cached = pd.to_datetime(cachedresponse.headers["Date"].decode())
        game_datetime = pd.to_datetime(request.cb_kwargs["data"]["game_datetime"])
        if date_cached.date() > game_datetime.date():
            return True
        return False
