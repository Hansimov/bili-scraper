import ast
import requests

from tclogger import logger, OSEnver
from pathlib import Path

from .constants import REQUESTS_HEADERS


class ProxyPool:
    def __init__(self):
        enver = OSEnver(Path(__file__).parents[1] / "configs" / "secrets.json")
        self.proxy_endpoint = enver["proxy_endpoint"]
        self.test_url = (
            "http://api.bilibili.com/x/web-interface/newlist?rid=95&pn=1&ps=1"
        )

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

    def bench(self, proxies: list[str] = []):
        for proxy in proxies:
            logger.note(f"> Benchmarking proxy: http://{proxy}", end=" ")
            requests_proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",
            }
            response = requests.get(
                self.test_url,
                headers=REQUESTS_HEADERS,
                timeout=5,
                proxies=requests_proxies,
            )
            if response.status_code == 200:
                logger.success(f"[{response.status_code}]")
            else:
                logger.warn(f"[{response.status_code}]")


if __name__ == "__main__":
    proxy_pool = ProxyPool()
    proxies = proxy_pool.get_proxies_list()

    # python -m networks.proxy_pool
