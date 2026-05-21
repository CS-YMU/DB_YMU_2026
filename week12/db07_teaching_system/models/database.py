from contextlib import contextmanager

from config import DB_CONFIG


class DatabaseUnavailable(RuntimeError):
    pass


def _load_driver():
    try:
        import pymysql
    except ImportError as exc:
        raise DatabaseUnavailable("未安装 PyMySQL，请执行：python3 -m pip install pymysql") from exc
    return pymysql


@contextmanager
def get_connection():
    pymysql = _load_driver()
    try:
        conn = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **DB_CONFIG)
    except Exception as exc:
        raise DatabaseUnavailable(f"数据库连接失败：{exc}") from exc
    try:
        yield conn
    finally:
        conn.close()


def check_database():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS db_name")
            row = cursor.fetchone()
    return row["db_name"]

