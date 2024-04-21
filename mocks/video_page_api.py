import pandas as pd
import random
import string

import uuid
import uvicorn

from datetime import datetime
from faker import Faker
from pathlib import Path
from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from tclogger import logger, OSEnver


from configs.envs import VIDEO_PAGE_API_MOCKER_ENVS as APP_ENVS

from apps.arg_parser import ArgParser


class ArchieveGenerator:
    def __init__(self):
        self.init_faker()

    def init_faker(self):
        fake = Faker()
        fake.seed_locale("zh_CN")
        self.fake = fake

    def get(self, rid: int, idx: int = 0):
        seed = rid * 1e9 + idx
        self.fake.seed_instance(seed)
        random.seed(seed)
        res = {
            "aid": random.randint(1000000000, 2000000000),
            "videos": random.randint(1, 10),
            "tid": rid,
            "tname": "".join(self.fake.word()),
            "copyright": random.randint(0, 1),
            "pic": f"http://random.image/{random.randint(100, 999)}.jpg",
            "title": "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            ),
            "pubdate": int(datetime.now().timestamp()),
            "ctime": int(datetime.now().timestamp()),
            "desc": "-",
            "state": 0,
            "duration": random.randint(10, 100),
            "rights": {},
            "owner": {
                "mid": random.randint(100000000, 200000000),
                "name": "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=5)
                ),
                "face": f"https://random.face/{random.randint(100, 999)}.jpg",
            },
            "stat": {
                "aid": random.randint(1000000000, 2000000000),
                "view": random.randint(0, 10000),
                "danmaku": random.randint(0, 1000),
                "reply": random.randint(0, 1000),
                "favorite": random.randint(0, 1000),
                "coin": random.randint(0, 1000),
                "share": random.randint(0, 1000),
                "now_rank": random.randint(0, 100),
                "his_rank": random.randint(0, 100),
                "like": random.randint(0, 1000),
                "dislike": random.randint(0, 1000),
                "vt": 0,
                "vv": 0,
            },
            "dynamic": "",
            "cid": random.randint(1000000000, 2000000000),
            "dimension": {
                "width": random.randint(100, 1000),
                "height": random.randint(100, 2000),
                "rotate": 0,
            },
            "short_link_v2": f"https://b23.tv/{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}",
            "up_from_v2": random.randint(10, 50),
            "first_frame": f"http://http://i0.hdslb.com/bfs/storyff/{random.randint(100, 999)}.jpg",
            "pub_location": "".join(
                random.choices(string.ascii_uppercase + string.digits, k=5)
            ),
            "cover43": "",
            "bvid": "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            ),
            "season_type": 0,
            "is_ogv": False,
            "ogv_info": None,
            "rcmd_reason": "",
            "enable_vt": 0,
            "ai_rcmd": None,
        }


class VideoPageAPIMocker:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=APP_ENVS["version"],
        )
        self.setup_routes()

    def page_info(self):
        return {}

    def setup_routes(self):
        self.app.post(
            "/page_info",
            summary="Return video page info by: Region(tid), Page idx (pn), Page size (ps)",
        )(self.page_info)


app = VideoPageAPIMocker().app

if __name__ == "__main__":
    args = ArgParser(app_envs=APP_ENVS).args
    uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m mocks.video_page_api
