import ast
import concurrent.futures
import os
import requests

from tclogger import logger, count_digits, OSEnver, Runtimer
from pathlib import Path

from .constants import REQUESTS_HEADERS


class ProxyPool:
    def __init__(self):
        enver = OSEnver(Path(__file__).parents[1] / "configs" / "secrets.json")
        self.proxy_endpoint = enver["proxy_endpoint"]

    def get_proxies_list(self):
        logger.note(f"> Fetching proxies list from {self.proxy_endpoint}", end=" ")
        response = requests.get(self.proxy_endpoint, headers=REQUESTS_HEADERS)
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
    def __init__(self):
        self.test_url = (
            "http://api.bilibili.com/x/web-interface/newlist?rid=95&pn=1&ps=1"
        )

        self.tested_count = 0
        self.success_count = 0
        self.success_proxies = []
        self.timer = Runtimer(False)
        self.max_workers = os.cpu_count() * 64

    def test_proxy(self, proxy=None):
        self.timer.start_time()
        self.tested_count += 1
        count_str = f"[{self.tested_count:>{count_digits(self.total_count)}}/{self.total_count}]"
        try:
            res = requests.get(
                self.test_url,
                headers=REQUESTS_HEADERS,
                proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                timeout=1,
            )
        except:
            logger.back(f"{count_str} × Not Connected: {proxy}")
            return False

        self.timer.end_time()
        elapsed_time = self.timer.elapsed_time()
        elapsed_time_str = self.timer.time2str(elapsed_time, unit_sep="")

        try:
            data = res.json()
            self.success_count += 1
            logger.success(
                f"√ [{self.success_count}] {count_str} [{elapsed_time_str}]: {proxy}"
            )
            self.success_proxies.append(proxy)
        except:
            logger.back(f"{count_str} × [{res.status_code}] {proxy}")
            return False

        return True

    def batch_test_proxy(self, proxies):
        logger.note(f"> Benchmarking {len(proxies)} proxies")
        self.total_count = len(proxies)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [executor.submit(self.test_proxy, proxy) for proxy in proxies]

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
