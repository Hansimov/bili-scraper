import requests
import uvicorn

from fastapi import FastAPI, Body
from random import randint
from tclogger import logger
from typing import Optional


from apps.arg_parser import ArgParser
from configs.envs import WORKER_APP_ENVS, VIDEO_PAGE_API_MOCKER_ENVS
from networks.constants import GET_VIDEO_PAGE_API


class WorkerApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=WORKER_APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=WORKER_APP_ENVS["version"],
        )
        self.setup_routes()

    def get_page_info(
        self,
        tid: int,
        pn: Optional[int] = 1,
        ps: Optional[int] = 50,
        mock: Optional[bool] = False,
    ):
        if mock:
            video_page_api = (
                f"http://127.0.0.1:{VIDEO_PAGE_API_MOCKER_ENVS['port']}/page_info"
            )
            res = requests.get(
                video_page_api, params={"tid": tid, "pn": pn, "ps": ps}
            ).json()
        else:
            video_page_api = GET_VIDEO_PAGE_API
            res = {
                "code": 0,
                "message": "0",
                "ttl": 1,
                "data": {
                    "archives": [],
                    "page": {"count": randint(1e4, 1e7), "num": pn, "size": ps},
                },
            }
        return res

    def setup_routes(self):
        self.app.get(
            "/get_page_info",
            summary="Fetch video page info by: Region(tid), Page idx (pn), Page size (ps)",
        )(self.get_page_info)


app = WorkerApp().app

if __name__ == "__main__":
    args = ArgParser(app_envs=WORKER_APP_ENVS).args

    if args.reload:
        uvicorn.run("__main__:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.worker_app
