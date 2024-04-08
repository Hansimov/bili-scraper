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
from configs.envs import PROXY_APP_ENVS


class ProxiesDatabase:
    def __init__(self):
        self.init_df()

    def init_df(self):
        # create a pandas dataframe to store good proxies
        # columns: server(ip:port):str, latency:float, last_checked:datetime
        self.column_dtypes = {
            "server": str,
            "latency": float,
            "last_checked": "datetime64[ns]",
        }
        self.columns = list(self.column_dtypes.keys())
        self.df = pd.DataFrame(columns=self.columns).astype(self.column_dtypes)

    def add_proxy(self, server: str, latency: float):
        logger.success(f"+ Add proxy: [{latency:.2f}s] {server}")
        new_item = {
            "server": [server],
            "latency": [latency],
            "last_checked": [pd.Timestamp.now()],
        }
        new_row = pd.DataFrame(new_item)
        self.df = pd.concat([self.df, new_row])


class ProxyApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=PROXY_APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=PROXY_APP_ENVS["version"],
        )
        self.db = ProxiesDatabase()
        self.setup_routes()

    def refresh_proxies(self):
        logger.note(f"> Refreshing proxies")
        proxies = ProxyPool().get_proxies_list()
        benchmarker = ProxyBenchmarker()
        benchmarker.batch_test_proxy(proxies, callback=self.db.add_proxy)
        res = {
            "total": len(proxies),
            "usable": len(self.db.df),
            "status": "refreshed",
        }
        return res

    def get_all_proxies(self):
        logger.note(f"> Return all proxies")

    def get_proxy(self):
        logger.note(f"> Return a random proxy")
        res = {
            "server": "test",
            "latency": 0.0,
            "status": "ok",
        }
        return res

    def del_proxy(self, server: str):
        logger.warn(f"> Delete proxy: {server}")
        res = {
            "server": server,
            "status": "deleted",
        }
        return res

    def setup_routes(self):
        self.app.get(
            "/all_proxies",
            summary="Get all proxies",
        )(self.get_all_proxies)

        self.app.get(
            "/get_proxy",
            summary="Get a proxy",
        )(self.get_proxy)

        self.app.delete(
            "/del_proxy",
            summary="Delete a proxy",
        )(self.del_proxy)

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
            default=PROXY_APP_ENVS["host"],
            help=f"Host ({PROXY_APP_ENVS['host']}) for {PROXY_APP_ENVS['app_name']}",
        )
        self.add_argument(
            "-p",
            "--port",
            type=int,
            default=PROXY_APP_ENVS["port"],
            help=f"Port ({PROXY_APP_ENVS['port']}) for {PROXY_APP_ENVS['app_name']}",
        )

        self.args = self.parse_args(sys.argv[1:])


app = ProxyApp().app

if __name__ == "__main__":
    args = ArgParser().args
    uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.proxy_app
