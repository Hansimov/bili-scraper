import pandas as pd
import uvicorn

from typing import Optional

from fastapi import FastAPI
from tclogger import logger

from apps.arg_parser import ArgParser
from configs.envs import PROXY_APP_ENVS
from networks.proxy_pool import ProxyPool, ProxyBenchmarker


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
        logger.success(f"> {PROXY_APP_ENVS['app_name']} - v{PROXY_APP_ENVS['version']}")

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

    def get_proxy(self, mock: Optional[bool] = False):
        logger.note(f"> Return a random proxy")
        if mock:
            res = {
                "server": "",
                "latency": 0.0,
                "status": "ok",
            }
        else:
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
            summary="Get a usable proxy",
        )(self.get_proxy)

        self.app.delete(
            "/del_proxy",
            summary="Delete a proxy",
        )(self.del_proxy)

        self.app.post(
            "/refresh_proxies",
            summary="Refresh IP Proxies with benchmarker",
        )(self.refresh_proxies)


app = ProxyApp().app

if __name__ == "__main__":
    args = ArgParser(app_envs=PROXY_APP_ENVS).args
    if args.reload:
        uvicorn.run("__main__:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.proxy_app
