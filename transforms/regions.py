from pprint import pformat
from tclogger import logger

from networks.constants import REGION_CODES, REGION_GROUPS, REGION_INFOS


def get_region_tids_from_codes(region_codes: list[str] = []) -> list[int]:
    region_tids = []
    for region_code in region_codes:
        region_dict = REGION_CODES.get(region_code, {})
        sub_region_dict = region_dict.get("children", {})
        for k, v in sub_region_dict.items():
            tmp_tid = v.get("tid", -1)
            if tmp_tid > 0:
                region_tids.append(tmp_tid)
    return region_tids


def get_region_tids_from_groups(region_groups: list[str] = []) -> list[int]:
    region_tids = []
    region_codes = []
    for region_group in region_groups:
        region_codes.extend(REGION_GROUPS.get(region_group, []))

    region_tids = get_region_tids_from_codes(region_codes)
    return region_tids


def get_region_info_by_tid(tid: int = -1) -> dict:
    region_info = {
        "region_tid": tid,  # 201
        "region_code": "",  # "science"
        "region_name": "",  # "科学科普"
        "parent_tid": 0,  # 36
        "parent_code": "",  # "knowledge"
        "parent_name": "",  # "知识"
        "group_code": "",  # "learns"
    }

    region_info = REGION_INFOS.get(tid, region_info)

    return region_info


if __name__ == "__main__":
    tid = 201
    region_info = get_region_info_by_tid(tid)
    logger.success(pformat(region_info, sort_dicts=False))

    # python -m transforms.regions
