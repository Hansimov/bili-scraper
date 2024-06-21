import ast
import concurrent.futures
import os
import requests
import time

from tclogger import logger, int_bits, OSEnver, Runtimer
from typing import Literal

from networks.constants import REQUESTS_HEADERS
from configs.envs import SECRETS


class ProxyPool:
    def __init__(self):
        pass

    def get_proxies_list(self):
        proxy_endpoint = SECRETS["proxy_endpoint"]
        logger.note(f"> Fetching proxies list from {proxy_endpoint}", end=" ")
        response = requests.get(proxy_endpoint, headers=REQUESTS_HEADERS)
        if response.status_code == 200:
            logger.success(f"[{response.status_code}]")
            data = ast.literal_eval(response.text)
            logger.mesg(f"Proxies count: {len(data)}")
        else:
            logger.err(f"[{response.status_code}]")
            logger.err(f"{response.text}")
            data = []
        return data


class ProxyBenchmarker:
    def __init__(self, test_type: Literal["newlist", "view"] = "newlist"):
        self.test_type = test_type
        if self.test_type == "view":
            self.test_url = (
                "http://api.bilibili.com/x/web-interface/view?bvid=BV1Qz421B7W9"
            )
        else:
            self.test_url = (
                "http://api.bilibili.com/x/web-interface/newlist?rid=95&pn=1&ps=1"
            )

        self.tested_count = 0
        self.success_count = 0
        self.success_proxies = []
        self.timer = Runtimer(False)
        self.max_workers = os.cpu_count() * 64
        self.retry_count = 5
        self.retry_interval = 0.1
        self.accept_success_rate = 0.2
        self.test_timeout = 1

    def test_proxy(self, proxy=None, good_callback=None, bad_callback=None):
        self.tested_count += 1
        count_str = (
            f"[{self.tested_count:>{int_bits(self.total_count)}}/{self.total_count}]"
        )

        current_proxy_success_count = 0
        current_proxy_retry_count = 0
        current_proxy_accumulated_time = 0
        while current_proxy_retry_count < self.retry_count:
            try:
                self.timer.start_time()
                res = requests.get(
                    self.test_url,
                    headers=REQUESTS_HEADERS,
                    proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                    timeout=self.test_timeout,
                )
                self.timer.end_time()
                elapsed_time = self.timer.elapsed_time()
                elapsed_seconds = round(elapsed_time.microseconds * 1e-6, 4)
                res_json = res.json()

                is_success = False
                if self.test_type == "view":
                    data = res_json.get("data", None)
                    if data:
                        is_success = True
                else:
                    archives = res_json.get("data", {}).get("archives", [])
                    if len(archives) > 0:
                        is_success = True

                if is_success:
                    current_proxy_success_count += 1
                    current_proxy_accumulated_time += elapsed_seconds
            except:
                pass

            current_proxy_retry_count += 1
            time.sleep(self.retry_interval)

        current_proxy_success_rate = current_proxy_success_count / self.retry_count

        if current_proxy_success_rate < self.accept_success_rate:
            logger.back(f"{count_str} × Not Connected: {proxy}")
            if bad_callback:
                bad_callback(proxy)
            return False
        else:
            current_proxy_average_latency = round(
                current_proxy_accumulated_time / current_proxy_success_count, 2
            )

        average_latency_str = self.timer.time2str(
            current_proxy_average_latency, unit_sep=""
        )

        self.success_count += 1
        logger.mesg(
            f"√ [{self.success_count}] {count_str} [{average_latency_str}]: {proxy}"
        )
        self.success_proxies.append(proxy)

        if good_callback:
            good_callback(
                proxy, current_proxy_average_latency, current_proxy_success_rate
            )
        return True

    def batch_test_proxy(self, proxies, good_callback=None, bad_callback=None):
        logger.note(f"> Benchmarking {len(proxies)} proxies")
        logger.file(f"  * test_url: {self.test_url}")
        self.total_count = len(proxies)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [
                executor.submit(self.test_proxy, proxy, good_callback, bad_callback)
                for proxy in proxies
            ]

        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()

        logger.success(self.success_count, end="")
        logger.note(f"/{self.total_count}")

        if self.success_proxies:
            logger.back(self.success_proxies)


if __name__ == "__main__":
    with Runtimer():
        proxy_pool = ProxyPool()
        proxies = proxy_pool.get_proxies_list()

        benchmarker = ProxyBenchmarker()
        benchmarker.batch_test_proxy(proxies[:])

    # python -m networks.proxy_pool
