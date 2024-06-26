import argparse
import json
import requests
import shutil
import sys
import time

from math import ceil
from pathlib import Path
from tclogger import logger
from termcolor import colored
from tqdm import tqdm

from configs.envs import LOG_ENVS, COOKIES, BILI_DATA_ROOT
from networks.wbi import ParamsWBISigner
from workers.video_downloader import VideoDownloader
from workers.video_details_fetcher import VideoDetailsFetcher


class UserWorker:
    def __init__(self, mid: int = None):
        self.url = "https://api.bilibili.com/x/space/wbi/arc/search"
        self.mid = mid
        self.log_file = BILI_DATA_ROOT / "logs" / LOG_ENVS["user"]
        self.save_root = BILI_DATA_ROOT / f"{self.mid}"
        self.video_pages_dir = self.save_root / "video_pages"
        self.video_pages_json = self.save_root / "video_pages.json"
        self.video_details_josn = self.save_root / "video_details.json"
        self.video_page_request_interval = 0.5

    def get_json_filename(self, pn: int = 1, ps: int = 30):
        return f"videos_pn_{pn}_ps_{ps}.json"

    def save_video_pages_to_json(
        self, res: dict, json_filename: str, overwrite: bool = True
    ):
        save_path = self.video_pages_dir / json_filename
        if not save_path.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as wf:
            json.dump(res, wf, ensure_ascii=False, indent=4)
        logger.success(f"+ Videos info saved:")
        logger.file(f"  * {save_path}")

    def fetch_videos_info(
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
                self.save_video_pages_to_json(
                    res=res_dict, json_filename=json_filename, overwrite=overwrite
                )
        except Exception as e:
            logger.warn(f"× Error: {e}")

        logger.exit_quiet(not verbose)

        return res_dict

    def fetch_all_videos_info(
        self, start_pn: int = 1, ps: int = 5, remove_old: bool = False
    ):
        logger.note(f"> Fetching all videos info for mid={self.mid}")
        if remove_old and self.video_pages_dir.exists():
            shutil.rmtree(self.video_pages_dir)

        # get total videos count and page num
        try:
            res_dict = self.fetch_videos_info(pn=1, ps=ps)
            data = res_dict.get("data", {})
            videos_total_count = data.get("page", {}).get("count", 0)
            vlist = data.get("list", {}).get("vlist", [])
            page_num = ceil(videos_total_count / ps)
            author = vlist[0].get("author", "Unknown")
            time.sleep(self.video_page_request_interval)
        except Exception as e:
            logger.warn(f"x Error: {e}")

        # get all pages of current user
        logger.file(f"  - {page_num} pages, {videos_total_count} videos by {author}")
        for pn in tqdm(range(start_pn, page_num + 1)):
            res_dict = self.fetch_videos_info(pn=pn, ps=ps)
            vlist = data.get("list", {}).get("vlist", [])
            time.sleep(self.video_page_request_interval)

    def summarize_all_videos_info(self):
        video_page_json_files = sorted(self.video_pages_dir.glob("*.json"))
        video_pages_dict = []
        for p in video_page_json_files:
            # logger.file(f"  - {f}")
            with open(p, "r", encoding="utf-8") as rf:
                rf_dict = json.load(rf)
                data = rf_dict.get("data", {})
                vlist = data.get("list", {}).get("vlist", [])
                video_pages_dict.extend(vlist)

        video_pages_dict = sorted(
            video_pages_dict, key=lambda v: v["created"], reverse=True
        )

        with open(self.video_pages_json, "w") as wf:
            json.dump(video_pages_dict, wf, ensure_ascii=False, indent=4)
        logger.success(f"+ Summary of video pages info saved at:")
        logger.file(f"  - {self.video_pages_json}")

    def get_all_bvids(self):
        if not self.video_pages_json.exists():
            return []
        bvids = []
        with open(self.video_pages_json, "r", encoding="utf-8") as rf:
            video_pages_dict = json.load(rf)
            for v in video_pages_dict:
                if v.get("bvid", ""):
                    bvids.append(v["bvid"])
        return bvids

    def download_all_videos(self):
        video_downloader = VideoDownloader()
        bvids = self.get_all_bvids()
        logger.note(f"> Download {len(bvids)} videos for mid={self.mid}")
        for bvid in tqdm(bvids):
            is_download = video_downloader.download(bvid, self.mid)
            if is_download:
                time.sleep(2)

    def fetch_all_videos_details(self, overwrite: bool = False):
        bvids = self.get_all_bvids()
        video_details_fetcher = VideoDetailsFetcher()
        logger.note(f"> Fetch {len(bvids)} videos details for mid={self.mid}")
        for bvid in tqdm(bvids):
            is_fetch = video_details_fetcher.fetch(
                bvid,
                mid=self.mid,
                overwrite=overwrite,
                restore_proxy_after_fetch=False,
            )
            if is_fetch:
                time.sleep(self.video_page_request_interval)
        video_details_fetcher.restore_proxy()

    def run(
        self,
        update_videos_pages: bool = False,
        download_videos: bool = False,
        fetch_videos_details: bool = False,
        overwrite_video_details: bool = False,
    ):
        if update_videos_pages or not self.video_pages_json.exists():
            self.fetch_all_videos_info(ps=50, remove_old=True)
            self.summarize_all_videos_info()
        else:
            logger.mesg("> Skip updating videos info:")
            logger.file(f"  - {self.video_pages_json}")

        if download_videos:
            self.download_all_videos()
        else:
            logger.mesg("> Skip downloading videos.")

        if fetch_videos_details:
            self.fetch_all_videos_details(overwrite=overwrite_video_details)
        else:
            logger.mesg("> Skip fetching videos details.")


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgParser, self).__init__(*args, **kwargs)
        self.add_argument(
            "-m",
            "--mid",
            type=int,
            help="User mid.",
        )
        self.add_argument(
            "-p",
            "--pages",
            action="store_true",
            help="Update all video info pages. If exists, overwrite.",
        )
        self.add_argument(
            "-v",
            "--videos",
            action="store_true",
            help="Download all videos. If some video exists, skip it.",
        )
        self.add_argument(
            "-d",
            "--details",
            action="store_true",
            help="Fetch all videos details. If some video details exist, skip it.",
        )
        self.add_argument(
            "-od",
            "--overwrite-details",
            action="store_true",
            help="Overwrite existing video details.",
        )

        self.args = self.parse_args(sys.argv[1:])


if __name__ == "__main__":
    args = ArgParser().args
    mid = args.mid or 946974  # 影视飓风
    # mid = 1629347259  # 红警HBK08
    worker = UserWorker(mid=mid)
    worker.run(
        update_videos_pages=args.pages,
        download_videos=args.videos,
        fetch_videos_details=args.details,
        overwrite_video_details=args.overwrite_details,
    )

    # Update all video info pages
    # python -m workers.user_worker -p

    # Download all videos
    # python -m workers.user_worker -v

    # Fetch all videos details
    # python -m workers.user_worker -d
    # python -m workers.user_worker -d -od

    # Update video info pages, download video and download details (overwrite)
    # python -m workers.user_worker -p -v -d -od
