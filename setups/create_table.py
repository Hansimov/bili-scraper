from tclogger import logger
from transforms.video_row import VideoInfoConverter
from transforms.dtypes import DataTyper
from networks.sql import SQLOperator


def create_video_info_table(table_name: str = "videos"):
    """This script would only run once, to create sql table with required columns."""

    py_columns = VideoInfoConverter.COLUMNS
    columns_sql_map = VideoInfoConverter.COLUMNS_SQL_MAP
    columns_rename_map = VideoInfoConverter.COLUMNS_RENAME_MAP
    columns_to_ignore = VideoInfoConverter.COLUMNS_TO_IGNORE

    typer = DataTyper()
    sql_columns = {k: typer.py_dtype_to_sql_dtype(v) for k, v in py_columns.items()}
    sql_columns = {k: columns_sql_map.get(k, v) for k, v in sql_columns.items()}
    sql_columns = {columns_rename_map.get(k, k): v for k, v in sql_columns.items()}
    sql_columns = {k: v for k, v in sql_columns.items() if k not in columns_to_ignore}

    ws = " " * 4
    table_str = f",\n{ws}".join([f"{k} {v}" for k, v in sql_columns.items()])

    cmd_create_table = f"""CREATE TABLE {table_name} (
    {table_str}
    );"""

    logger.note(f"Creating table: {table_name} with {len(sql_columns)} columns:")
    logger.mesg(f"{cmd_create_table}")

    sql = SQLOperator()
    res = sql.exec(cmd_create_table)
    logger.mesg(res)


if __name__ == "__main__":
    create_video_info_table()
    # python -m setups.create_table
