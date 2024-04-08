import ast
import concurrent.futures
import os
import requests

from tclogger import logger, int_bits, OSEnver, Runtimer
from pathlib import Path

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
    def __init__(self):
        self.test_url = (
            "http://api.bilibili.com/x/web-interface/newlist?rid=95&pn=1&ps=1"
        )

        self.tested_count = 0
        self.success_count = 0
        self.success_proxies = []
        self.timer = Runtimer(False)
        self.max_workers = os.cpu_count() * 64

    def test_proxy(self, proxy=None, callback=None):
        self.timer.start_time()
        self.tested_count += 1
        count_str = (
            f"[{self.tested_count:>{int_bits(self.total_count)}}/{self.total_count}]"
        )
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
            logger.mesg(
                f"√ [{self.success_count}] {count_str} [{elapsed_time_str}]: {proxy}"
            )
            self.success_proxies.append(proxy)
            if callback:
                elapsed_seconds = round(elapsed_time.microseconds * 1e-6, 2)
                callback(proxy, elapsed_seconds)
        except:
            logger.back(f"{count_str} × [{res.status_code}] {proxy}")
            return False

        return True

    def batch_test_proxy(self, proxies, callback=None):
        logger.note(f"> Benchmarking {len(proxies)} proxies")
        self.total_count = len(proxies)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = [
                executor.submit(self.test_proxy, proxy, callback) for proxy in proxies
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
