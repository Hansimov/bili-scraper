from tclogger import logger
from transforms.user_video_row import UserVideoInfoConverter
from transforms.dtypes import DataTyper
from networks.sql import SQLOperator


def create_user_video_info_table(
    table_name: str = "user_videos", primary_key: str = "bvid"
):
    """This script would only run once, to create sql table with required columns."""

    py_columns = UserVideoInfoConverter.COLUMNS
    columns_sql_map = UserVideoInfoConverter.COLUMNS_SQL_MAP
    columns_rename_map = UserVideoInfoConverter.COLUMNS_RENAME_MAP
    columns_to_ignore = UserVideoInfoConverter.COLUMNS_TO_IGNORE

    typer = DataTyper()
    sql_columns = {k: typer.py_dtype_to_sql_dtype(v) for k, v in py_columns.items()}
    sql_columns = {k: columns_sql_map.get(k, v) for k, v in sql_columns.items()}
    sql_columns = {columns_rename_map.get(k, k): v for k, v in sql_columns.items()}
    sql_columns = {k: v for k, v in sql_columns.items() if k not in columns_to_ignore}

    ws = " " * 4

    column_str_list = []
    for k, v in sql_columns.items():
        column_str = f"{k} {v}"
        if k == primary_key:
            column_str += " PRIMARY KEY"
        column_str_list.append(column_str)
    table_str = f",\n{ws}".join(column_str_list)

    cmd_create_table = f"""CREATE TABLE {table_name} (
    {table_str}
    );"""

    logger.note(f"Creating table: {table_name} with {len(sql_columns)} columns:")
    logger.mesg(f"{cmd_create_table}")

    sql = SQLOperator()
    res = sql.exec(cmd_create_table)
    logger.mesg(res)


if __name__ == "__main__":
    create_user_video_info_table()
    # python -m setups.create_user_videos_table
