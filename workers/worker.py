import requests
import threading
import time

from datetime import datetime, timedelta
from pathlib import Path
from tclogger import logger, Runtimer
from typing import Literal

from configs.envs import PROXY_APP_ENVS, LOG_ENVS
from networks.constants import REQUESTS_HEADERS, GET_VIDEO_PAGE_API, REGION_CODES
from transforms.video_row import VideoInfoConverter
from networks.sql import SQLOperator


class WorkerParamsGenerator:
    def __init__(
        self,
        region_codes: list[str] = [],
        start_tid: int = -1,
        start_pn: int = -1,
        end_tid: int = -1,
        end_pn: int = -1,
        log_mids: list[int] = [],
    ):
        self.lock = threading.Lock()
        self.region_codes = region_codes
        self.start_tid = start_tid
        self.start_pn = start_pn
        self.end_tid = end_tid
        self.end_pn = end_pn
        self.log_mids = log_mids
        self.log_file = Path(__file__).parents[1] / "logs" / LOG_ENVS["worker"]
        self.inserted_videos_num = 0
        self.start_time = datetime.now()
        self.init_tids()

    def init_tids(self):
        self.queue = []
        self.exhausted_tids = []
        main_regions = [REGION_CODES[region_code] for region_code in self.region_codes]
        self.regions = [
            region
            for main_region in main_regions
            for region in main_region["children"].values()
            if region.get("status", "") not in ["redirect"]
        ]
        self.tids = [region["tid"] for region in self.regions]
        logger.note(f"> Regions: {self.region_codes} => {len(self.tids)} sub-regions")

        if self.start_tid != -1 and self.start_tid in self.tids:
            self.tid_idx = self.tids.index(self.start_tid)
        else:
            self.tid_idx = 0
        if self.start_pn != -1:
            self.pn = self.start_pn
        else:
            self.pn = 0
        self.tid = self.get_tid()

        if self.end_tid in self.tids:
            self.end_tid_idx = self.tids.index(self.end_tid)
        else:
            self.end_tid_idx = len(self.tids)

        self.queue.append((self.tid, self.pn))
        self.is_current_region_exhausted = False
        logger.note(f"> Start: tid={self.tid}, pn={self.pn}")

    def get_region(self, tid: int):
        if tid in self.tids:
            idx = self.tids.index(tid)
            return self.regions[idx]
        else:
            return {}

    def get_region_name(self, tid: int):
        return self.get_region(tid).get("name", "Unknown")

    def get_tid(self):
        if self.tid_idx < len(self.tids):
            return self.tids[self.tid_idx]
        else:
            return -1

    def log_to_file(
        self, log_type: Literal["end_of_region", "others"] = "end_of_region"
    ):
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if log_type == "end_of_region":
            region_name = self.get_region_name(self.tid)
            log_str = f"× [{time_str}] [End of Region]: region={region_name}, tid={self.tid}, pn={self.pn}"
        else:
            log_str = f"? [{time_str}]"
        with open(self.log_file, "a") as f:
            f.write(f"{log_str}\n\n")

    def add_inserted_videos_num(self, num: int = 50):
        with self.lock:
            self.inserted_videos_num += num

    def get_estimated_remaining_time_str(
        self, current_count: int = -1, total_count: int = -1
    ):
        if current_count == -1 or total_count == -1:
            return None
        if self.inserted_videos_num == 0:
            return None
        remaining_count = total_count - current_count
        elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
        estimated_remaining_seconds = int(
            elapsed_seconds * remaining_count / self.inserted_videos_num
        )

        hours = estimated_remaining_seconds // 3600
        minutes = (estimated_remaining_seconds % 3600) // 60
        seconds = estimated_remaining_seconds % 60
        estimated_remaining_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        return estimated_remaining_time_str

    def flag_current_region_exhausted(self, exhausted_tid: int, task_str: str = ""):
        with self.lock:
            if exhausted_tid not in self.exhausted_tids:
                logger.mesg(f"  ! End: {task_str}")
                self.exhausted_tids.append(exhausted_tid)
                self.is_current_region_exhausted = True
                self.log_to_file(log_type="end_of_region")

    def is_terminated(self):
        with self.lock:
            if self.queue:
                return False
            if self.tid == -1 and self.pn == -1:
                return True
            if self.tid_idx >= self.end_tid_idx and self.pn >= self.end_pn:
                return True
            return False

    def append_queue(self, tid: int, pn: int):
        with self.lock:
            self.queue.append((tid, pn))

    def next(self):
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
            if self.tid == -1 and self.pn == -1:
                return (-1, -1)
            if self.is_current_region_exhausted:
                self.tid_idx += 1
                if self.tid_idx < len(self.tids):
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
    def __init__(self, region_end_retry_count: int = 5):
        self.region_end_retry_idx = 0
        self.region_end_retry_count = region_end_retry_count
        self.lock = threading.Lock()

    def categorize(
        self, res_dict: dict
    ) -> Literal["network_error", "end_of_region", "normal"]:
        code = res_dict.get("code", -1)
        if code != 0:
            return "network_error"

        archives = res_dict.get("data", {}).get("archives", [])
        if len(archives) == 0:
            with self.lock:
                self.region_end_retry_idx += 1
                if self.region_end_retry_idx >= self.region_end_retry_count:
                    self.region_end_retry_idx = 0
                    return "end_of_region"

        return "normal"


