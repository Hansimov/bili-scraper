import pandas as pd
import requests
import threading
import uvicorn

from datetime import datetime
from fastapi import FastAPI, Body
from pydantic import BaseModel
from tclogger import logger
from typing import Optional, List, Literal

from apps.arg_parser import ArgParser
from configs.envs import PROXY_APP_ENVS, WORKER_APP_ENVS
from networks.proxy_pool import ProxyPool, ProxyBenchmarker


class ProxiesDatabase:
    COLUMN_DTYPES = {
        "server": str,
        "latency": float,
        "last_checked": "datetime64[ns]",
        "success_rate": float,
    }
    COLUMNS = list(COLUMN_DTYPES.keys())
    INDEX_COLUMNS = ["server"]

    def __init__(self):
        self.init_df()
        self.lock = threading.Lock()

    def init_df(self):
        # create a pandas dataframe to store good proxies
        # columns: server(ip:port):str, latency:float, last_checked:datetime
        self.df_good = self.default_df()
        self.df_bad = self.default_df()
        self.df_using = self.default_df()

    def default_df(self):
        df = pd.DataFrame(columns=self.COLUMNS).astype(self.COLUMN_DTYPES)
        df = df.set_index(self.INDEX_COLUMNS)
        return df

    def add_proxy(
        self,
        server: str,
        latency: float,
        status: Literal["good", "bad", "using"] = "good",
        success_rate: float = -1,
    ):
        new_item = {
            "latency": latency,
            "last_checked": pd.Timestamp.now(),
            "success_rate": success_rate,
        }
        new_row = pd.Series(new_item)

        with self.lock:
            if status == "good":
                logger.success(
                    f"  + Add good proxy: [{latency:.2f}s] [{success_rate:.2f}] {server}"
                )
                self.df_good.loc[server] = new_row
            elif status == "bad":
                logger.back(f"  x Add bad proxy: {server}")
                self.df_bad.loc[server] = new_row
            elif status == "using":
                logger.note(f"  + Add using proxy: {server}")
                self.df_using.loc[server] = new_row
            else:
                logger.warn(f"  ? Unknown proxy status: {status}")

    def remove_proxy(
        self, server: str, status: Literal["good", "bad", "using"] = "good"
    ):
        with self.lock:
            if status == "good":
                if server in self.df_good.index:
                    self.df_good.drop(index=server, inplace=True)
                    logger.warn(f"- Remove good proxy: {server}")
            elif status == "bad":
                if server in self.df_bad.index:
                    self.df_bad.drop(index=server, inplace=True)
                    logger.warn(f"- Remove bad proxy: {server}")
            elif status == "using":
                if server in self.df_using.index:
                    self.df_using.drop(index=server, inplace=True)
                    logger.warn(f"- Remove using proxy: {server}")
            else:
                logger.warn(f"Unknown proxy status: {status}")

        return {"server": server, "status": "removed"}

    def add_good_proxy(self, server: str, latency: float, success_rate: float):
        self.add_proxy(server, latency, "good", success_rate)

    def add_bad_proxy(self, server: str):
        self.add_proxy(server, -1, "bad", -1)

    def add_using_proxy(self, server: str, latency: float, success_rate: float):
        self.add_proxy(server, latency, "using", success_rate)

    def remove_good_proxy(self, server: str):
        return self.remove_proxy(server, "good")

    def remove_bad_proxy(self, server: str):
        return self.remove_proxy(server, "bad")

    def remove_using_proxy(self, server: str):
        return self.remove_proxy(server, "using")

    def get_good_proxies_list(self) -> List[str]:
        return self.df_good.index.tolist()

    def get_bad_proxies_list(self) -> List[str]:
        return self.df_bad.index.tolist()

    def get_using_proxies_list(self) -> List[str]:
        return self.df_using.index.tolist()

    def empty_good_proxies(self):
        old_good_proxies = self.get_good_proxies_list()
        self.df_good = self.default_df()
        logger.success(f"+ Empty {len(old_good_proxies)} good proxies")
        return old_good_proxies

    def empty_bad_proxies(self):
        old_bad_proxies = self.get_bad_proxies_list()
        self.df_bad = self.default_df()
        logger.success(f"+ Empty {len(old_bad_proxies)} bad proxies")
        return old_bad_proxies

    def empty_using_proxies(self):
        old_using_proxies = self.get_using_proxies_list()
        self.df_using = self.default_df()
        logger.success(f"+ Empty {len(old_using_proxies)} using proxies")
        return old_using_proxies


class ProxyApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=PROXY_APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=PROXY_APP_ENVS["version"],
        )
        self.db = ProxiesDatabase()
        self.last_refresh_time = None
        self.is_refreshing_proxies = False
        self.trigger_refresh_proxies_min_goods = 3
        self.trigger_refresh_proxies_min_seconds = 30
        self.empty_bad_proxies_time = None
        self.trigger_empty_bad_proxies_min_seconds = 300
        self.setup_routes()
        logger.success(f"> {PROXY_APP_ENVS['app_name']} - v{PROXY_APP_ENVS['version']}")

    class RefreshProxiesPostItem(BaseModel):
        refresh_good: Optional[bool] = False

    def refresh_proxies(self, item: RefreshProxiesPostItem):
        start_refresh_time = datetime.now()
        start_refresh_time_str = start_refresh_time.strftime("%Y-%m-%d %H:%M:%S")
        logger.note(f"> Refreshing proxies", end=" ")
        logger.mesg(f"[{start_refresh_time_str}]")
        self.is_refreshing_proxies = True
        proxies = ProxyPool().get_proxies_list()
        proxies = list(set(proxies))
        benchmarker = ProxyBenchmarker()
        old_good_proxies = self.db.get_good_proxies_list()
        old_bad_proxies = self.db.get_bad_proxies_list()
        old_using_proxies = self.db.get_using_proxies_list()
        new_proxies = list(
            set(proxies)
            - set(old_good_proxies)
            - set(old_bad_proxies)
            - set(old_using_proxies)
        )
        if item.refresh_good:
            proxies_to_test = list(set(new_proxies + old_good_proxies))
            self.db.empty_good_proxies()
            gs = "Test"
        else:
            proxies_to_test = new_proxies
            gs = "Keep"
        logger.file(
            f"  * New  proxies (Test): {len(new_proxies)}\n"
            f"  * Good proxies ({gs}): {len(old_good_proxies)}\n"
            f"  * Bad  proxies (Skip): {len(old_bad_proxies)}"
        )
        benchmarker.batch_test_proxy(
            proxies_to_test,
            good_callback=self.db.add_good_proxy,
            bad_callback=self.db.add_bad_proxy,
        )
        good_proxies_count = len(self.db.get_good_proxies_list())
        bad_proxies_count = len(self.db.get_bad_proxies_list())
        total_proxies_count = good_proxies_count + bad_proxies_count
        if self.empty_bad_proxies_time is None:
            self.empty_bad_proxies_time = datetime.now()
        self.last_refresh_time = datetime.now()
        last_refresh_time_str = self.last_refresh_time.strftime("%Y-%m-%d %H:%M:%S")
        self.is_refreshing_proxies = False
        logger.success(good_proxies_count, end="")
        logger.note(f"/{total_proxies_count}", end=" ")
        logger.mesg(f"[{last_refresh_time_str}]")
        res = {
            "total": total_proxies_count,
            "usable": good_proxies_count,
            "status": "refreshed",
        }

        if good_proxies_count > self.trigger_refresh_proxies_min_goods:
            self.resume_workers(
                num=good_proxies_count - self.trigger_refresh_proxies_min_goods
            )

        return res

    # ANCHOR[id=get_proxy]
    def get_proxy(self, mock: Optional[bool] = False):
        if mock:
            res = {
                "server": "mock",
                "latency": 0.0,
                "success_rate": 1.0,
                "status": "ok",
            }
        else:
            # Get the proxy with highest success_rate and lowest latency,
            # and not in using list
            good_rows = self.db.df_good.sort_values(
                by=["success_rate", "latency"], ascending=[False, True]
            )
            if good_rows.empty:
                logger.warn(f"> No usable good proxy")
                res = {
                    "server": "",
                    "latency": -1,
                    "success_rate": -1,
                    "status": "error",
                }
            else:
                res = {
                    "server": good_rows.index[0],
                    "latency": good_rows.iloc[0]["latency"],
                    "success_rate": good_rows.iloc[0]["success_rate"],
                    "status": "ok",
                }
                self.db.add_using_proxy(
                    res["server"], res["latency"], res["success_rate"]
                )
                self.db.remove_good_proxy(res["server"])

        logger.success(
            f"> Get proxy: [{res['status']}] {res['server']}, {res['latency']:.2f}s, {res['success_rate']*100}%"
        )

        # trigger refresh_proxies if requirements met
        need_to_refresh_proxies = False
        now = datetime.now()
        if self.last_refresh_time:
            last_refresh_time_delta_seconds = (
                now - self.last_refresh_time
            ).total_seconds()
            need_to_refresh_proxies = (
                (not self.is_refreshing_proxies)
                and len(self.db.get_good_proxies_list())
                < self.trigger_refresh_proxies_min_goods
                and (
                    last_refresh_time_delta_seconds
                    >= self.trigger_refresh_proxies_min_seconds
                )
            )
        else:
            need_to_refresh_proxies = not self.is_refreshing_proxies

        if need_to_refresh_proxies:
            logger.note(f"> refresh_proxies triggered by get_proxy")
            if self.empty_bad_proxies_time:
                last_empty_bad_proxies_time_delta_seconds = (
                    now - self.empty_bad_proxies_time
                ).total_seconds()
                if (
                    last_empty_bad_proxies_time_delta_seconds
                    >= self.trigger_empty_bad_proxies_min_seconds
                ):
                    self.db.empty_bad_proxies()
                    self.empty_bad_proxies_time = datetime.now()
            self.refresh_proxies(self.RefreshProxiesPostItem())
            # TODO: the worker that triggers refresh_proxies would get invalid proxy,
            # as the res is not re-fetched from the refreshed new proxies

        return res

    class DropProxyPostItem(BaseModel):
        server: str = Body(default="", description="Proxy server to drop")

    # ANCHOR[id=drop_proxy]
    def drop_proxy(self, item: DropProxyPostItem):
        server = item.server
        logger.note(f"> Drop proxy: {server}")
        self.db.remove_using_proxy(server)
        self.db.remove_good_proxy(server)
        self.db.add_bad_proxy(server)
        logger.success(f"+ Dropped proxy: {server}")
        logger.note(f"  ({len(self.db.get_using_proxies_list())} using proxies)")
        logger.mesg(f"  ({len(self.db.get_good_proxies_list())} good proxies left)")
        res = {
            "server": server,
            "status": "dropped",
        }
        return res

    # ANCHOR[id=reset_using_proxies]
    def reset_using_proxies(self, flag_as_good: Optional[bool] = Body(True)):
        if flag_as_good:
            self.db.df_good = pd.concat(
                [self.db.df_good, self.db.df_using], sort=False
            ).drop_duplicates()
            logger.note(
                f"> Flag {len(self.db.get_good_proxies_list())} using proxies as good"
            )
        old_using_proxies = self.db.empty_using_proxies()
        message = f"Reset {len(old_using_proxies)} using proxies"
        logger.mesg(f"> {message}")
        res = {
            "status": "ok",
            "message": message,
        }
        return res

    def resume_workers(self, num: int = -1):
        # LINK apps/worker_app.py#resume
        worker_resume_api = f"http://127.0.0.1:{WORKER_APP_ENVS['port']}/resume"
        logger.note(f"> Resuming workers")
        try:
            res = requests.post(worker_resume_api, json={"num": num})
            data = res.json()
        except Exception as e:
            data = {"status": "error", "message": str(e), "count": -1}
        logger.mesg(f"√ Resume workers: [{data.get('status')}] {data.get('count')}")
        return data

    def setup_routes(self):
        self.app.get(
            "/get_proxy",
            summary="Get a usable proxy",
        )(self.get_proxy)

        self.app.post(
            "/drop_proxy",
            summary="Drop a proxy",
        )(self.drop_proxy)

        self.app.post(
            "/reset_using_proxies",
            summary="Reset using proxies",
        )(self.reset_using_proxies)

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
