import pymysql
import streamlit as st
from config import DB_CONFIG


def clean_select_sql(sql):
    """Normalize a user-entered SELECT for EXPLAIN."""
    sql = (sql or "").strip().rstrip(";").strip()
    lowered = sql.lower()
    if lowered.startswith("explain"):
        parts = sql.split(None, 1)
        sql = parts[1] if len(parts) > 1 else ""
        lowered = sql.lower()
        if lowered.startswith("format="):
            parts = sql.split(None, 1)
            sql = parts[1] if len(parts) > 1 else ""
    return sql.strip()


def get_connection():
    """获取数据库连接，使用 config.py 中的配置"""
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
        )
        return conn
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        return None


def test_connection():
    """测试数据库连接"""
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            connect_timeout=5,
        )
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


def execute_query(sql, params=None):
    """执行查询并返回结果"""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
    except Exception as e:
        st.error(f"查询执行失败: {e}")
        return None
    finally:
        conn.close()


def execute_explain(sql, params=None):
    """执行EXPLAIN分析，支持参数化查询"""
    sql = clean_select_sql(sql)
    if not sql:
        st.error("请输入 SELECT 查询语句")
        return None

    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(f"EXPLAIN FORMAT=TRADITIONAL {sql}", params)
            except Exception:
                cursor.execute(f"EXPLAIN {sql}", params)
            return cursor.fetchall()
    except Exception as e:
        st.error(f"EXPLAIN执行失败: {e}")
        return None
    finally:
        conn.close()


def execute_ddl(sql):
    """执行DDL/DML语句（CREATE/DROP/INSERT等）"""
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
            return True
    except Exception as e:
        st.error(f"DDL执行失败: {e}")
        return False
    finally:
        conn.close()


def execute_script(sql_script):
    """按分号顺序执行简单脚本。"""
    statements = [s.strip() for s in sql_script.split(";") if s.strip()]
    if not statements:
        return True
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            for stmt in statements:
                cursor.execute(stmt)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"脚本执行失败: {e}")
        return False
    finally:
        conn.close()


def table_exists(table_name):
    sql = """
        SELECT COUNT(*) AS cnt
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
    """
    result = execute_query(sql, (table_name,))
    return bool(result and result[0].get("cnt", 0) > 0)


def index_exists(table_name, index_name):
    sql = """
        SELECT COUNT(*) AS cnt
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND INDEX_NAME = %s
    """
    result = execute_query(sql, (table_name, index_name))
    return bool(result and result[0].get("cnt", 0) > 0)


def create_index_if_missing(table_name, index_name, columns):
    if index_exists(table_name, index_name):
        return True, "exists"
    ok = execute_ddl(f"CREATE INDEX {index_name} ON {table_name}({columns})")
    return ok, "created" if ok else "failed"


def drop_index_if_exists(table_name, index_name):
    if not index_exists(table_name, index_name):
        return True, "missing"
    ok = execute_ddl(f"DROP INDEX {index_name} ON {table_name}")
    return ok, "dropped" if ok else "failed"


def get_table_info(table_name):
    """获取表结构信息"""
    sql = f"""
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_KEY,
            COLUMN_DEFAULT,
            EXTRA
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """
    return execute_query(sql)


def get_indexes(table_name):
    """获取表的索引信息"""
    sql = f"""
        SELECT
            INDEX_NAME,
            COLUMN_NAME,
            NON_UNIQUE,
            SEQ_IN_INDEX,
            CARDINALITY
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
    """
    return execute_query(sql)


def get_table_stats():
    """获取所有表的统计信息"""
    sql = """
        SELECT
            TABLE_NAME,
            TABLE_ROWS,
            ROUND(DATA_LENGTH / 1024 / 1024, 2) AS DATA_SIZE_MB,
            ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS INDEX_SIZE_MB,
            ENGINE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY DATA_LENGTH DESC
    """
    return execute_query(sql)
