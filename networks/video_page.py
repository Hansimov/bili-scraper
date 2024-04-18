import requests
from tclogger import logger
from .constants import REQUESTS_HEADERS


class VideoPageFetcher:
    def __init__(self):
        self.api_body = (
            "http://api.bilibili.com/x/web-interface/newlist?rid={}&pn={}&ps={}"
        )

    def get(self, rid: int, pn: int, ps: int = 50, proxy=None):
        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        else:
            proxies = None

        url = self.api_body.format(rid, pn, ps)
        logger.note(f"> rid: {rid} | pn: {pn} - Fetching video page list", end=" ")
        res = requests.get(url, headers=REQUESTS_HEADERS, proxies=proxies, timeout=10)
        if res.status_code == 200:
            logger.success(f"[{res.status_code}]")
        else:
            logger.err(f"[{res.status_code}]")
            logger.err(f"{res.text}")
        data = res.json()
        return data


if __name__ == "__main__":
    fetcher = VideoPageFetcher()
    rid, pn = 20, 1
    data = fetcher.get(rid=rid, pn=pn)

    # python -m networks.video_page
