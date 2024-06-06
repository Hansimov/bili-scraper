import json
import requests
import shutil
import time

from math import ceil
from pathlib import Path
from tclogger import logger
from termcolor import colored
from tqdm import tqdm

from configs.envs import LOG_ENVS, COOKIES
from networks.wbi import ParamsWBISigner


class UserWorker:
    def __init__(self, mid: int = None):
        self.url = "https://api.bilibili.com/x/space/wbi/arc/search"
        self.mid = mid
        self.log_file = Path(__file__).parents[1] / "logs" / LOG_ENVS["user"]
        self.save_root = Path(__file__).parents[1] / "data" / "user" / f"{self.mid}"

    def get_json_filename(self, pn: int = 1, ps: int = 30):
        return f"videos_pn_{pn}_ps_{ps}.json"

    def save_to_json(self, res: dict, json_filename: str, overwrite: bool = True):
        save_path = self.save_root / json_filename
        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as wf:
            json.dump(res, wf, ensure_ascii=False, indent=4)
        logger.success(f"+ Videos info saved:")
        logger.file(f"  * {save_path}")

    def get_videos_info(
        self,
        pn: int = 1,
        ps: int = 5,
        save_json: bool = True,
        overwrite: bool = True,
        verbose: bool = False,
    ):
        logger.enter_quiet(not verbose)

        signer = ParamsWBISigner()
        headers = signer.headers
        headers["Cookie"] = COOKIES

        mid_str = colored(f"{self.mid}", "blue")
        pn_str = colored(f"{pn}", "blue")
        ps_str = colored(f"{ps}", "blue")

        video_params_str = f"mid={mid_str}, pn={pn_str}, ps={ps_str}"

        logger.note(f"> Get signed params: {video_params_str}")
        params = {"mid": self.mid, "pn": pn, "ps": ps}
        signed_params = signer.run(params)

        logger.note(f"> Get videos info: {video_params_str}")

        res_dict = None
        try:
            res = requests.get(self.url, headers=headers, params=signed_params)
            res_dict = res.json()
            if save_json:
                logger.note(f"> Save videos info to json: {video_params_str}")
                json_filename = self.get_json_filename(pn, ps)
                self.save_to_json(
                    res=res_dict, json_filename=json_filename, overwrite=overwrite
                )
        except Exception as e:
            logger.warn(f"× Error: {e}")

        logger.exit_quiet(not verbose)

        return res_dict

    def get_all_videos_info(
        self, start_pn: int = 1, ps: int = 5, remove_old: bool = False
    ):
        logger.note(f"> Fetching all videos info for mid={self.mid}")

        if remove_old and self.save_root.exists():
            shutil.rmtree(self.save_root)

        # get total videos count and page num
        try:
            res_dict = self.get_videos_info(pn=1, ps=ps)
            data = res_dict.get("data", {})
            videos_total_count = data.get("page", {}).get("count", 0)
            vlist = data.get("list", {}).get("vlist", [])
            page_num = ceil(videos_total_count / ps)
            author = vlist[0].get("author", "Unknown")
            time.sleep(0.5)
        except Exception as e:
            logger.warn(f"x Error: {e}")

        # get all pages of current user
        logger.file(f"  - {page_num} pages, {videos_total_count} videos by {author}")
        for pn in tqdm(range(start_pn, page_num + 1)):
            res_dict = self.get_videos_info(pn=pn, ps=ps)
            vlist = data.get("list", {}).get("vlist", [])
            time.sleep(0.5)

    def run(self, pn: int = 1, ps: int = 5):
        self.get_all_videos_info(ps=50, remove_old=True)


if __name__ == "__main__":
    # mid = 946974 # 影视飓风
    mid = 1629347259  # 红警HBK08
    worker = UserWorker(mid=mid)
    worker.run()

    # python -m workers.user_worker