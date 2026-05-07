"""数据库初始化脚本

功能：
1. 创建 DB06 数据库（如不存在）
2. 运行 dbsc.sql 创建表结构和初始数据
3. 创建自定义函数 fn_GetTotalCreditBySID
4. 创建存储过程 sp_CourseStat
5. 创建触发器 trg_grade_check

使用方式：
    python init_db.py

参考：week09/stu_app_v1_04/init_data.py 的初始化模式
"""

import os
import sys
import subprocess
from config import DB_CONFIG


def get_sql_file_path():
    """获取 dbsc.sql 文件的绝对路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # dbsc.sql 在上级目录的 DB06 文件夹中
    sql_path = os.path.join(
        script_dir, '..', 'DB06数据库应用系统260504', 'dbsc.sql')
    return os.path.abspath(sql_path)


def create_database():
    """使用 mysql CLI 创建数据库"""
    print("正在创建数据库 DB06...")
    cmd = [
        'mysql',
        '-h', DB_CONFIG['host'],
        '-u', DB_CONFIG['user'],
        f"-p{DB_CONFIG['password']}",
        '-e', 'CREATE DATABASE IF NOT EXISTS DB06 CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"创建数据库失败: {result.stderr}")
        return False
    print("数据库 DB06 创建成功")
    return True


def run_sql_file(sql_path):
    """使用 mysql CLI 运行 SQL 文件"""
    print(f"正在执行 SQL 文件: {sql_path}")
    cmd = [
        'mysql',
        '-h', DB_CONFIG['host'],
        '-u', DB_CONFIG['user'],
        f"-p{DB_CONFIG['password']}",
        DB_CONFIG['database']
    ]
    with open(sql_path, 'r', encoding='utf-8') as f:
        result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"执行 SQL 文件失败: {result.stderr}")
        return False
    print("SQL 文件执行完成")
    return True


def create_db_objects():
    """通过 Python 连接创建函数和存储过程"""
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

    # 步骤1: 创建数据库
    if not create_database():
        sys.exit(1)

    # 步骤2: 执行 dbsc.sql（建表 + 插入数据）
    if not run_sql_file(sql_path):
        sys.exit(1)

    # 步骤3: 创建函数和存储过程
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
