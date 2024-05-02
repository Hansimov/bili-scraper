import asyncio
from random import randint
import requests
import uvicorn

from fastapi import FastAPI, Body
from random import randint
from tclogger import logger
from typing import Optional


from apps.arg_parser import ArgParser
from configs.envs import WORKER_APP_ENVS, VIDEO_PAGE_API_MOCKER_ENVS, PROXY_APP_ENVS
from networks.constants import REQUESTS_HEADERS, GET_VIDEO_PAGE_API, REGION_CODES


class WorkerParamsGenerator:
    def __init__(self, region_codes: list[str] = [], mock: bool = False):
        self.mock = mock
        self.region_codes = region_codes

        self.init_tids()

    def init_tids(self):
        self.tid_idx = 0
        main_regions = [REGION_CODES[region_code] for region_code in self.region_codes]
        self.regions = [
            region
            for main_region in main_regions
            for region in main_region["children"].values()
        ]
        self.tids = [region["tid"] for region in self.regions]
        self.is_current_region_exhausted = False
        self.pn = 0
        self.tid = self.get_tid()
        logger.note(f"> Regions: {self.region_codes} => {len(self.tids)} sub-regions")

    def get_region(self):
        if self.tid_idx < len(self.regions):
            return self.regions[self.tid_idx]
        else:
            return {}

    def get_tid(self):
        if self.tid_idx < len(self.tids):
            return self.tids[self.tid_idx]
        else:
            return -1

    async def flag_current_region_exhausted(self):
        self.is_current_region_exhausted = True

    async def is_terminated(self):
        if self.tid == -1 and self.pn == -1:
            return True
        return False

    async def next(self):
        if not self.is_current_region_exhausted:
            self.pn += 1
        else:
            self.tid_idx += 1
            if self.tid_idx < len(self.regions):
                self.tid = self.get_tid()
                self.pn = 1
            else:
                self.tid = -1
                self.pn = -1
            self.is_current_region_exhausted = False
        return self.tid, self.pn


class Worker:
    def __init__(
        self,
        generator: WorkerParamsGenerator,
        lock: asyncio.Lock,
        wid: int = -1,
        proxy: str = None,
        mock: bool = False,
    ):
        self.wid = wid
        self.generator = generator
        self.lock = lock
        self.proxy = proxy
        self.mock = mock
        self.active = False

    async def get_proxy(self):
        proxy_api = f"http://127.0.0.1:{PROXY_APP_ENVS['port']}/get_proxy"
        params = {"mock": self.mock}
        try:
            res = requests.get(proxy_api, params=params)
            if res.status_code == 200:
                proxy = res.json().get("server")
            else:
                proxy = None
        except Exception as e:
            proxy = None

        if proxy:
            logger.success(f"> New worker {self.wid} with proxy: [{proxy}]")
            self.active = True
        else:
            logger.warn(f"> Failed to create new worker as no proxy")
            self.active = False

        self.proxy = proxy

    def get_page(self, tid: int, pn: int, ps: int = 50):
        proxy = self.proxy
        mock = self.mock

        if proxy:
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        else:
            proxies = None

        if mock:
            url = f"http://127.0.0.1:{VIDEO_PAGE_API_MOCKER_ENVS['port']}/page_info"
            proxies = None
        else:
            url = GET_VIDEO_PAGE_API

        params = {"tid": tid, "pn": pn, "ps": ps}

        try:
            res = requests.get(
                url, headers=REQUESTS_HEADERS, params=params, proxies=proxies, timeout=5
            )
            if res.status_code == 200:
                res_json = res.json()
            else:
                res_json = {
                    "code": res.status_code,
                    "message": res.text,
                    "ttl": 1,
                    "data": {
                        "archives": [],
                        "page": {"count": randint(1e4, 1e7), "num": pn, "size": ps},
                    },
                }
        except Exception as e:
            res_json = {
                "code": -1,
                "message": str(e),
                "ttl": 1,
                "data": {
                    "archives": [],
                    "page": {"count": randint(1e4, 1e7), "num": pn, "size": ps},
                },
            }
        return res_json

    async def run(self):
        if not self.proxy:
            async with self.lock:
                await self.get_proxy()

        while True:
            if not self.active:
                break

            async with self.lock:
                if await self.generator.is_terminated():
                    self.active = False
                    break

            async with self.lock:
                tid, pn = await self.generator.next()

            region_name = self.generator.get_region().get("name", "Unknown")
            logger.note(
                f"> GET: wid={self.wid}, tid={tid}, pn={pn}, region={region_name}",
                end=" => ",
            )
            if tid == -1 and pn == -1:
                logger.success(f"[Finished]")
                break

            res_json = self.get_page(tid=tid, pn=pn)
            archives = res_json.get("data", {}).get("archives", [])

            if len(archives) == 0:
                async with self.lock:
                    await self.generator.flag_current_region_exhausted()

            res_code = res_json.get("code", -1)

            if res_code == 0:
                logger.success(f"[code={res_code}]", end=" ")
                if len(archives) > 0:
                    logger.mesg(f"<{len(archives)} videos>")
                else:
                    logger.warn(f"<0 video>")
            else:
                logger.warn(f"[code={res_code}]")
                logger.warn(f"{res_json.get('message', '')}")

            await asyncio.sleep(randint(0,1))


class WorkersApp:
    def __init__(self):
        self.app = FastAPI(
            docs_url="/",
            title=WORKER_APP_ENVS["app_name"],
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            version=WORKER_APP_ENVS["version"],
        )
        self.setup_routes()
        self.workers = []
        self.generator = None
        self.lock = asyncio.Lock()
        logger.success(
            f"> {WORKER_APP_ENVS['app_name']} - v{WORKER_APP_ENVS['version']}"
        )

    async def create_workers(
        self, max_workers: Optional[int] = Body(20), mock: Optional[bool] = Body(True)
    ):
        self.workers = []
        for i in range(max_workers):
            worker = Worker(wid=i, generator=self.generator, lock=self.lock, mock=mock)
            self.workers.append(worker)

    async def start(
        self,
        region_codes: Optional[list[str]] = Body(["game", "knowledge", "tech"]),
        max_workers: Optional[int] = Body(20),
        mock: Optional[bool] = Body(True),
    ):
        if not self.generator:
            self.generator = WorkerParamsGenerator(region_codes=region_codes, mock=mock)
        await self.create_workers(max_workers=max_workers, mock=mock)

        tasks = [worker.run() for worker in self.workers]
        await asyncio.gather(*tasks)

    def stop(self):
        for worker in self.workers:
            worker.active = False
        logger.success(f"> All workers stopped")

    def setup_routes(self):
        self.app.post(
            "/start",
            summary="Start new workers",
        )(self.start)

        self.app.post(
            "/stop",
            summary="Stop all workers",
        )(self.stop)


app = WorkersApp().app

if __name__ == "__main__":
    args = ArgParser(app_envs=WORKER_APP_ENVS).args

    if args.reload:
        uvicorn.run("__main__:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.worker_app
