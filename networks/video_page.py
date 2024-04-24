import requests

from random import randint
from tclogger import logger

from networks.constants import REQUESTS_HEADERS, GET_VIDEO_PAGE_API
from configs.envs import VIDEO_PAGE_API_MOCKER_ENVS


class VideoPageFetcher:
    def get(self, tid: int, pn: int, ps: int = 50, proxy=None, mock: bool = False):
        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        else:
            proxies = None

        if mock:
            url = f"http://127.0.0.1:{VIDEO_PAGE_API_MOCKER_ENVS['port']}/page_info"
        else:
            url = GET_VIDEO_PAGE_API

        params = {"tid": tid, "pn": pn, "ps": ps}

        try:
            res = requests.get(
                url, headers=REQUESTS_HEADERS, params=params, proxies=proxies, timeout=5
            )
            if res.status_code == 200:
                res_json = res.json()
            else:
                res_json = {
                    "code": res.status_code,
                    "message": res.text,
                    "ttl": 1,
                    "data": {
                        "archives": [],
                        "page": {"count": randint(1e4, 1e7), "num": pn, "size": ps},
                    },
                }
        except Exception as e:
            res_json = {
                "code": -1,
                "message": str(e),
                "ttl": 1,
                "data": {
                    "archives": [],
                    "page": {"count": randint(1e4, 1e7), "num": pn, "size": ps},
                },
            }
        return res_json


if __name__ == "__main__":
    fetcher = VideoPageFetcher()
    rid, pn = 20, 1
    data = fetcher.get(rid=rid, pn=pn)

    # python -m networks.video_page
