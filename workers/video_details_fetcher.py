import json
import requests

from tclogger import logger

from configs.envs import PROXY_VIEW_APP_ENVS, COOKIES, BILI_DATA_ROOT
from networks.wbi import ParamsWBISigner
from networks.constants import REQUESTS_HEADERS


class VideoDetailsFetcher:
    KEYS_TO_IGNORE = ["subtitle"]

    def __init__(self):
        self.api = "https://api.bilibili.com/x/web-interface/view"
        self.headers = REQUESTS_HEADERS
        self.headers["Cookie"] = COOKIES

        self.proxy_endpoint = f"http://127.0.0.1:{PROXY_VIEW_APP_ENVS['port']}"
        self.get_proxy_api = f"{self.proxy_endpoint}/get_proxy"
        self.drop_proxy_api = f"{self.proxy_endpoint}/drop_proxy"
        self.restore_proxy_api = f"{self.proxy_endpoint}/restore_proxy"

        self.proxy = None
        self.is_proxy_usable = False

        self.retry_interval = 0.5
        self.retry_count = 5
        self.requests_timeout = 1

    def get_proxy(self):
        # LINK apps/proxy_app.py#get_proxy
        try:
            res = requests.get(self.get_proxy_api)
            if res.status_code == 200:
                proxy = res.json().get("server")
            else:
                proxy = None
        except Exception as e:
            proxy = None

        if proxy:
            if not self.proxy:
                logger.file(f"  > Get proxy:", end=" ")
            else:
                logger.file(f"  > New proxy:", end=" ")
            logger.mesg(f"[{proxy}]")
        else:
            logger.warn(f"  × Failed to get proxy when fetch video: [{self.bvid}]")

        self.proxy = proxy
        if self.proxy:
            self.requests_proxies = {
                "http": f"http://{self.proxy}",
                "https": f"http://{self.proxy}",
            }
        else:
            self.requests_proxies = None

    def drop_proxy(self):
        # LINK apps/proxy_app.py#drop_proxy
        try:
            requests.post(self.drop_proxy_api, json={"server": self.proxy})
        except Exception as e:
            pass
        self.proxy = None
        self.requests_proxies = None

    def restore_proxy(self):
        # LINK apps/proxy_app.py#restore_proxy
        try:
            requests.post(self.restore_proxy_api, json={"server": self.proxy})
        except Exception as e:
            pass
        self.proxy = None
        self.requests_proxies = None

    def create_save_path(self):
        self.save_path = (
            BILI_DATA_ROOT / f"{self.mid}" / "video_details" / f"{self.bvid}.json"
        )
        if not self.save_path.exists():
            self.save_path.parent.mkdir(parents=True, exist_ok=True)

    def filter_video_data(self, data: dict):
        for key in self.KEYS_TO_IGNORE:
            data.pop(key, None)
        return data

    def check_existed(self, mid: int = None):
        if mid is None:
            existed_path = BILI_DATA_ROOT.glob(f"*/video_details/{self.bvid}.json")
            existed_path = sorted(list(existed_path))
            if existed_path:
                existed_path = existed_path[0]
                mid = existed_path.parents[1].name
            else:
                return False
        else:
            existed_path = (
                BILI_DATA_ROOT / f"{mid}" / "video_details" / f"{self.bvid}.json"
            )
            if not existed_path.exists():
                return False

        with open(existed_path, "r") as rf:
            data = json.load(rf)
        if data.get("bvid", "") == self.bvid:
            logger.mesg(f"  * Video details existed: bvid=[{self.bvid}], mid=[{mid}]")
            logger.file(f"  - {existed_path}")
            return True
        return False

    def save_to_json(self, data: dict):
        with open(self.save_path, "w", encoding="utf-8") as wf:
            json.dump(data, wf, ensure_ascii=False, indent=4)
        logger.success(f"  + Video details saved: bvid=[{self.bvid}], mid=[{self.mid}]")
        logger.file(f"  - {self.save_path}")

    def save_result(self, res: requests.Response = None, mid: int = None):
        if res is None:
            logger.warn(f"× No result found: bvid=[{self.bvid}]")
            return

        res_dict = res.json()
        data = res_dict.get("data", {})

        if mid is None:
            self.mid = data.get("owner", {}).get("mid", 0)
        else:
            self.mid = mid

        self.create_save_path()
        data = self.filter_video_data(data)
        self.save_to_json(data)

    def fetch(
        self,
        bvid: str,
        mid: int = None,
        overwrite: bool = False,
        restore_proxy_after_fetch: bool = True,
    ):
        self.bvid = bvid

        logger.note(f"> Fetch video details for bvid:", end=" ")
        logger.mesg(f"[{self.bvid}]")

        is_existed = self.check_existed(mid=mid)
        if is_existed and not overwrite:
            return False

        params = {"bvid": self.bvid}

        is_completed = False
        while not is_completed:
            retry_count = 0
            if not self.proxy or not self.is_proxy_usable:
                self.get_proxy()
            while retry_count < self.retry_count:
                try:
                    res = requests.get(
                        self.api,
                        params=params,
                        headers=REQUESTS_HEADERS,
                        proxies=self.requests_proxies,
                        timeout=self.requests_timeout,
                    )
                    retry_count = 0
                    is_completed = True

                    break
                except Exception as e:
                    retry_count += 1

            if not is_completed:
                self.drop_proxy()
                self.is_proxy_usable = False
            else:
                if restore_proxy_after_fetch:
                    self.restore_proxy()
                    self.is_proxy_usable = False
                else:
                    self.is_proxy_usable = True
                break

        self.save_result(res, mid=mid)

        return True


if __name__ == "__main__":
    bvid = "BV1Qz421B7W9"
    # bvid = "BV1es411q7uP"  # 17 parts
    # bvid = "BV1Uh4y1N7oD"  # missing
    fetcher = VideoDetailsFetcher()
    fetcher.fetch(bvid)

    # python -m workers.video_details_fetcher
