"""
* WBI 签名 (Python) | BAC Document
    * https://socialsisteryi.github.io/bilibili-API-collect/docs/misc/sign/wbi.html#python
* 用户主页获取投稿列表 -352 新增校验 · Issue #868 · SocialSisterYi/bilibili-API-collect
  * https://github.com/SocialSisterYi/bilibili-API-collect/issues/868
"""

import urllib.parse
import time
import requests

from functools import reduce
from hashlib import md5
from pprint import pformat
from tclogger import logger

from configs.envs import COOKIES
from networks.constants import REQUESTS_HEADERS


class ParamsWBISigner:
    # fmt: off
    MAGIC_KEYS = [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
        33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
        61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
        36, 20, 34, 44, 52
    ]
    # fmt: on

    def __init__(self):
        self.init_headers()

    def init_headers(self):
        self.headers = REQUESTS_HEADERS
        new_headers = {
            "Referer": "https://space.bilibili.com/",
            # "Cookie": COOKIES,
        }
        self.headers.update(new_headers)

        self.img_key = None
        self.sub_key = None

    def get_magic_key(self, text: str):
        """shuffle img_key and sub_key"""
        return reduce(lambda s, i: s + text[i], self.MAGIC_KEYS, "")[:32]

    def get_wbi_keys(self) -> tuple[str, str]:
        """get latest img_key and sub_key"""
        nav_url = "https://api.bilibili.com/x/web-interface/nav"
        resp = requests.get(nav_url, headers=self.headers)
        resp.raise_for_status()
        json_content = resp.json()
        wbi_img = json_content["data"]["wbi_img"]
        img_url = wbi_img["img_url"]
        sub_url = wbi_img["sub_url"]
        self.img_key = img_url.rsplit("/", 1)[1].split(".")[0]
        self.sub_key = sub_url.rsplit("/", 1)[1].split(".")[0]

    def sign_params_with_wbi(self, params: dict, img_key: str, sub_key: str):
        """sign params with wbi"""
        magic_key = self.get_magic_key(img_key + sub_key)
        curr_time = round(time.time())
        params["wts"] = curr_time
        params = dict(sorted(params.items()))
        params = {
            k: "".join(filter(lambda chr: chr not in "!'()*", str(v)))
            for k, v in params.items()
        }
        query = urllib.parse.urlencode(params)
        wbi_sign = md5((query + magic_key).encode()).hexdigest()
        params["w_rid"] = wbi_sign
        return params

    def run(self, params: dict):
        if self.img_key is None or self.sub_key is None:
            self.get_wbi_keys()
        signed_params = self.sign_params_with_wbi(params, self.img_key, self.sub_key)
        return signed_params


if __name__ == "__main__":
    url = "https://api.bilibili.com/x/space/wbi/arc/search"
    mid = 946974
    pn, ps = 1, 5
    params = {"mid": mid, "pn": pn, "ps": ps}
    signer = ParamsWBISigner()
    signed_params = signer.run(params)
    logger.note("> Get signed params:")
    print(pformat(signed_params, sort_dicts=False))
    headers = signer.headers
    headers["Cookie"] = COOKIES
    res = requests.get(url, headers=headers, params=signed_params)
    res.raise_for_status()
    logger.note(f"> Get videos from mid {mid}:")
    print(pformat(res.json(), sort_dicts=False))

    # python -m networks.wbi
