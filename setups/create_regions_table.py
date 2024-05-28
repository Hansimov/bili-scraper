"""This script would only run once, to create sql table with required columns."""

from tclogger import logger
from transforms.dtypes import DataTyper
from networks.sql import SQLOperator
from networks.constants import REGION_CODES, REGION_GROUPS
from pprint import pformat


def get_region_group(main_region_key: str):
    for k, v in REGION_GROUPS.items():
        if main_region_key in v:
            return k
    return ""


SQL_COLUMNS = {
    "r_tid": "int8 PRIMARY KEY",
    "r_key": "text",
    "r_name": "text",
    "main_r_tid": "int8",
    "main_r_key": "text",
    "main_r_name": "text",
    "r_group": "text",
}


def create_regions_info_table_columns(table_name: str = "regions"):
    ws = " " * 4
    table_str = f",\n{ws}".join([f"{k} {v}" for k, v in SQL_COLUMNS.items()])

    cmd_create_table = f"""CREATE TABLE {table_name} (
    {table_str}
    );"""
    logger.note(f"Creating table: {table_name} with {len(SQL_COLUMNS)} columns:")
    logger.mesg(f"{cmd_create_table}")

    sql = SQLOperator()
    res = sql.exec(cmd_create_table)
    logger.mesg(res)


def create_regions_info_dict():
    regions_info_dict = []
    logger.note("Creating regions_info_dict:")

    for k, v in REGION_CODES.items():
        main_region_key = k
        main_region_name = v["name"]
        main_region_tid = v["tid"]
        region_group = get_region_group(main_region_key)
        regions = v["children"]
        for sk, sv in regions.items():
            region_key = sk
            region_name = sv["name"]
            region_tid = sv["tid"]
            region_status = sv.get("status", "")
            if region_status == "redirect":
                continue
            region_info = {
                "r_tid": region_tid,
                "r_key": region_key,
                "r_name": region_name,
                "main_r_tid": main_region_tid,
                "main_r_key": main_region_key,
                "main_r_name": main_region_name,
                "r_group": region_group,
            }
            regions_info_dict.append(region_info)
    # logger.success(pformat(regions_info_dict, sort_dicts=False))
    return regions_info_dict


def insert_regions_info_table_rows(
    table_name: str = "regions", primary_key: str = "r_tid"
):
    sql = SQLOperator()
    regions_info_dict = create_regions_info_dict()
    columns_str = ", ".join(SQL_COLUMNS.keys())

    update_on_conflict_str = f" ON CONFLICT ({primary_key}) DO UPDATE SET "
    update_set_columns = [k for k in SQL_COLUMNS.keys() if k != primary_key]
    update_set_columns_str = ", ".join(
        [f"{k} = EXCLUDED.{k}" for k in update_set_columns]
    )
    update_set_str = f"{update_on_conflict_str}{update_set_columns_str}"

    sql_query = f"INSERT INTO {table_name} ({columns_str}) VALUES %s {update_set_str}"
    # sql_query = f"INSERT INTO {table_name} ({columns_str}) VALUES %s"
    # logger.mesg(sql_query)

    sql_values = [tuple(row.values()) for row in regions_info_dict]
    # logger.file(sql_values)

    logger.note(f"Inserting {len(sql_values)} rows into table: {table_name}")
    res = sql.exec(sql_query, sql_values, is_many=True)
    logger.mesg(res)


if __name__ == "__main__":
    # create_regions_info_table_columns()
    insert_regions_info_table_rows()

    # python -m setups.create_regions_table
