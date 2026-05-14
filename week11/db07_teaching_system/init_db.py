"""
DB07 教学系统 — 数据库初始化脚本

用法：
    python3 init_db.py              # 全新初始化（会删旧表）
    python3 init_db.py --keep-data  # 保留旧表数据，只增量插入新题

依赖：pip3 install pymysql
"""

import argparse
import sys

try:
    import pymysql
except ImportError:
    print("❌ 请先安装 PyMySQL：python3 -m pip install pymysql")
    sys.exit(1)

# 不依赖 config.py 里的数据库名，先连接到服务器再创建
from config import DB_CONFIG

DB_NAME = DB_CONFIG["database"]
HOST = DB_CONFIG["host"]
USER = DB_CONFIG["user"]
PASSWORD = DB_CONFIG["password"]

# 五个主题
TOPICS_SQL = """
INSERT INTO db07_topics (topic_key, title, source_section, sort_order) VALUES
('problem', '为什么要规范化', '课件 7.1', 1),
('fd', '函数依赖与推理', '课件 7.2.1-7.2.4', 2),
('closure', '闭包、候选键与最小依赖集', '课件 7.2.5-7.2.7', 3),
('decomposition', '模式分解：无损与保持依赖', '课件 7.3', 4),
('normal_forms', '范式：1NF 到 5NF', '课件 7.4-7.6', 5)
ON DUPLICATE KEY UPDATE title=VALUES(title), source_section=VALUES(source_section);
"""

# 从 seed_data 导入习题数据
from models.seed_data import EXERCISES


def get_server_connection():
    """连接到 MySQL 服务器（不指定数据库）"""
    return pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def get_db_connection():
    """连接到目标数据库"""
    return pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def create_database():
    """创建数据库（如不存在）"""
    print(f"📦 检查数据库 {DB_NAME} ...")
    conn = get_server_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print(f"   ✅ 数据库 {DB_NAME} 已就绪")
    finally:
        conn.close()


def create_tables(drop_existing=False):
    """创建表结构"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if drop_existing:
                print("🗑️  删除旧表...")
                cur.execute("DROP TABLE IF EXISTS db07_student_attempts")
                cur.execute("DROP TABLE IF EXISTS db07_exercises")
                cur.execute("DROP TABLE IF EXISTS db07_topics")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS db07_topics (
                    topic_key VARCHAR(40) PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    source_section VARCHAR(60) NOT NULL,
                    sort_order INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS db07_exercises (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    topic_key VARCHAR(40) NOT NULL,
                    question_type ENUM('single', 'judge') NOT NULL DEFAULT 'single',
                    question TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    answer VARCHAR(100) NOT NULL,
                    explanation TEXT NOT NULL,
                    difficulty ENUM('基础', '提高', '综合') NOT NULL DEFAULT '基础',
                    sort_order INT NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_db07_exercises_topic
                        FOREIGN KEY (topic_key) REFERENCES db07_topics(topic_key)
                        ON UPDATE CASCADE ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS db07_student_attempts (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    exercise_id INT NOT NULL,
                    student_name VARCHAR(80) NOT NULL DEFAULT '匿名学生',
                    submitted_answer VARCHAR(255) NOT NULL,
                    is_correct TINYINT(1) NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_db07_attempts_exercise
                        FOREIGN KEY (exercise_id) REFERENCES db07_exercises(id)
                        ON UPDATE CASCADE ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

        conn.commit()
        print("   ✅ 表结构已就绪")
    finally:
        conn.close()


def insert_data(replace_exercises=False):
    """插入主题和习题数据"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 插入主题
            print("📝 写入主题...")
            for stmt in TOPICS_SQL.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    cur.execute(stmt)

            # 习题处理
            if replace_exercises:
                print("🗑️  清空旧习题...")
                cur.execute("DELETE FROM db07_exercises")

            # 检查现有题目数
            cur.execute("SELECT COUNT(*) AS cnt FROM db07_exercises")
            existing = cur.fetchone()["cnt"]

            if existing >= len(EXERCISES):
                print(f"   ℹ️  已有 {existing} 题 >= {len(EXERCISES)} 题，无需插入")
            else:
                # 获取已有 ID
                cur.execute("SELECT id FROM db07_exercises")
                existing_ids = {row["id"] for row in cur.fetchall()}

                new_count = 0
                for ex in EXERCISES:
                    if ex["id"] in existing_ids:
                        continue
                    import json
                    cur.execute(
                        """
                        INSERT INTO db07_exercises
                            (id, topic_key, question_type, question, options_json,
                             answer, explanation, difficulty, sort_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            ex["id"],
                            ex["topic_key"],
                            ex.get("question_type", "single"),
                            ex["question"],
                            json.dumps(ex.get("options", []), ensure_ascii=False),
                            str(ex.get("answer", "0")),
                            ex.get("explanation", ""),
                            ex.get("difficulty", "基础"),
                            ex.get("sort_order", 1),
                        ),
                    )
                    new_count += 1

                print(f"   ✅ 新增 {new_count} 题，题库共 {existing + new_count} 题")

        conn.commit()
    finally:
        conn.close()


def show_summary():
    """显示数据库概况"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT topic_key, COUNT(*) AS cnt FROM db07_exercises GROUP BY topic_key ORDER BY topic_key")
            rows = cur.fetchall()
            total = sum(r["cnt"] for r in rows)
            print(f"\n📊 数据库 {DB_NAME} 概况：")
            print(f"   练习题总数：{total}")
            for r in rows:
                print(f"     {r['topic_key']}: {r['cnt']} 题")

            cur.execute("SELECT COUNT(*) AS cnt FROM db07_student_attempts")
            attempts = cur.fetchone()["cnt"]
            print(f"   学生作答记录：{attempts} 条")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="DB07 教学系统数据库初始化")
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="保留旧数据，只增量插入新题目（不删表）",
    )
    args = parser.parse_args()

    drop = not args.keep_data

    print("=" * 52)
    print("  DB07 教学系统 — 数据库初始化")
    print(f"  服务器：{HOST}")
    print(f"  数据库：{DB_NAME}")
    print(f"  模式：{'保留数据增量更新' if args.keep_data else '全新初始化'}")
    print("=" * 52)

    try:
        create_database()
        create_tables(drop_existing=drop)
        insert_data(replace_exercises=drop)
        show_summary()
        print("\n🎉 初始化完成！运行 python3 app.py 启动教学系统。")
    except pymysql.err.OperationalError as e:
        print(f"\n❌ 数据库连接失败：{e}")
        print(f"   请检查 config.py 中的连接配置：")
        print(f"   HOST={HOST}, USER={USER}, DB={DB_NAME}")
        sys.exit(1)


if __name__ == "__main__":
    main()
