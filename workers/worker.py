import requests
import time

from tclogger import logger, Runtimer
from typing import Literal


from configs.envs import VIDEO_PAGE_API_MOCKER_ENVS, PROXY_APP_ENVS
from networks.constants import REQUESTS_HEADERS, GET_VIDEO_PAGE_API, REGION_CODES


class WorkerParamsGenerator:
    def __init__(
        self,
        region_codes: list[str] = [],
        start_tid: int = -1,
        start_pn: int = -1,
        mock: bool = False,
    ):
        self.mock = mock
        self.region_codes = region_codes
        self.start_tid = start_tid
        self.start_pn = start_pn
        self.init_tids()

    def init_tids(self):
        self.queue = []
        self.exhausted_tids = []
        main_regions = [REGION_CODES[region_code] for region_code in self.region_codes]
        self.regions = [
            region
            for main_region in main_regions
            for region in main_region["children"].values()
        ]
        self.tids = [region["tid"] for region in self.regions]
        if self.start_tid != -1 and self.start_tid in self.tids:
            self.tid_idx = self.tids.index(self.start_tid)
        else:
            self.tid_idx = 0
        if self.start_pn != -1:
            self.pn = self.start_pn
        else:
            self.pn = 0
        self.tid = self.get_tid()
        self.queue.append((self.tid, self.pn))
        self.is_current_region_exhausted = False
        logger.note(f"> Regions: {self.region_codes} => {len(self.tids)} sub-regions")

    def get_region(self, tid: int):
        if tid in self.tids:
            idx = self.tids.index(tid)
            return self.regions[idx]
        else:
            return {}

    def get_tid(self):
        if self.tid_idx < len(self.tids):
            return self.tids[self.tid_idx]
        else:
            return -1

    def flag_current_region_exhausted(self, exhausted_tid: int):
        if exhausted_tid not in self.exhausted_tids:
            self.exhausted_tids.append(exhausted_tid)
            self.is_current_region_exhausted = True

    def is_terminated(self):
        if self.tid == -1 and self.pn == -1:
            return True
        return False

    def next(self):
        if self.queue:
            return self.queue.pop(0)
        if self.is_current_region_exhausted:
            self.tid_idx += 1
            if self.tid_idx < len(self.regions):
                self.tid = self.get_tid()
                self.pn = 1
            else:
                self.tid = -1
                self.pn = -1
            self.is_current_region_exhausted = False
        else:
            self.pn += 1
        return self.tid, self.pn


class ResponseCategorizer:
    def categorize(
        self, res_dict: dict
    ) -> Literal["network_error", "end_of_region", "normal"]:
        code = res_dict.get("code")
        if code != 0:
            return "network_error"
        archives = res_dict.get("data", {}).get("archives", [])
        if len(archives) == 0:
            return "end_of_region"
        else:
            return "normal"


class Worker:
    def __init__(
        self,
        generator: WorkerParamsGenerator,
        lock,
        wid: int = -1,
        proxy: str = None,
        mock: bool = False,
        interval: float = 2.5,
        retry_count: int = 15,
        time_out: float = 2.5,
    ):
        self.wid = wid
        self.generator = generator
        self.lock = lock
        self.proxy = proxy
        self.mock = mock
        self.active = False
        self.interval = interval
        self.retry_count = retry_count
        self.time_out = time_out
        self.response_categorizer = ResponseCategorizer()
        self.proxy_endpoint = f"http://127.0.0.1:{PROXY_APP_ENVS['port']}"
        self.get_proxy_api = f"{self.proxy_endpoint}/get_proxy"
        self.drop_proxy_api = f"{self.proxy_endpoint}/drop_proxy"

    def get_proxy(self):
        # LINK apps/proxy_app.py#get_proxy
        params = {"mock": self.mock}
        try:
            res = requests.get(self.get_proxy_api, params=params)
            if res.status_code == 200:
                proxy = res.json().get("server")
            else:
                proxy = None
        except Exception as e:
            proxy = None

        if proxy:
            if not self.proxy:
                logger.file(f"> New worker {self.wid} with proxy: [{proxy}]")
            else:
                logger.file(f"> Worker {self.wid} with new proxy: [{proxy}]")
            self.active = True
        else:
            logger.warn(f"× Failed to create new worker: No usable proxy")
            self.active = False

        self.proxy = proxy

    def drop_proxy(self):
        # LINK apps/proxy_app.py#drop_proxy
        try:
            requests.post(self.drop_proxy_api, json={"server": self.proxy})
        except Exception as e:
            pass

    def get_page(self, tid: int, pn: int, ps: int = 50):
        proxy = self.proxy
        mock = self.mock

        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        else:
            proxies = None

        if mock:
            url = f"http://127.0.0.1:{VIDEO_PAGE_API_MOCKER_ENVS['port']}/page_info"
            proxies = None
        else:
            url = GET_VIDEO_PAGE_API

        params = {"rid": tid, "pn": pn, "ps": ps}

        res_json = None
        retry_count = 0
        while retry_count < self.retry_count:
            try:
                res = requests.get(
                    url,
                    headers=REQUESTS_HEADERS,
                    params=params,
                    proxies=proxies,
                    timeout=self.time_out,
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
                "message": f"Failed to get page after {self.retry_count} retries: tid={tid}, pn={pn}",
                "data": {
                    "archives": [],
                    "page": {"count": -1, "num": pn, "size": ps},
                },
            }

        return res_json

    def run(self):
        if not self.proxy:
            with self.lock:
                self.get_proxy()

        retry_last_params = False
        self.timer = Runtimer(verbose=False)

        while True:
            self.timer.start_time()
            if not self.active:
                break

            with self.lock:
                if self.generator.is_terminated():
                    self.active = False
                    break

            with self.lock:
                if not retry_last_params:
                    tid, pn = self.generator.next()
                else:
                    tid, pn = tid, pn
                    retry_last_params = False

            region_name = self.generator.get_region(tid).get("name", "Unknown")
            task_str = f"region={region_name}, tid={tid}, pn={pn}, wid={self.wid: >2}"
            logger.note(f"> GET: {task_str}")

            if tid == -1 and pn == -1:
                logger.success(f"[Finished]")
                break

            res_json = self.get_page(tid=tid, pn=pn)
            archives = res_json.get("data", {}).get("archives", [])
            res_code = res_json.get("code", -1)
            res_condition = self.response_categorizer.categorize(res_json)

            if res_condition == "end_of_region":
                logger.mesg(f"  ! End: {task_str}")
                with self.lock:
                    self.generator.flag_current_region_exhausted(exhausted_tid=tid)
            elif res_condition == "normal":
                logger.success(f"  + GOOD: {task_str}", end=" ")
                logger.mesg(f"<{len(archives)} videos>")
            elif res_condition == "network_error":
                logger.warn(f"  × BAD: {task_str} [code={res_code}]")
                logger.warn(f"    {res_json.get('message', '')}")
                self.drop_proxy()
                self.get_proxy()
                retry_last_params = True
                if not self.active:
                    with self.lock:
                        self.generator.queue.append((tid, pn))
            else:
                logger.warn(f"  - Unknown condition: {task_str} [code={res_code}]")

            self.timer.end_time()
            dt = self.timer.elapsed_time()

            sleep_time = max(self.interval - dt.total_seconds(), 0)
            time.sleep(sleep_time)
