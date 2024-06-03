"""
* WBI 签名 (Python) | BAC Document
    * https://socialsisteryi.github.io/bilibili-API-collect/docs/misc/sign/wbi.html#python
* 用户主页获取投稿列表 -352 新增校验 · Issue #868 · SocialSisterYi/bilibili-API-collect
  * https://github.com/SocialSisterYi/bilibili-API-collect/issues/868
"""

import urllib.parse
import time
import requests

from hashlib import md5
from functools import reduce

from configs.envs import SECRETS
from networks.constants import REQUESTS_HEADERS


# fmt: off
mixinKeyEncTab = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]
# fmt: on


def get_mi_xin_key(orig: str):
    "对 img_key 和 sub_key 进行字符顺序打乱编码"
    return reduce(lambda s, i: s + orig[i], mixinKeyEncTab, "")[:32]


def sign_params_with_wbi(params: dict, img_key: str, sub_key: str):
    "为请求参数进行 wbi 签名"
    mixin_key = get_mi_xin_key(img_key + sub_key)
    curr_time = round(time.time())
    # 添加 wts 字段
    params["wts"] = curr_time
    # 按照 key 重排参数
    params = dict(sorted(params.items()))
    # 过滤 value 中的 "!'()*" 字符
    params = {
        k: "".join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v in params.items()
    }
    # 序列化参数
    query = urllib.parse.urlencode(params)
    # 计算 w_rid
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()
    params["w_rid"] = wbi_sign
    return params


COOKIES = "; ".join(f"{key}={val}" for key, val in SECRETS["cookies"].items())

headers = REQUESTS_HEADERS
new_headers = {
    "Referer": "https://space.bilibili.com/",
    "Cookie": COOKIES,
}
headers.update(new_headers)


def get_wbi_keys() -> tuple[str, str]:
    # 获取最新的 img_key 和 sub_key
    resp = requests.get("https://api.bilibili.com/x/web-interface/nav", headers=headers)
    resp.raise_for_status()
    json_content = resp.json()
    img_url: str = json_content["data"]["wbi_img"]["img_url"]
    sub_url: str = json_content["data"]["wbi_img"]["sub_url"]
    img_key = img_url.rsplit("/", 1)[1].split(".")[0]
    sub_key = sub_url.rsplit("/", 1)[1].split(".")[0]
    return img_key, sub_key


img_key, sub_key = get_wbi_keys()

signed_params = sign_params_with_wbi(
    params={"mid": 946974, "pn": 1, "ps": 5},
    img_key=img_key,
    sub_key=sub_key,
)
query = urllib.parse.urlencode(signed_params)
print(signed_params)
print(query)

api_head = "https://api.bilibili.com/x/space/wbi/arc/search"

url = f"{api_head}?{query}"
print(url)

res = requests.get(url, headers=headers)
res.raise_for_status()
print(res.json())

# python -m networks.wbi
