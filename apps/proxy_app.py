import argparse
import markdown2
import sys
import uvicorn

from pathlib import Path
from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from tclogger import logger, OSEnver

from networks.proxy_pool import ProxyPool, ProxyBenchmarker


info_path = Path(__file__).parents[1] / "configs" / "info.json"
ENVER = OSEnver(info_path)["proxy_app"]


class ProxyApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=ENVER["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=ENVER["version"],
        )
        self.setup_routes()

    def refresh_proxies(self, latency: Optional[float] = 1.0):
        logger.note(f"> Refreshing proxies")

    def get_all_proxies(self):
        logger.note(f"> Return all proxies")

    def get_proxy(self, latency: Optional[float] = 1.0):
        logger.note(f"> Return a random proxy")

    def setup_routes(self):
        self.app.get(
            "/all_proxies",
            summary="Get all proxies",
        )(self.get_all_proxies)

        self.app.get(
            "/get_proxy",
            summary="Get a proxy",
        )(self.get_proxy)

        self.app.post(
            "/refresh_proxies",
            summary="Refresh IP Proxies with benchmarker",
        )(self.refresh_proxies)


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgParser, self).__init__(*args, **kwargs)

        self.add_argument(
            "-s",
            "--host",
            type=str,
            default=ENVER["host"],
            help=f"Host ({ENVER['host']}) for {ENVER['app_name']}",
        )
        self.add_argument(
            "-p",
            "--port",
            type=int,
            default=ENVER["port"],
            help=f"Port ({ENVER['port']}) for {ENVER['app_name']}",
        )

        self.args = self.parse_args(sys.argv[1:])


app = ProxyApp().app

if __name__ == "__main__":
    args = ArgParser().args
    uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.proxy_app