class Worker:
    def __init__(
        self,
        generator: WorkerParamsGenerator,
        sql: SQLOperator,
        lock: threading.Lock,
        wid: int = -1,
        proxy: str = None,
        interval: float = 2.5,
        retry_count: int = 15,
        time_out: float = 2.5,
    ):
        self.wid = wid
        self.generator = generator
        self.lock = lock
        self.proxy = proxy
        self.active = False
        self.condition = threading.Condition()
        self.interval = interval
        self.retry_count = retry_count
        self.time_out = time_out
        self.response_categorizer = ResponseCategorizer()
        self.converter = VideoInfoConverter()
        self.sql = sql
        self.log_file = Path(__file__).parents[1] / "logs" / LOG_ENVS["worker"]
        self.proxy_endpoint = f"http://127.0.0.1:{PROXY_APP_ENVS['port']}"
        self.get_proxy_api = f"{self.proxy_endpoint}/get_proxy"
        self.drop_proxy_api = f"{self.proxy_endpoint}/drop_proxy"

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

        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        else:
            proxies = None

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

    def log_to_file(self, log_str: str):
        with open(self.log_file, "a") as f:
            f.write(f"{log_str}\n\n")

    def get_pubdate_str_from_archives(self, archives: list) -> str:
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        pubdate_ts = now.timestamp()
        for archive in archives:
            pubdate_ts = min(archive.get("pubdate", pubdate_ts), pubdate_ts)
            if self.generator.log_mids:
                owner = archive.get("owner", {})
                mid = owner.get("mid", 0)
                if mid in self.generator.log_mids:
                    title = archive.get("title", "")
                    name = owner.get("name", "")
                    pubdate_str = datetime.fromtimestamp(pubdate_ts).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    log_str = f"+ [{now_str}] [{pubdate_str}] [{name}] [{title}]"
                    self.log_to_file(log_str)

        pubdate_datetime = datetime.fromtimestamp(pubdate_ts)
        pubdate_datetime_str = pubdate_datetime.strftime("%Y-%m-%d %H:%M:%S")
        return pubdate_datetime_str

    def get_archives_from_response(
        self, res_json: dict, pn: int, ps: int = 50, task_str: str = ""
    ):
        archives = res_json.get("data", {}).get("archives", [])
        page = res_json.get("data", {}).get("page", {})
        total_count = page.get("count", -1)
        current_count = pn * ps
        if total_count > 0:
            progress = round(current_count / total_count * 100, 2)
        else:
            progress = 0
        pubdate_str = self.get_pubdate_str_from_archives(archives)
        logger.success(f"  + GOOD: {task_str}", end=" ")
        logger.mesg(f"<{len(archives)} videos>")
        logger.file(f"    [{pubdate_str}]", end=" ")
        logger.mesg(f"[{current_count}/{total_count}] [{progress}%]")
        return archives, current_count, total_count

    def insert_rows(
        self, archives: list, current_count: int = -1, total_count: int = -1
    ):
        t1 = datetime.now()
        sql_values_list = []
        for archive in archives:
            sql_row = self.converter.to_sql_row(archive)
            sql_query, sql_values = self.converter.to_sql_query_and_values(
                sql_row,
                table_name="videos",
                is_many=True,
                update_on_conflict=True,
                primary_key="bvid",
            )
            sql_values_list.append(sql_values)
        if sql_values_list:
            self.sql.exec(sql_query, sql_values_list, is_many=True)
            t2 = datetime.now()
            dt = t2 - t1
            dt_str = f"{dt.seconds}.{dt.microseconds // 1000:03d} s"
            self.generator.add_inserted_videos_num(len(archives))
            estimated_remaining_seconds_str = (
                self.generator.get_estimated_remaining_time_str(
                    current_count=current_count, total_count=total_count
                )
            )
            logger.success(f"  + Inserted: {len(archives)} rows", end=" ")
            logger.file(f"({dt_str})", end=" ")
            logger.mesg(f"[ETA={estimated_remaining_seconds_str}]")

    def resolve_network_error(
        self, res_json: dict, tid: int, pn: int, task_str: str = ""
    ):
        res_code = res_json.get("code", -1)
        logger.warn(f"  × BAD: {task_str} [code={res_code}]")
        logger.warn(f"    {res_json.get('message', '')}")
        self.drop_proxy()
        self.get_proxy()
        self.generator.append_queue(tid, pn)

    def activate(self):
        with self.condition:
            self.active = True
            self.condition.notify()

    def deactivate(self):
        self.active = False
        logger.mesg(f"> Deactivate worker {self.wid}")

    def run(self):
        if not self.proxy:
            with self.lock:
                self.get_proxy()

        self.timer = Runtimer(verbose=False)

        while True:
            with self.condition:
                while not self.active:
                    self.condition.wait()

            self.timer.start_time()

            if self.generator.is_terminated():
                self.deactivate()
                logger.file("=" * 20 + f" [Terminated] ({self.wid: >2}) " + "=" * 20)
                continue

            tid, pn = self.generator.next()

            region_name = self.generator.get_region_name(tid)
            task_str = f"region={region_name}, tid={tid}, pn={pn}, wid={self.wid: >2}"
            logger.note(f"> GET: {task_str}")

            ps = 50
            res_json = self.get_page(tid=tid, pn=pn, ps=ps)
            res_condition = self.response_categorizer.categorize(res_json)

            if res_condition == "end_of_region":
                self.generator.flag_current_region_exhausted(
                    exhausted_tid=tid, task_str=task_str
                )
            elif res_condition == "normal":
                archives, current_count, total_count = self.get_archives_from_response(
                    res_json=res_json, pn=pn, ps=ps, task_str=task_str
                )
                self.insert_rows(
                    archives, current_count=current_count, total_count=total_count
                )
            elif res_condition == "network_error":
                self.resolve_network_error(
                    res_json=res_json, tid=tid, pn=pn, task_str=task_str
                )
            else:
                res_code = res_json.get("code", -1)
                logger.warn(f"  ? Unknown condition: {task_str} [code={res_code}]")

            self.timer.end_time()
            dt = self.timer.elapsed_time()

            sleep_time = max(self.interval - dt.total_seconds(), 0)
            time.sleep(sleep_time)
