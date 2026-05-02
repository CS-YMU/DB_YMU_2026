"""初始化测试数据 —— 使用 DB05 的 SQL 脚本。

教学定位：
本脚本用于把数据库恢复到“完整业务需求状态”。它先执行
`DB05课外练习案例/dbsample.sql` 和 `生成测试数据.sql`，再补充
原始业务描述中出现、但 DB05 示例 SQL 未实现的 2 张关系表。

为什么先 DROP DATABASE？
课堂演示时可能运行过视图、触发器、存储过程，或者学生误建了额外表。
为了避免历史实验对象干扰，本脚本每次都会删除并重建 dbsample。
"""
import subprocess
from pathlib import Path

DB_CONFIG = {
    'host': 'localhost',
    'database': 'dbsample',
    'user': 'dylan',
    'password': 'P@ssw0rd'
}

# 这些路径是相对当前文件推导出来的：
# homework/
# ├── DB05课外练习案例/
# └── stu_app_v1_04/init_data.py
BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR.parent / 'DB05课外练习案例'
SCHEMA_SQL = SQL_DIR / 'dbsample.sql'
DATA_SQL = SQL_DIR / '生成测试数据.sql'

# DB05 示例 SQL 的 16 张基础表 + 原始业务描述补充的 2 张关系表。
EXPECTED_TABLES = [
    'course',
    'course_leader',
    'course_prerequisite',
    'dd_administrative_divisions',
    'dd_professional_title',
    'dd_sex',
    'major',
    'major_leader',
    'student',
    'student_course',
    'student_major1',
    'student_major2',
    'student_phone',
    'teacher',
    'teacher_course',
    'teacher_major',
    'major_course',
    'teacher_guidance',
]

SUPPLEMENT_SCHEMA_SQL = """
CREATE TABLE `major_course` (
  `MajorAID` smallint NOT NULL COMMENT '专业AID',
  `CourseAID` int NOT NULL COMMENT '课程AID',
  PRIMARY KEY (`MajorAID`, `CourseAID`) USING BTREE,
  INDEX `Major_Course_FK_2`(`CourseAID` ASC) USING BTREE,
  CONSTRAINT `Major_Course_FK_1` FOREIGN KEY (`MajorAID`) REFERENCES `major` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Major_Course_FK_2` FOREIGN KEY (`CourseAID`) REFERENCES `course` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '专业开设课程' ROW_FORMAT = Dynamic;

CREATE TABLE `teacher_guidance` (
  `StudentAID` int NOT NULL COMMENT '学生AID',
  `TeacherAID` int NOT NULL COMMENT '指导教师AID',
  `StartDate` date NOT NULL COMMENT '指导开始日期',
  `EndDate` date NULL DEFAULT NULL COMMENT '指导结束日期',
  PRIMARY KEY (`StudentAID`) USING BTREE,
  INDEX `Teacher_Guidance_FK_2`(`TeacherAID` ASC) USING BTREE,
  CONSTRAINT `Teacher_Guidance_FK_1` FOREIGN KEY (`StudentAID`) REFERENCES `student` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Teacher_Guidance_FK_2` FOREIGN KEY (`TeacherAID`) REFERENCES `teacher` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '教师指导学生' ROW_FORMAT = Dynamic;
"""

SUPPLEMENT_DATA_SQL = """
INSERT IGNORE INTO major_course (MajorAID, CourseAID)
SELECT DISTINCT tm.MajorAID, tc.CourseAID
FROM teacher_course tc
JOIN teacher_major tm ON tc.TeacherAID = tm.TeacherAID;

INSERT IGNORE INTO major_course (MajorAID, CourseAID)
SELECT m.AID, c.AID
FROM major m
JOIN course c ON c.AID IN (1, 2, 6, 7, 8);

INSERT INTO teacher_guidance (StudentAID, TeacherAID, StartDate, EndDate)
SELECT s.AID,
       COALESCE((
           SELECT tm.TeacherAID
           FROM student_major1 sm
           JOIN teacher_major tm ON sm.MajorAID = tm.MajorAID
           WHERE sm.StudentAID = s.AID
           ORDER BY RAND()
           LIMIT 1
       ), (SELECT AID FROM teacher ORDER BY AID LIMIT 1)) AS TeacherAID,
       MAKEDATE(s.YearInroll, 1) AS StartDate,
       NULL AS EndDate
FROM student s;
"""


