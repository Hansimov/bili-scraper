from pathlib import Path

from tclogger import logger, shell_cmd

from configs.envs import VIDEOS_ENVS, COOKIES_DICT


class VideoDownloader:
    def __init__(self):
        pass

    def get_cmd_args(self, bvid: str, mid: int = 0):
        self.bbdown = "BBDown"
        self.user_videos_dir = Path(VIDEOS_ENVS["root"]) / f"{mid}"

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
        }
        self.cmd_args_str = " ".join(f"{k} {v}" for k, v in self.cmd_args.items())
        self.cmd_str = f'{self.bbdown} "{bvid}" {self.cmd_args_str}'
        return self.cmd_str

    def download(self, bvid: str, mid: int = 0):
        self.get_cmd_args(bvid, mid)
        logger.note(f"> Download video: [{bvid}]")
        logger.file(f"  - {self.user_videos_dir}")
        # logger.mesg(f"  * {self.cmd_str}")
        shell_cmd(self.cmd_str)


if __name__ == "__main__":
    bvid = "BV1Lm421V78u"
    mid = 946974
    donwloader = VideoDownloader()
    donwloader.download(bvid, mid)

    # python -m workers.video_downloader
