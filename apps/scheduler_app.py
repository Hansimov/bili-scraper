import argparse
import markdown2
import pandas as pd
import sys
import uvicorn

from pathlib import Path
from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from tclogger import logger, OSEnver

from networks.proxy_pool import ProxyPool, ProxyBenchmarker
from configs.envs import SCHEDULER_APP_ENVS


class SchedulerApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=SCHEDULER_APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=SCHEDULER_APP_ENVS["version"],
        )
        self.setup_routes()

    class VideoInfoPostItem(BaseModel):
        code: int = Field(default=0)
        message: str = Field(default="0")
        ttl: int = Field(default=1)
        data: dict = Field(default={})

    def save_video_info(self, item: VideoInfoPostItem):
        data = item.data
        logger.note(f"Video info:")
        logger.mesg(data)

    def next_task(self):
        pass

    def setup_routes(self):
        self.app.post(
            "/save_video_info",
            summary="Save video info to database",
        )(self.save_video_info)

        self.app.post(
            "/next_task",
            summary="Determine next task by: Region(tid), Page idx (pn), Page size (ps)",
        )(self.next_task)


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgParser, self).__init__(*args, **kwargs)

        self.add_argument(
            "-s",
            "--host",
            type=str,
            default=SCHEDULER_APP_ENVS["host"],
            help=f"Host ({SCHEDULER_APP_ENVS['host']}) for {SCHEDULER_APP_ENVS['app_name']}",
        )
        self.add_argument(
            "-p",
            "--port",
            type=int,
            default=SCHEDULER_APP_ENVS["port"],
            help=f"Port ({SCHEDULER_APP_ENVS['port']}) for {SCHEDULER_APP_ENVS['app_name']}",
        )

        self.args = self.parse_args(sys.argv[1:])


app = SchedulerApp().app

if __name__ == "__main__":
    args = ArgParser().args
    uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.scheduler_app
