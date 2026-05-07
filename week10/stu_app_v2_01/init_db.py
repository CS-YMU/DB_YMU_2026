"""数据库初始化脚本

功能：
1. 创建 DB06 数据库（如不存在）
2. 运行 dbsc.sql 创建表结构和初始数据
3. 创建自定义函数 fn_GetTotalCreditBySID
4. 创建存储过程 sp_CourseStat
5. 创建触发器 trg_grade_check

使用方式：
    python init_db.py

说明：
    全程使用 mysql-connector-python 完成，不依赖 mysql 命令行工具，
    学生只需 `pip install -r requirements.txt` 即可，无需在系统 PATH
    中配置 mysql.exe。
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_sql_file_path():
    """获取 dbsc.sql 文件的绝对路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'dbsc.sql')


def create_database():
    """创建 DB06 数据库（不指定数据库连接）"""
    print("正在创建数据库 DB06...")
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset='utf8mb4',
        )
        cursor = conn.cursor()
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS DB06 "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("数据库 DB06 创建成功")
        return True
    except Error as e:
        print(f"创建数据库失败: {e}")
        return False


def split_sql_statements(sql_content):
    """将 SQL 文件内容切分为单条语句

    按分号分割，跳过空行和单行注释。dbsc.sql 中没有 BEGIN...END 块，
    所以分号即语句分隔符。
    """
    cleaned_lines = []
    in_block_comment = False
    for line in sql_content.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if in_block_comment:
            if stripped.endswith('*/'):
                in_block_comment = False
            continue
        if stripped.startswith('/*'):
            if not stripped.endswith('*/'):
                in_block_comment = True
            continue
        if stripped.startswith('--'):
            continue
        cleaned_lines.append(line)

    cleaned_sql = '\n'.join(cleaned_lines)
    return [s.strip() for s in cleaned_sql.split(';') if s.strip()]


def run_sql_file(sql_path):
    """通过 mysql-connector-python 执行 SQL 文件"""
    print(f"正在执行 SQL 文件: {sql_path}")

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    statements = split_sql_statements(sql_content)

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4',
        )
        cursor = conn.cursor()

        for stmt in statements:
            try:
                cursor.execute(stmt)
            except Error as e:
                print(f"  语句执行警告: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("SQL 文件执行完成")
        return True
    except Error as e:
        print(f"执行 SQL 文件失败: {e}")
        return False


def create_db_objects():
    """通过 Database 类创建函数、存储过程和触发器"""
    from database import Database
    db = Database(**DB_CONFIG)
    if not db.connect():
        return False
    db.init_db_objects()
    db.close()
    return True


def main():
    print("=" * 60)
    print("DB06 数据库应用系统 —— 数据库初始化")
    print("=" * 60)

    sql_path = get_sql_file_path()
    print(f"SQL 文件路径: {sql_path}")

    if not os.path.exists(sql_path):
        print(f"错误: SQL 文件不存在 - {sql_path}")
        sys.exit(1)

    if not create_database():
        sys.exit(1)

    if not run_sql_file(sql_path):
        sys.exit(1)

    if not create_db_objects():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("初始化完成！")
    print("数据库: DB06")
    print("表: student, course, student_course, student_course_retake")
    print("函数: fn_GetTotalCreditBySID")
    print("存储过程: sp_CourseStat")
    print("触发器: trg_grade_check")
    print("=" * 60)
    print("\n启动 Web 应用: flask run --debug")


if __name__ == '__main__':
    main()
