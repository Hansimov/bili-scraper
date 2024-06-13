import json

from pathlib import Path

from tclogger import logger, shell_cmd

from configs.envs import VIDEOS_ENVS, COOKIES_DICT


class VideoDownloader:
    def calc_cmd_args(self):
        self.bbdown = "BBDown"
        self.user_videos_dir = Path(VIDEOS_ENVS["root"]) / f"{self.mid}"
        self.user_videos_meta_json = (
            Path(VIDEOS_ENVS["root"]) / f"{self.mid}" / "meta.json"
        )

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

    def check_cache(self):
        if not self.user_videos_meta_json.exists():
            return False
        else:
            with open(self.user_videos_meta_json, "r") as rf:
                meta_dict = json.load(rf)
            if meta_dict.get(self.bvid, {}).get("status", "") == "ok":
                cached_files = meta_dict.get(self.bvid, {}).get("files", [])
                logger.mesg(
                    f"  * {len(cached_files)} files cached for bvid: [{self.bvid}]"
                )
                logger.file(f"  * {cached_files}")
                return True
        return False

    def save_meta_to_json(self):
        if not self.user_videos_meta_json.exists():
            meta_dict = {}
        else:
            with open(self.user_videos_meta_json, "r") as rf:
                meta_dict = json.load(rf)

        files_start_with_bvid = sorted(
            [f.name for f in self.user_videos_dir.glob(f"{self.bvid}*")]
        )
        meta_dict[self.bvid] = {"status": "ok", "files": files_start_with_bvid}

        with open(self.user_videos_meta_json, "w", encoding="utf-8") as wf:
            json.dump(meta_dict, wf, ensure_ascii=False, indent=4)

        logger.success(f"+ meta json saved for bvid: [{self.bvid}]")

    def download(self, bvid: str, mid: int = 0):
        self.bvid = bvid
        self.mid = mid
        self.calc_cmd_args()
        logger.note(f"> Download video: [{bvid}]")
        logger.file(f"  - {self.user_videos_dir}/{bvid}*")
        is_cached = self.check_cache()
        if not is_cached:
            shell_cmd(self.cmd_str)
            self.save_meta_to_json()


if __name__ == "__main__":
    # bvid = "BV1Lm421V78u"
    bvid = "BV1hZ421g7xC"
    mid = 946974
    donwloader = VideoDownloader()
    donwloader.download(bvid, mid)

    # python -m workers.video_downloader
