import markdown2
import pandas as pd
import sys
import uuid
import uvicorn

from pathlib import Path
from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from tclogger import logger, OSEnver


from configs.envs import VIDEO_PAGE_API_MOCKER_ENVS as APP_ENVS

from apps.arg_parser import ArgParser


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
