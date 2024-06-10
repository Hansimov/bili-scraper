import json
import requests
import time

from math import ceil
from pathlib import Path
from tclogger import logger, Runtimer
from typing import Literal

from configs.envs import PROXY_APP_ENVS
from networks.constants import (
    REQUESTS_HEADERS,
    GET_VIDEO_PAGE_API,
    REGION_CODES,
    REGION_GROUPS,
    REGION_INFOS,
)
from transforms.regions import (
    get_region_tids_from_parent_codes,
    get_region_tids_from_groups,
    get_all_region_tids,
)


class Scanner:
    def __init__(self):
        self.proxy_endpoint = f"http://127.0.0.1:{PROXY_APP_ENVS['port']}"
        self.get_proxy_api = f"{self.proxy_endpoint}/get_proxy"
        self.drop_proxy_api = f"{self.proxy_endpoint}/drop_proxy"
        self.proxy = None
        self.retry_count = 10
        self.timeout = 2.5
        self.interval = 2
        self.tid_queue = []
        self.save_json_path = (
            Path(__file__).parents[1] / "data" / "region" / "regions_count.json"
        )

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
                logger.file(f"> Get proxy: [{proxy}]")
            else:
                logger.file(f"> Update proxy: [{proxy}]")
        else:
            logger.warn(f"× Failed to create new worker: No usable proxy")

        self.proxy = proxy

    def drop_proxy(self):
        # LINK apps/proxy_app.py#drop_proxy
        try:
            requests.post(self.drop_proxy_api, json={"server": self.proxy})
        except Exception as e:
            pass

    def get_page_of_tid(self, tid: int):
        # LINK workers/worker.py#get_page
        proxy = self.proxy

        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        else:
            proxies = None

        url = GET_VIDEO_PAGE_API

        params = {"rid": tid, "pn": 1, "ps": 1}
        res_json = None
        retry_count = 0
        while retry_count < self.retry_count:
            try:
                res = requests.get(
                    url,
                    headers=REQUESTS_HEADERS,
                    params=params,
                    proxies=proxies,
                    timeout=self.timeout,
                )
                if res.status_code == 200:
                    res_json = res.json()
                    break
                else:
                    retry_count += 1
            except Exception as e:
                retry_count += 1

        if not res_json:
            res_json = {
                "code": -1,
                "message": f"Failed to get page after {self.retry_count} retries: tid={tid}",
                "data": {
                    "archives": [],
                    "page": {"count": -1, "num": 1, "size": 1},
                },
            }

        return res_json

    def categorize_response(self, res_dict: dict) -> Literal["network_error", "normal"]:
        code = res_dict.get("code", -1)
        if code != 0:
            return "network_error"
        else:
            return "normal"

    def resolve_network_error(self, res_json: dict, tid: int, task_str: str = ""):
        res_code = res_json.get("code", -1)
        logger.warn(f"  × BAD: {task_str} [code={res_code}]")
        logger.warn(f"    {res_json.get('message', '')}")
        self.drop_proxy()
        self.get_proxy()
        self.tid_queue.insert(0, tid)

    def get_videos_count_from_response(self, res_json: dict, task_str: str = "") -> int:
        page = res_json.get("data", {}).get("page", {})
        videos_count = page.get("count", -1)
        logger.success(f"  √ OK: {task_str}")
        logger.mesg(f"  - videos count: {videos_count}")
        return videos_count

    def update_json_info(self, tid: int, videos_count: int = 0):
        if not self.save_json_path.exists():
            self.save_json_path.parent.mkdir(parents=True, exist_ok=True)
            json_dict = REGION_CODES
        else:
            with open(self.save_json_path, "r", encoding="utf-8") as rf:
                json_dict = json.load(rf)

        region_info = REGION_INFOS[tid]
        parent_code = region_info["parent_code"]
        region_code = region_info["region_code"]

        json_dict[parent_code]["children"][region_code]["videos_count"] = videos_count
        page_count = ceil(videos_count / 50)
        json_dict[parent_code]["children"][region_code]["page_count"] = page_count

        with open(self.save_json_path, "w", encoding="utf-8") as wf:
            json.dump(json_dict, wf, ensure_ascii=False, indent=4)

    def scan(
        self,
        region_groups: list[int] = None,
        region_codes: list[int] = None,
        region_tids: list[int] = None,
    ):
        tids = []

        if region_tids:
            tids = region_tids
        elif region_codes:
            tids = get_region_tids_from_parent_codes(region_codes)
        elif region_groups:
            tids = get_region_tids_from_groups(region_groups)
        else:
            tids = get_all_region_tids()

        logger.mesg(tids)
        self.tid_queue = tids

        if not self.proxy:
            self.get_proxy()

        self.timer = Runtimer(verbose=False)

        scanned_count = 1
        tid_count = len(self.tid_queue)

        while self.tid_queue:
            tid = self.tid_queue.pop(0)
            self.timer.start_time()
            region_name = REGION_INFOS[tid]["region_name"]

            task_str = f"region={region_name}, tid={tid}"
            logger.note(f"> [{scanned_count}/{tid_count}] GET: {task_str}")

            res_json = self.get_page_of_tid(tid)
            res_condition = self.categorize_response(res_json)

            if res_condition == "normal":
                videos_count = self.get_videos_count_from_response(
                    res_json=res_json, task_str=task_str
                )
                self.update_json_info(tid=tid, videos_count=videos_count)
                scanned_count += 1
            elif res_condition == "network_error":
                self.resolve_network_error(
                    res_json=res_json, tid=tid, task_str=task_str
                )
            else:
                res_code = res_json.get("code", -1)
                logger.warn(f"  ? Unknown condition: {task_str} [code={res_code}]")

            self.timer.end_time()
            dt = self.timer.elapsed_time()
            sleep_time = max(self.interval - dt.total_seconds(), 0)
            time.sleep(sleep_time)


if __name__ == "__main__":
    scanner = Scanner()
    region_groups = ["learns"]
    scanner.scan()

    # python -m workers.scanner
