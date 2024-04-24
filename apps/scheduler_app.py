import argparse
import pandas as pd
import requests
import sys
import uuid
import uvicorn

from pathlib import Path
from typing import Union, Optional

from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from tclogger import logger, OSEnver

from apps.arg_parser import ArgParser
from networks.proxy_pool import ProxyPool, ProxyBenchmarker
from configs.envs import SCHEDULER_APP_ENVS, WORKER_APP_ENVS


class SchedulerApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=SCHEDULER_APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=SCHEDULER_APP_ENVS["version"],
        )
        self.worker_app_endpoint = f"http://127.0.0.1:{WORKER_APP_ENVS['port']}"
        self.setup_routes()

    def new_task(
        self,
        tid: int = Body(),
        pn: Optional[int] = Body(1),
        ps: Optional[int] = Body(50),
        mock: Optional[bool] = Body(True),
    ):
        worker_id = str(uuid.uuid4())
        logger.note(f"> New worker: {worker_id}")
        logger.mesg(f"> Params    : tid={tid}, pn={pn}, ps={ps}")
        # post to worker app endpoint
        url = f"{self.worker_app_endpoint}/get_page_info"
        data = {"tid": tid, "pn": pn, "ps": ps, "mock": mock}
        res = requests.get(url, params=data)
        res_data = res.json()
        logger.note(f"> Response  :")
        logger.mesg(res_data)
        return res_data

    class VideoInfoPostItem(BaseModel):
        code: int = Field(default=0)
        message: str = Field(default="0")
        ttl: int = Field(default=1)
        data: dict = Field(default={})

    def save_video_info(self, item: VideoInfoPostItem):
        data = item.data
        logger.note(f"Video info:")
        logger.mesg(data)

    def setup_routes(self):
        self.app.post(
            "/new_task",
            summary="Create new task by: Region(tid), Page idx (pn), Page size (ps)",
        )(self.new_task)

        self.app.post(
            "/save_video_info",
            summary="Save video info to database",
        )(self.save_video_info)


app = SchedulerApp().app

if __name__ == "__main__":
    args = ArgParser(app_envs=SCHEDULER_APP_ENVS).args
    if args.reload:
        uvicorn.run("__main__:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.scheduler_app
