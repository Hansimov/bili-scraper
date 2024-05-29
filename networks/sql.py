import psycopg2
import psycopg2.extras
import threading

from datetime import datetime
from pathlib import Path
from pprint import pformat
from tclogger import logger
from typing import Union, Tuple, List

from configs.envs import SQL_ENVS


class SQLOperator:
    def __init__(self):
        self.host = SQL_ENVS["host"]
        self.port = SQL_ENVS["port"]
        self.dbname = SQL_ENVS["dbname"]
        self.user = SQL_ENVS["user"]
        self.password = SQL_ENVS["password"]
        self.log_file = Path(__file__).parents[1] / "logs" / SQL_ENVS["log_file"]
        self.lock = threading.Lock()
        self.connect()

    def connect(self):
        logger.note(f"> Connecting to: {self.host}:{self.port} ...")
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )
        self.cur = self.conn.cursor()
        logger.success(f"+ Connected to [{self.dbname}] as ({self.user})")

    def log_error(
        self, query: str, values: Union[Tuple, List[Tuple]] = None, e: Exception = None
    ):
        error_info = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "values": values,
            "error": repr(e),
        }
        logger.err(f"× SQL Error:")
        logger.warn(f"{error_info}")
        error_str = pformat(error_info, sort_dicts=False)
        with open(self.log_file, "a") as f:
            f.write(f"{error_str}\n\n")

    def exec(
        self,
        query: str,
        values: Union[Tuple, List[Tuple]] = None,
        is_fetchall: bool = False,
        is_many: bool = False,
    ):
        with self.lock:
            try:
                if not is_many:
                    self.cur.execute(query, values)
                else:
                    # https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values
                    psycopg2.extras.execute_values(
                        cur=self.cur, sql=query, argslist=values
                    )
            except Exception as e:
                self.log_error(query, values, e)

            if is_fetchall:
                try:
                    res = self.cur.fetchall()
                except Exception as e:
                    res = None
                    if "no results to fetch" not in str(e):
                        logger.warn(e)
            else:
                res = None

            self.conn.commit()
        return res

    def close(self):
        self.cur.close()
        self.conn.close()
        return True

    def test_connection(self):
        try:
            # get current connected database name
            command = "SELECT current_database();"
            res = self.exec(command)
            logger.success(f"{res}")
            return True
        except Exception as e:
            logger.warn(f"{e}")
            return False

    def __del__(self):
        self.close()
        logger.success(f"- Disconnected: {self.host}:{self.port}")


if __name__ == "__main__":
    sql = SQLOperator()
    sql.test_connection()

    # python -m networks.sql
