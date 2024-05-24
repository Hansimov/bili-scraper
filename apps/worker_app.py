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

    def create_workers(
        self, max_workers: Optional[int] = Body(40), mock: Optional[bool] = Body(True)
    ):
        self.reset_using_proxies()
        self.workers: List[Worker] = []
        for i in range(max_workers):
            worker = Worker(wid=i, generator=self.generator, lock=self.lock, mock=mock)
            self.workers.append(worker)

    def start(
        self,
        region_codes: Optional[list[str]] = Body(["knowledge", "tech"]),
        max_workers: Optional[int] = Body(40),
        start_tid: Optional[int] = Body(-1),
        start_pn: Optional[int] = Body(-1),
        mock: Optional[bool] = Body(False),
    ):
        if not self.generator:
            self.generator = WorkerParamsGenerator(
                region_codes=region_codes,
                start_tid=start_tid,
                start_pn=start_pn,
                mock=mock,
            )
        self.max_workers = max_workers
        self.create_workers(max_workers=max_workers, mock=mock)

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
