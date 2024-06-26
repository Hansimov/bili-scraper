import concurrent.futures
import requests
import threading
import uvicorn

from fastapi import FastAPI, Body
from pydantic import BaseModel
from tclogger import logger
from typing import Optional, List

from apps.arg_parser import ArgParser
from configs.envs import WORKER_APP_ENVS, PROXY_APP_ENVS
from networks.sql import SQLOperator
from workers.worker import WorkerParamsGenerator, Worker


class WorkerApp:
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
        self.sql = None
        self.lock = threading.Lock()
        logger.success(
            f"> {WORKER_APP_ENVS['app_name']} - v{WORKER_APP_ENVS['version']}"
        )

    def reset_using_proxies(self):
        # LINK apps/proxy_app.py#reset_using_proxies
        api = f"http://127.0.0.1:{PROXY_APP_ENVS['port']}/reset_using_proxies"
        logger.note(f"> Resetting using proxies")
        try:
            res = requests.post(api)
            data = res.json()
        except Exception as e:
            data = {
                "status": "error",
                "message": str(e),
            }
        logger.mesg(f"√ Reset using proxies: {data.get('status')}")
        return data

    def create_workers(self, max_workers: Optional[int] = Body(40)):
        self.reset_using_proxies()
        self.workers: List[Worker] = []
        for i in range(max_workers):
            worker = Worker(
                wid=i, generator=self.generator, sql=self.sql, lock=self.lock
            )
            self.workers.append(worker)

    def start(
        self,
        region_groups: Optional[list[str]] = Body([]),
        region_codes: Optional[list[str]] = Body([]),
        region_tids: Optional[list[int]] = Body([]),
        max_workers: Optional[int] = Body(100),
        start_tid: Optional[int] = Body(-1),
        start_pn: Optional[int] = Body(-1),
        end_tid: Optional[int] = Body(-1),
        end_pn: Optional[int] = Body(-1),
        log_mids: Optional[list[int]] = Body([]),
    ):
        if not self.generator:
            self.generator = WorkerParamsGenerator(
                region_groups=region_groups,
                region_codes=region_codes,
                region_tids=region_tids,
                start_tid=start_tid,
                start_pn=start_pn,
                end_tid=end_tid,
                end_pn=end_pn,
                log_mids=log_mids,
            )
            log_str = (
                f"Get {len(self.generator.tids)} region tids:\n{self.generator.tids}"
            )
            self.generator.log_to_file(log_type="others", log_str=log_str)
        if not self.sql:
            self.sql = SQLOperator()
        self.max_workers = max_workers
        self.create_workers(max_workers=max_workers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker.run) for worker in self.workers]
            for future in concurrent.futures.as_completed(futures):
                future.result()

        return {"status": "started"}

    def stop(self):
        for worker in self.workers:
            worker.deactivate()
        logger.mesg(f"> All workers stopped")

    class ResumePostItem(BaseModel):
        num: Optional[int] = -1

    # ANCHOR[id=resume]
    def resume(self, item: ResumePostItem):
        num = item.num
        if num == -1:
            num = self.max_workers
        logger.note(f"> Resuming workers: {num}")
        resume_count = 0
        for worker in self.workers:
            if not worker.active:
                worker.activate()
                resume_count += 1
            if resume_count >= num:
                break
        logger.mesg(f"√ {resume_count} workers resumed")
        return {
            "status": "resumed",
            "count": resume_count,
        }

    def __del__(self):
        logger.note(f"> Shutting down: {WORKER_APP_ENVS['app_name']}")
        self.reset_using_proxies()

    def setup_routes(self):
        self.app.post(
            "/start",
            summary="Start new workers",
        )(self.start)

        self.app.post(
            "/stop",
            summary="Stop all workers",
        )(self.stop)

        self.app.post(
            "/resume",
            summary="Resume inactive workers",
        )(self.resume)


app = WorkerApp().app

if __name__ == "__main__":
    args = ArgParser(app_envs=WORKER_APP_ENVS).args

    if args.reload:
        uvicorn.run("__main__:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run("__main__:app", host=args.host, port=args.port)

    # python -m apps.worker_app
