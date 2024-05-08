import psycopg2

from tclogger import logger

from configs.envs import SQL_ENVS


class SQLOperator:
    def __init__(self):
        self.host = SQL_ENVS["host"]
        self.port = SQL_ENVS["port"]
        self.dbname = SQL_ENVS["dbname"]
        self.user = SQL_ENVS["user"]
        self.password = SQL_ENVS["password"]
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

    def exec(self, query: str, values=None):
        self.cur.execute(query, values)
        try:
            res = self.cur.fetchall()
        except Exception as e:
            res = None
            logger.warn(e)
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
