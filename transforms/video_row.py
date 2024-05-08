import requests

from datetime import datetime
from tclogger import logger

from networks.constants import REQUESTS_HEADERS, GET_VIDEO_PAGE_API


class VideoInfoConverter:
    """
    - 视频 API 信息
      - https://socialsisteryi.github.io/bilibili-API-collect/docs/video/info.html#%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E8%AF%A6%E7%BB%86%E4%BF%A1%E6%81%AF-web%E7%AB%AF
    - 2020年B站番剧相关API整合
      - https://www.bilibili.com/read/cv5293665/
    """

    ID_COLUMNS = {
        "aid": int,  # video id
        "bvid": str,  # video BV id
        "cid": str,  # video part id
    }

    OWNER_COLUMNS = {
        "mid": int,  # owner id
        "name": str,  # owner name
        "face": str,  # owner avatar url
        "pub_location": str,  # location when publish video
    }

    STATS_COLUMNS = {
        "view": int,  # views count
        "danmaku": int,  # danmakus count
        "reply": int,  # replies count
        "favorite": int,  # favorites count
        "coin": int,  # coins count
        "share": int,  # shares count
        "like": int,  # likes count
        "dislike": int,  # dislikes count (no longer used)
        "now_rank": int,  # current rank
        "his_rank": int,  # historical highest rank
        "vt": int,  # Unknown, always 0
        "vv": int,  # same to "view"
    }

    META_COLUMNS = {
        "title": str,  # video title
        "pubdate": int,  # publish datetime (timestamp)
        "ctime": int,  # post datetime (timestamp)
        "duration": int,  # video duration (seconds)
        "desc": str,  # video description
        "dynamic": str,  # dynamic when (re)post video
        "videos": int,  # number of video parts
        "tid": int,  # region code
        "tname": str,  # region name
        "copyright": int,  # 1: original; 2: reposted
    }

    MEDIA_COLUMNS = {
        "pic": str,  # cover image url
        "short_link_v2": str,  # short b23.tv link
        "first_frame": str,  # first frame image url
        "cover43": str,  # NOT SURE: cover image url with 4:3 aspect ratio
    }

    OTHER_COLUMNS = {
        "rights": dict,  # rights
        "dimension": dict,  # dimension of video resolution
        "state": int,  # binary flag bits for video permissions and states, combined with OR
        "up_from_v2": int,  # NO SURE: seems to be the original region code before upgraded to api v2
        "season_type": int,  # season type
        "is_ogv": bool,  # is original generated video
        "ogv_info": dict,  # original generated video info
        "rcmd_reason": str,  # recommendation reason
        "enable_vt": int,  # enable vt
        "ai_rcmd": dict,  # ai recommendation
    }

    EXTRA_COLUMNS = {
        "inserted_at": int,
    }

    COLUMNS_SQL_MAP = {
        "pubdate": "timestamp",
        "ctime": "timestamp",
        "inserted_at": "timestamp",
    }
    COLUMNS_RENAME_MAP = {
        "desc": "description",
        "like": "thumb_up",
    }

    COLUMNS = {
        **ID_COLUMNS,
        **OWNER_COLUMNS,
        **STATS_COLUMNS,
        **META_COLUMNS,
        **MEDIA_COLUMNS,
        **OTHER_COLUMNS,
        **EXTRA_COLUMNS,
    }

    def __init__(self):
        self.rename_columns()

    def rename_columns(self):
        self.COLUMNS = {
            self.COLUMNS_RENAME_MAP.get(k, k): v for k, v in self.COLUMNS.items()
        }

    def flatten(self, video_info: dict):
        new_video_info = {}
        for k, v in video_info.items():
            if k in ["owner", "stat"]:
                new_video_info.update(v)
            else:
                new_video_info[k] = v
        return new_video_info

    def rename(self, video_info: dict):
        new_video_info = {}
        for k, v in video_info.items():
            if k in self.COLUMNS_RENAME_MAP:
                new_k = self.COLUMNS_RENAME_MAP[k]
                new_video_info[new_k] = v
            else:
                new_video_info[k] = v
        return new_video_info

    def get_now_timestamp(self):
        return int(datetime.now().timestamp())

    def to_sql_row(self, video_info: dict):
        new_video_info = video_info
        new_video_info = self.flatten(new_video_info)
        new_video_info = self.rename(new_video_info)
        new_video_info["inserted_at"] = self.get_now_timestamp()
        return new_video_info


if __name__ == "__main__":
    res = requests.get(
        GET_VIDEO_PAGE_API,
        headers=REQUESTS_HEADERS,
        params={"rid": 95, "pn": 1000, "ps": 50},
    )
    if res.status_code == 200:
        res_json = res.json()

    video_info_dict = res_json["data"]["archives"][0]

    converter = VideoInfoConverter()
    new_video_info = converter.to_sql_row(video_info_dict)
    logger.mesg(new_video_info)

    # python -m transforms.video_row
