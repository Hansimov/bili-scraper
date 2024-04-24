import pandas as pd
import random
import string
import uvicorn

from datetime import datetime
from faker import Faker
from fastapi import FastAPI, Body
from pprint import pformat
from pydantic import BaseModel, Field
from random import randint
from tclogger import logger
from typing import Union, Optional


from apps.arg_parser import ArgParser
from configs.envs import VIDEO_PAGE_API_MOCKER_ENVS as APP_ENVS
from networks.constants import REGION_CODES


class ArchiveGenerator:
    def __init__(self):
        self.init_faker()

    def init_faker(self):
        fake = Faker(locale="zh_CN")
        self.fake = fake

    def get_region_name_by_tid(self, tid: int):
        for key, val in REGION_CODES.items():
            sub_regions = val["children"]
            for sub_key, sub_val in sub_regions.items():
                if sub_val["tid"] == tid:
                    return sub_val["name"]
        return None

    def select_from_random_set(self, random_set, length: 1) -> str:
        return "".join(random.choices(random_set, k=length))

    def random_hex(self, length: int = 40) -> str:
        random_set = "0123456789abcdef"
        return self.select_from_random_set(random_set, length)

    def random_lower_ascii(self, length: int = 32):
        random_set = string.ascii_lowercase + string.digits
        return self.select_from_random_set(random_set, length)

    def random_ascii(self, length: int = 10):
        random_set = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return self.select_from_random_set(random_set, length)

    def random_timestamp(self):
        t = self.fake.date_time_between_dates(
            datetime_start=datetime(2006, 6, 26), datetime_end=datetime.now()
        )
        return int(t.timestamp())

    def get(self, tid: int, idx: int = 0):
        seed = tid * 1e9 + idx
        self.fake.seed_instance(seed)
        random.seed(seed)

        aid = randint(1, 1e10)
        bvid = "BV" + self.random_ascii(10)
        pubdate = self.random_timestamp()
        res = {
            "aid": aid,
            "videos": randint(1, 10),
            "tid": tid,
            "tname": self.get_region_name_by_tid(tid),
            "copyright": randint(0, 1),
            "pic": f"http://i1.hdslb.com/bfs/archive/{self.random_hex(40)}.jpg",
            "title": self.fake.sentence(nb_words=20),
            "pubdate": pubdate,
            "ctime": pubdate,
            "desc": self.fake.sentence(nb_words=40),
            "state": 0,
            "duration": randint(5, 3600),
            "rights": {},
            "owner": {
                "mid": randint(1, 1e10),
                "name": self.fake.name(),
                "face": f"https://i2.hdslb.com/bfs/face/{self.random_hex(40)}.jpg",
            },
            "stat": {
                "aid": aid,
                "view": randint(0, 1e5),
                "danmaku": randint(0, 1e3),
                "reply": randint(0, 1e2),
                "favorite": randint(0, 1e3),
                "coin": randint(0, 1e3),
                "share": randint(0, 1e3),
                "now_rank": 0,
                "his_rank": 0,
                "like": randint(0, 1e3),
                "dislike": randint(0, 1e3),
                "vt": 0,
                "vv": 0,
            },
            "dynamic": self.fake.sentence(nb_words=10),
            "cid": randint(1, 1e10),
            "dimension": {},
            "short_link_v2": f"https://b23.tv/{bvid}",
            "up_from_v2": random.choice([8, 9, 19, 35, 36, 39]),
            "first_frame": f"http://i0.hdslb.com/bfs/storyff/{self.random_lower_ascii(32)}_firsti.jpg",
            "pub_location": self.fake.province(),
            "cover43": "",
            "bvid": bvid,
            "season_type": 0,
            "is_ogv": False,
            "ogv_info": None,
            "rcmd_reason": "",
            "enable_vt": 0,
            "ai_rcmd": None,
        }

        return res


class VideoPageAPIMocker:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=APP_ENVS["version"],
        )
        self.archive_generator = ArchiveGenerator()
        self.setup_routes()

    def page_info(self, tid: int, pn: Optional[int] = 1, ps: Optional[int] = 50):
        res = {
            "code": 0,
            "message": "0",
            "ttl": 1,
            "data": {
                "archives": [],
                "page": {"count": randint(1e4, 1e7), "num": pn, "size": ps},
            },
        }
        for i in range(ps):
            idx = pn * (ps - 1) + i
            archive = self.archive_generator.get(tid=tid, idx=idx)
            res["data"]["archives"].append(archive)
        return res

    def setup_routes(self):
        self.app.get(
            "/page_info",
            summary="Return video page info by: Region(tid), Page idx (pn), Page size (ps)",
        )(self.page_info)


app = VideoPageAPIMocker().app

if __name__ == "__main__":
    args = ArgParser(app_envs=APP_ENVS).args
    if args.reload:
        uvicorn.run("__main__:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run("__main__:app", host=args.host, port=args.port)

    # archive_generator = ArchiveGenerator()
    # tid = 95
    # pn, ps = 1, 50
    # idx = pn * (ps - 1)
    # res = archive_generator.get(tid=tid, idx=idx)
    # logger.mesg(pformat(res, indent=4, sort_dicts=False))

    # python -m apps.video_page_api_mocker
