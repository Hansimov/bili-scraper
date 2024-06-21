import json

from datetime import datetime
from tclogger import logger, shell_cmd
from pathlib import Path

from configs.envs import COOKIES_DICT, BILI_DATA_ROOT


class VideoDownloader:
    def calc_cmd_args(self):
        self.bbdown = "BBDown"
        self.user_videos_dir = BILI_DATA_ROOT / f"{self.mid}" / "videos"
        self.user_videos_meta_json = BILI_DATA_ROOT / f"{self.mid}" / "video_files.json"

        if not self.user_videos_dir.exists():
            self.user_videos_dir.mkdir(parents=True, exist_ok=True)

        self.cmd_args = {
            "--work-dir": f'"{self.user_videos_dir}"',
            "--cookie": f'"SESSDATA={COOKIES_DICT["SESSDATA"]}"',
            "--encoding-priority": "hevc",
            "--dfn-priority": '"720P 高清, 480P 清晰, 360P 流畅"',
            "--file-pattern": '"<bvid>"',
            "--multi-file-pattern": '"<bvid>_p<pageNumberWithZero>"',
            "--audio-ascending": "",
            "--download-danmaku": "",
            "--hide-streams": "",
        }
        self.cmd_args_str = " ".join(f"{k} {v}" for k, v in self.cmd_args.items())
        self.cmd_str = f'{self.bbdown} "{self.bvid}" {self.cmd_args_str}'
        return self.cmd_str

    def check_existed(self):
        if not self.user_videos_meta_json.exists():
            return False
        else:
            with open(self.user_videos_meta_json, "r") as rf:
                meta_dict = json.load(rf)
            video_item = meta_dict.get("videos", {}).get(self.bvid, {})
            if video_item.get("status", "") == "ok":
                existed_files = video_item.get("files", [])
                logger.mesg(
                    f"  * {len(existed_files)} files existed for bvid: [{self.bvid}]"
                )
                logger.file(f"  * {existed_files}")
                return True
        return False

    def save_meta_to_json(self):
        if not self.user_videos_meta_json.exists():
            meta_dict = {
                "mid": self.mid,
                "count": 0,
                "videos": {},
            }
        else:
            with open(self.user_videos_meta_json, "r") as rf:
                meta_dict = json.load(rf)

        bvid_files = sorted(list(self.user_videos_dir.glob(f"{self.bvid}*")))
        bvid_filnames = [f.name for f in bvid_files]

        if bvid_files:
            bvid_file_last_update_time = datetime.fromtimestamp(
                max([f.stat().st_mtime for f in bvid_files])
            ).strftime("%Y-%m-%d %H:%M:%S")

            meta_dict["videos"][self.bvid] = {
                "status": "ok",
                "files": bvid_filnames,
                "update_at": bvid_file_last_update_time,
            }
            meta_dict["count"] = len(meta_dict["videos"])
        else:
            logger.warn(f"> Videos missing for bvid: [{self.bvid}]")
            meta_dict["videos"][self.bvid] = {
                "status": "missing",
                "files": bvid_filnames,
                "update_at": "",
            }
            meta_dict["count"] = len(meta_dict["videos"])

        with open(self.user_videos_meta_json, "w", encoding="utf-8") as wf:
            json.dump(meta_dict, wf, ensure_ascii=False, indent=4)

        logger.success(f"+ Meta info saved for bvid: [{self.bvid}]")

    def download(
        self, bvid: str, mid: int = 0, update_meta_for_downloaded: bool = False
    ):
        self.bvid = bvid
        self.mid = mid
        self.calc_cmd_args()
        logger.note(f"> Download video: [{bvid}]")
        logger.file(f"  - {self.user_videos_dir}/{bvid}*")
        is_existed = self.check_existed()
        if not is_existed:
            shell_cmd(self.cmd_str)
        if not is_existed or update_meta_for_downloaded:
            self.save_meta_to_json()

        return not is_existed


if __name__ == "__main__":
    # bvid = "BV1Lm421V78u"
    bvid = "BV1hZ421g7xC"
    mid = 946974
    donwloader = VideoDownloader()
    donwloader.download(bvid, mid)

    # python -m workers.video_downloader