def run_mysql(sql=None, database=None):
    """执行 mysql CLI 命令，统一传入连接参数和字符集。

    这里使用 mysql 命令行而不是 mysql.connector，是为了让“建库导入 SQL”
    不依赖 Python 包是否安装，学生只要有 MySQL 客户端即可初始化。
    """
    cmd = [
        'mysql',
        '-h', DB_CONFIG['host'],
        '-u', DB_CONFIG['user'],
        f"-p{DB_CONFIG['password']}",
        '--default-character-set=gb18030',
    ]
    if database:
        cmd.append(database)

    return subprocess.run(
        cmd,
        input=sql,
        capture_output=True,
        check=False,
        timeout=60
    )


def print_mysql_error(prefix, result):
    """统一打印 mysql 命令失败信息。"""
    stderr = result.stderr.decode('utf-8', errors='replace').strip()
    stdout = result.stdout.decode('utf-8', errors='replace').strip()
    detail = stderr or stdout or f"mysql 退出码 {result.returncode}"
    print(f"❌ {prefix}：{detail}")


def close_database_sessions():
    """关闭正在使用目标数据库的其它连接，避免 DROP DATABASE 等待元数据锁。

    Navicat、命令行客户端或正在运行的主程序如果保持在 dbsample 上，
    MySQL 会让 DROP DATABASE 一直等待 metadata lock。教学环境中重置
    数据库前主动 KILL 这些会话，可以避免“卡在第一步没反应”。
    """
    process_sql = (
        "SELECT ID "
        "FROM INFORMATION_SCHEMA.PROCESSLIST "
        f"WHERE DB = '{DB_CONFIG['database']}' "
        "AND ID <> CONNECTION_ID()"
    )
    result = run_mysql(sql=process_sql.encode('utf-8'))
    if result.returncode != 0:
        print_mysql_error("检查数据库连接失败", result)
        return False

    lines = result.stdout.decode('utf-8', errors='replace').splitlines()
    session_ids = [line.strip() for line in lines[1:] if line.strip().isdigit()]
    if not session_ids:
        return True

    print(f"   发现 {len(session_ids)} 个正在使用 {DB_CONFIG['database']} 的连接，准备断开...")
    kill_sql = " ".join(f"KILL {sid};" for sid in session_ids).encode('utf-8')
    result = run_mysql(sql=kill_sql)
    if result.returncode != 0:
        print_mysql_error("断开占用连接失败", result)
        return False
    return True


def verify_with_mysql_cli():
    """在缺少 Python MySQL 依赖时，用 mysql CLI 校验完整业务表。"""
    table_check_sql = (
        "SELECT TABLE_NAME "
        "FROM INFORMATION_SCHEMA.TABLES "
        f"WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}' "
        "AND TABLE_TYPE = 'BASE TABLE'"
    )
    result = run_mysql(sql=table_check_sql.encode('utf-8'), database=DB_CONFIG['database'])
    if result.returncode != 0:
        print_mysql_error("校验表结构失败", result)
        return False

    output = result.stdout.decode('utf-8', errors='replace').splitlines()
    existing_tables = set(output[1:]) if output else set()
    expected_table_set = set(EXPECTED_TABLES)
    missing_tables = [table for table in EXPECTED_TABLES if table not in existing_tables]
    unexpected_tables = sorted(existing_tables - expected_table_set)
    if missing_tables:
        print(f"❌ 缺少 DB05 表：{', '.join(missing_tables)}")
        return False
    if unexpected_tables:
        print(f"❌ 存在非 DB05 基础表：{', '.join(unexpected_tables)}")
        return False

    print(f"  业务表结构：{len(EXPECTED_TABLES)} 张表，已全部创建")
    for table_name in EXPECTED_TABLES:
        count_sql = f"SELECT COUNT(*) AS cnt FROM `{table_name}`"
        result = run_mysql(sql=count_sql.encode('utf-8'), database=DB_CONFIG['database'])
        if result.returncode != 0:
            print_mysql_error(f"统计 {table_name} 失败", result)
            return False
        lines = result.stdout.decode('utf-8', errors='replace').splitlines()
        count = lines[1] if len(lines) > 1 else '?'
        print(f"  {table_name:<28} {count} 条")
    return True


