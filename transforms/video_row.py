import json
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
        "insert_at": int,
    }

    COLUMNS_SQL_MAP = {
        "pubdate": "timestamptz",
        "ctime": "timestamptz",
        "insert_at": "timestamptz",
    }
    COLUMNS_RENAME_MAP = {
        "desc": "description",
        "like": "thumb_up",
        "videos": "video_parts",
    }
    COLUMNS_TO_IGNORE = [
        "face",
        "dislike",
        "vt",
        "vv",
        "dynamic",
        "short_link_v2",
        "cover43",
        *OTHER_COLUMNS.keys(),
    ]

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
        self.update_set_str = None

    def rename_columns(self):
        self.COLUMNS = {
            self.COLUMNS_RENAME_MAP.get(k, k): v for k, v in self.COLUMNS.items()
        }

    def create_update_set_str(self, sql_row: dict, primary_key: str = "bvid"):
        update_on_conflict_str = f" ON CONFLICT ({primary_key}) DO UPDATE SET "
        update_set_columns = [k for k in sql_row.keys() if k != primary_key]
        update_set_columns_str = ", ".join(
            [f"{k} = EXCLUDED.{k}" for k in update_set_columns]
        )
        self.update_set_str = f"{update_on_conflict_str}{update_set_columns_str}"
        return self.update_set_str

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

    def extra(self, video_info: dict):
        new_video_info = video_info
        new_video_info["insert_at"] = self.get_now_timestamp()
        return new_video_info

    def sort(self, video_info: dict):
        """Sort the keys in the order of self.COLUMNS"""
        new_video_info = {}
        for k in self.COLUMNS.keys():
            if k in video_info:
                new_video_info[k] = video_info[k]
            else:
                new_video_info[k] = None
        return new_video_info

    def ignore(self, video_info: dict):
        new_video_info = {
            k: v for k, v in video_info.items() if k not in self.COLUMNS_TO_IGNORE
        }
        return new_video_info

    def to_sql_row(self, video_info: dict):
        new_video_info = video_info
        for method in [self.flatten, self.rename, self.extra, self.sort, self.ignore]:
            new_video_info = method(new_video_info)
        return new_video_info

    def serialize_sql_row(self, sql_row: dict):
        new_sql_values = []
        for k, v in sql_row.items():
            if isinstance(v, dict):
                new_v = json.dumps(v)
            elif k in self.COLUMNS_SQL_MAP:
                if self.COLUMNS_SQL_MAP[k] == "timestamptz":
                    new_v = datetime.fromtimestamp(v)
                else:
                    new_v = v
            else:
                new_v = v

            # Fix Error: 'A string literal cannot contain NUL (0x00) characters.'
            if isinstance(v, str):
                new_v = new_v.replace("\x00", "")

            new_sql_values.append(new_v)
        new_sql_values = tuple(new_sql_values)
        return new_sql_values

    def to_sql_query_and_values(
        self,
        video_info: dict,
        table_name: str = "videos",
        is_many: bool = False,
        update_on_conflict: bool = True,
        primary_key: str = "bvid",
    ):
        """Basic module usage - Psycopg 2.9.9 documentation:
        - https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        - https://www.psycopg.org/docs/usage.html#adaptation-of-python-values-to-sql-types
        - https://www.psycopg.org/docs/usage.html#adapt-date
        """
        sql_row = self.to_sql_row(video_info)
        values_placeholders = ", ".join(["%s"] * len(sql_row))

        if not is_many:
            sql_query = f"INSERT INTO {table_name} VALUES ({values_placeholders})"
        else:
            sql_query = f"INSERT INTO {table_name} VALUES %s"

        if update_on_conflict:
            if not self.update_set_str:
                self.create_update_set_str(sql_row, primary_key)

            sql_query = f"{sql_query} {self.update_set_str}"

        sql_values = self.serialize_sql_row(sql_row)
        return sql_query, sql_values


if __name__ == "__main__":
    res = requests.get(
        GET_VIDEO_PAGE_API,
        headers=REQUESTS_HEADERS,
        params={"rid": 95, "pn": 1000, "ps": 50},
    )
    if res.status_code == 200:
        res_json = res.json()

    archives = res_json["data"]["archives"]
    converter = VideoInfoConverter()

    video_infos = []
    sql_values_list = []
    for i in range(3):
        video_info = archives[i]
        video_infos.append(video_info)

        logger.note("> Converting video info to SQL row:")
        sql_row = converter.to_sql_row(video_info)
        logger.mesg(sql_row)

        logger.note("> Converting video info to SQL query and values:")
        sql_query, sql_values = converter.to_sql_query_and_values(
            video_info, is_many=True
        )
        sql_values_list.append(sql_values)
        logger.mesg(sql_query)
        logger.mesg(sql_values)

    from networks.sql import SQLOperator

    logger.note("Inserting video info:")
    sql = SQLOperator()
    res = sql.exec(sql_query, sql_values_list, is_fetchall=True, is_many=True)
    logger.success(res)

    # python -m transforms.video_row
