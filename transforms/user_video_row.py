import json
import requests

from datetime import datetime
from tclogger import logger

from networks.constants import REQUESTS_HEADERS, GET_VIDEO_PAGE_API


class UserVideoInfoConverter:
    """
    查询用户投稿视频明细：
    - https://socialsisteryi.github.io/bilibili-API-collect/docs/user/space.html#%E6%9F%A5%E8%AF%A2%E7%94%A8%E6%88%B7%E6%8A%95%E7%A8%BF%E8%A7%86%E9%A2%91%E6%98%8E%E7%BB%86

    API：
    - https://api.bilibili.com/x/space/wbi/arc/search
    - params: `mid`, `pn`, `ps`, `wts`, `w_rid`
    """

    META_COLUMNS = {
        "aid": int,  # video id
        "bvid": str,  # video BV id
        "title": str,  # video title
        "description": str,  # video description (same with `desc`)
        "pic": str,  # cover image url
        "created": int,  # post datetime (timestamp) (same with `ctime`)
        "length": str,  # video duration (in format "mm:ss")
        "typeid": int,  # reigon code (same with `tid`)
        "copyright": str,  # 1: original; 2: reposted. [Need to covert to int]
        "is_charging_arc": bool,  # video only accessible for charging users
        "attribute": int,  # video attribute bits, see: https://socialsisteryi.github.io/bilibili-API-collect/docs/video/attribute_data.html
    }
    OWNER_COLUMNS = {
        "mid": int,  # owner id
        "author": str,  # owner name (same with `name`)
        "is_union_video": int,  # 0: not union video; 1: union video
    }
    STATS_COLUMNS = {
        "play": int,  # plays count (same with `view`)
        "video_review": int,  # danmakus count (same with `danmaku`)
        "comment": int,  # comments count (same with `reply`)
    }
    SEASON_COLUMNS = {
        "meta": dict,  # info of episode collection (or called `season`), None or dict (if belongs to a season)
        "season_id": int,  # season id, 0 means not belongs to any season
    }

    UNKNOWN_COLUMNS = {
        "subtitle": str,  # Unknown, always ""
        "review": int,  # Unknown, always 0
        "hide_click": bool,  # Unknown, always False
        "is_pay": int,  # Unknown, always 0
        "is_steins_gate": int,  # Unknown, always 0
        "is_live_playback": int,  # Unknown, always 0
        "is_lesson_video": int,  # Unknown, always 0
        "is_lesson_finished": int,  # Unknown, always 0
        "lesson_update_info": str,  # Unknown, always ""
        "jump_url": str,  # Unknown, always ""
        "is_avoided": int,  # Unknown, always 0
        "vt": int,  # Unknown, always 0
        "enable_vt": int,  # Unknown, always 0
        "vt_display": str,  # Unknown, alwasy ""
        "playback_position": int,  # Unknown, always 0
    }

    EXTRA_COLUMNS = {
        "insert_at": int,
    }
    COLUMNS_SQL_MAP = {
        "ctime": "timestamptz",
        "insert_at": "timestamptz",
    }
    COLUMNS_RENAME_MAP = {
        "author": "name",
        "play": "view",
        "video_review": "danmaku",
        "comment": "reply",
        "typeid": "tid",
        "created": "ctime",
    }

    COLUMNS_TO_IGNORE = [
        "meta",
        *UNKNOWN_COLUMNS.keys(),
    ]

    COLUMNS = {
        **META_COLUMNS,
        **OWNER_COLUMNS,
        **STATS_COLUMNS,
        **SEASON_COLUMNS,
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
        for method in [self.rename, self.extra, self.sort, self.ignore]:
            new_video_info = method(new_video_info)
        return new_video_info

    def serialize_sql_row(self, sql_row: dict):
        """serialize sql row dict to tuples"""
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

            if isinstance(v, str):
                new_v = new_v.replace("\x00", "")

            new_sql_values.append(new_v)
        new_sql_values = tuple(new_sql_values)
        return new_sql_values

    def to_sql_query_and_values(
        self,
        video_info: dict,
        table_name: str = "user_videos",
        is_many: bool = False,
        update_on_conflict: bool = True,
        primary_key: str = "bvid",
    ):
        """convert video info dict to sql query and values"""
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
    pass

    # python -m transforms.user_video_row