def init_data():
    """运行 DB05 的建表和测试数据 SQL"""
    print("=" * 55)
    print("  初始化 dbsample 数据库（完整业务需求）")
    print("=" * 55)

    # 先检查 SQL 文件是否存在，避免后面报 FileNotFoundError 不易理解。
    for sql_file in (SCHEMA_SQL, DATA_SQL):
        if not sql_file.exists():
            print(f"❌ SQL 文件不存在：{sql_file}")
            return

    # 先删除再创建，确保旧实验表、视图、过程等不会影响本次作业环境。
    # 这一步会清空原 dbsample 的全部数据，适合作业环境重置。
    print("\n1. 重建数据库...")
    if not close_database_sessions():
        return
    create_sql = (
        f"DROP DATABASE IF EXISTS `{DB_CONFIG['database']}`; "
        f"CREATE DATABASE `{DB_CONFIG['database']}` "
        "CHARACTER SET gb18030 COLLATE gb18030_chinese_ci"
    ).encode('utf-8')
    result = run_mysql(sql=create_sql)
    if result.returncode != 0:
        print_mysql_error("重建数据库失败", result)
        return

    # 建表：执行老师给的/案例里的 dbsample.sql。
    print("2. 创建表结构...")
    result = run_mysql(sql=SCHEMA_SQL.read_bytes(), database=DB_CONFIG['database'])
    if result.returncode != 0:
        print_mysql_error("建表失败", result)
        return

    # 测试数据：执行生成测试数据.sql，填充字典、专业、学生、课程等数据。
    print("3. 生成测试数据...")
    result = run_mysql(sql=DATA_SQL.read_bytes(), database=DB_CONFIG['database'])
    if result.returncode != 0:
        print_mysql_error("测试数据生成失败", result)
        return

    print("4. 创建补充关系表...")
    result = run_mysql(sql=SUPPLEMENT_SCHEMA_SQL.encode('utf-8'), database=DB_CONFIG['database'])
    if result.returncode != 0:
        print_mysql_error("创建补充关系表失败", result)
        return

    print("5. 生成补充关系数据...")
    result = run_mysql(sql=SUPPLEMENT_DATA_SQL.encode('utf-8'), database=DB_CONFIG['database'])
    if result.returncode != 0:
        print_mysql_error("生成补充关系数据失败", result)
        return

    # 验证：优先用 Python 连接验证；缺少依赖时退回 mysql CLI 验证。
    print("\n6. 验证数据...")
    try:
        from database import Database
    except ModuleNotFoundError as e:
        print(f"⚠️ Python 连接验证不可用：缺少依赖 {e.name}")
        print("   可先运行：python -m pip install -r requirements.txt")
        print("   改用 mysql 命令行校验完整业务表...")
        verify_with_mysql_cli()
        print("\n✅ 数据库初始化完成！")
        return

    db = Database(**DB_CONFIG)
    if db.connect():
        db.cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
        existing_tables = {next(iter(row.values())) for row in db.cursor.fetchall()}
        expected_table_set = set(EXPECTED_TABLES)
        missing_tables = [table for table in EXPECTED_TABLES if table not in existing_tables]
        unexpected_tables = sorted(existing_tables - expected_table_set)
        if missing_tables:
            print(f"❌ 缺少 DB05 表：{', '.join(missing_tables)}")
            db.close()
            return
        if unexpected_tables:
            print(f"❌ 存在非 DB05 基础表：{', '.join(unexpected_tables)}")
            db.close()
            return

        print(f"  业务表结构：{len(EXPECTED_TABLES)} 张表，已全部创建")
        for table_name in EXPECTED_TABLES:
            db.cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table_name}")
            print(f"  {table_name:<28} {db.cursor.fetchone()['cnt']} 条")
        db.close()

    print("\n✅ 数据库初始化完成！")


if __name__ == "__main__":
    init_data()
