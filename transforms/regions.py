from pprint import pformat
from tclogger import logger

from networks.constants import REGION_CODES, REGION_GROUPS, REGION_INFOS


def get_all_region_tids(
    include_redirect: bool = False, include_offline=False
) -> list[int]:
    region_tids = []
    for k, v in REGION_INFOS.items():
        region_status = v.get("region_status", "")
        if not include_redirect and region_status == "redirect":
            continue
        if not include_offline and region_status == "offline":
            continue
        region_tid = v["region_tid"]
        region_tids.append(region_tid)
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


def get_region_tids_from_parent_codes(
    parent_codes: list[str] = [],
    include_redirect: bool = False,
    include_offline: bool = False,
) -> list[int]:
    region_tids = []
    for parent_code in parent_codes:
        parent_dict = REGION_CODES.get(parent_code, {})
        region_dict = parent_dict.get("children", {})
        for k, v in region_dict.items():
            tid = v["tid"]
            status = v.get("status", "")
            if not include_redirect and status == "redirect":
                continue
            if not include_offline and status == "offline":
                continue
            region_tids.append(tid)
    return region_tids


def get_region_tids_from_groups(
    region_groups: list[str] = [],
    include_redirect: bool = False,
    include_offline: bool = False,
) -> list[int]:
    region_tids = []
    region_codes = []
    for region_group in region_groups:
        region_codes.extend(REGION_GROUPS.get(region_group, []))

    region_tids = get_region_tids_from_parent_codes(
        region_codes, include_redirect=include_redirect, include_offline=include_offline
    )
    return region_tids


if __name__ == "__main__":
    all_tids = get_all_region_tids()
    logger.note(f"get_all_region_tids():")
    logger.mesg(f"- {len(all_tids)} tids")
    logger.success(all_tids)

    tid = 201
    region_info = get_region_info_by_tid(tid)
    logger.note(f"get_region_info_by_tid({tid}):")
    logger.success(pformat(region_info, sort_dicts=False))

    parent_codes = ["knowledge"]
    region_tids = get_region_tids_from_parent_codes(parent_codes)
    logger.note(f"get_region_tids_from_parent_codes({parent_codes}):")
    logger.success(region_tids)

    groups = ["learns"]
    region_tids = get_region_tids_from_groups(groups)
    logger.note(f"get_region_tids_from_groups({groups}):")
    logger.success(region_tids)

    # python -m transforms.regions
