import json
import requests

from pathlib import Path
from tclogger import logger
from termcolor import colored

from configs.envs import LOG_ENVS, COOKIES
from networks.wbi import ParamsWBISigner


class UserWorker:
    def __init__(self, mid: int = None):
        self.url = "https://api.bilibili.com/x/space/wbi/arc/search"
        self.mid = mid
        self.log_file = Path(__file__).parents[1] / "logs" / LOG_ENVS["user"]
        self.save_root = Path(__file__).parents[1] / "data" / "user" / f"{self.mid}"

    def is_terminated(self):
        pass

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

    def get_videos_info(self, pn: int = 1, ps: int = 3, overwrite: bool = True):
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
        try:
            res = requests.get(self.url, headers=headers, params=signed_params)
            res_dict = res.json()
            logger.note(f"> Save videos info to json: {video_params_str}")
            json_filename = self.get_json_filename(pn, ps)
            self.save_to_json(
                res=res_dict, json_filename=json_filename, overwrite=overwrite
            )
        except Exception as e:
            logger.warn(f"× Error: {e}")

    def run(self, pn: int = 1, ps: int = 3):
        self.get_videos_info(pn=pn, ps=ps)


if __name__ == "__main__":
    worker = UserWorker(mid=946974)
    pn, ps = 1, 3
    worker.run(pn, ps)

    # python -m workers.user_worker
