"""数据访问层 —— 数据库应用系统的"中间件"核心

本模块是教学演示的关键部分，展示数据库应用系统中"中间件"的完整实现：
1. 应用程序(Flask)不直接访问数据库，而是通过本层的 Database 类
2. Database 类封装了所有 SQL 操作，提供统一的数据访问接口
3. 使用参数化查询防止 SQL 注入（预处理语句）
4. 展示嵌入式 SQL 的核心概念：宿主语言(Python)中嵌入 SQL 语句

对应 PPT 教学内容：
- 嵌入式 SQL：Python 作为宿主语言，SQL 语句嵌入其中
- 共享变量：Python 变量传递给 SQL（参数化查询中的 %s 占位符）
- SQL 通信区：cursor 对象承载 SQL 执行状态信息
- 游标：cursor 处理查询结果集

参考：week09/stu_app_v1_04/database.py 的实现模式
"""

import mysql.connector
from mysql.connector import Error


class Database:
    """数据库访问中间层

    为 Flask 应用提供统一的数据访问接口，屏蔽底层 MySQL 的具体实现。
    这体现了中间件的核心价值：上层应用不需要知道底层 DBMS 的类型和细节。
    """

    def __init__(self, host, database, user, password, charset='utf8mb4', **kwargs):
        """初始化数据库连接配置（不立即连接）"""
        self.conn_config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'charset': charset,
            'use_unicode': kwargs.pop('use_unicode', True),
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """建立数据库连接

        Returns:
            bool: 连接成功返回 True，失败返回 False
        """
        try:
            self.connection = mysql.connector.connect(**self.conn_config)
            self.cursor = self.connection.cursor(dictionary=True)
            print(f"数据库连接成功: {self.conn_config['host']}/{self.conn_config['database']}")
            return True
        except Error as e:
            print(f"数据库连接失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("数据库连接已关闭")

    # ==================== 学生相关操作 ====================

    def get_all_students(self):
        """查询所有学生 —— 演示嵌入式 SQL 的 SELECT 操作

        宿主语言(Python)中嵌入 SQL 语句，通过 cursor 执行。
        cursor 充当了"SQL 通信区"的角色：承载执行状态和结果。
        """
        sql = "SELECT ID, Name, Sex, Age, Dept, RID FROM student ORDER BY ID"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_student_by_id(self, student_id):
        """查询单个学生 —— 演示带参数的嵌入式 SQL

        使用 %s 占位符实现参数化查询，类似于 PPT 中动态嵌入式 SQL 的 ? 占位符。
        Python 变量 student_id 作为"共享变量"向 SQL 语句传递数据。
        """
        sql = "SELECT ID, Name, Sex, Age, Dept, RID FROM student WHERE ID = %s"
        self.cursor.execute(sql, (student_id,))
        return self.cursor.fetchone()

    def add_student(self, student_id, name, sex, age, dept, rid):
        """新增学生 —— 演示 INSERT 操作"""
        sql = """
            INSERT INTO student (ID, Name, Sex, Age, Dept, RID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (student_id, name, sex, age, dept, rid))
        self.connection.commit()

    def update_student(self, student_id, name, sex, age, dept):
        """更新学生信息 —— 演示 UPDATE 操作"""
        sql = """
            UPDATE student
            SET Name = %s, Sex = %s, Age = %s, Dept = %s
            WHERE ID = %s
        """
        self.cursor.execute(sql, (name, sex, age, dept, student_id))
        self.connection.commit()

    def delete_student(self, student_id):
        """删除学生 —— 演示 DELETE 操作（含外键约束处理）

        必须先删除选课记录，再删除学生（参照 week09 的级联删除模式）。
        """
        # 先删除选课记录（外键约束）
        self.cursor.execute(
            "DELETE FROM student_course_retake WHERE StudentID = %s", (student_id,))
        self.cursor.execute(
            "DELETE FROM student_course WHERE StudentID = %s", (student_id,))
        # 再删除学生
        self.cursor.execute(
            "DELETE FROM student WHERE ID = %s", (student_id,))
        self.connection.commit()

    # ==================== 课程相关操作 ====================

    def get_all_courses(self):
        """查询所有课程（含先修课信息）"""
        sql = """
            SELECT c.ID, c.Name, c.Credit, c.PID,
                   pc.Name AS PrerequisiteName
            FROM course c
            LEFT JOIN course pc ON c.PID = pc.ID
            ORDER BY c.ID
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_course_by_id(self, course_id):
        """查询单个课程"""
        sql = """
            SELECT c.ID, c.Name, c.Credit, c.PID,
                   pc.Name AS PrerequisiteName
            FROM course c
            LEFT JOIN course pc ON c.PID = pc.ID
            WHERE c.ID = %s
        """
        self.cursor.execute(sql, (course_id,))
        return self.cursor.fetchone()

    # ==================== 选课相关操作 ====================

    def get_student_courses(self, student_id):
        """查询学生的选课记录 —— 演示多表连接"""
        sql = """
            SELECT sc.CourseID, c.Name AS CourseName, c.Credit,
                   sc.Grade,
                   CASE WHEN sc.Grade >= 60 THEN '及格' ELSE '不及格' END AS GradeLevel
            FROM student_course sc
            JOIN course c ON sc.CourseID = c.ID
            WHERE sc.StudentID = %s
            ORDER BY sc.CourseID
        """
        self.cursor.execute(sql, (student_id,))
        return self.cursor.fetchall()

    def get_course_students(self, course_id):
        """查询某门课程的选课学生"""
        sql = """
            SELECT sc.StudentID, s.Name AS StudentName, sc.Grade,
                   s.Dept
            FROM student_course sc
            JOIN student s ON sc.StudentID = s.ID
            WHERE sc.CourseID = %s
            ORDER BY sc.StudentID
        """
        self.cursor.execute(sql, (course_id,))
        return self.cursor.fetchall()

    # ==================== 函数演示 ====================

    def create_function_get_total_credit(self):
        """创建自定义函数 fn_GetTotalCreditBySID

        该函数对应实验任务1：统计学生已获得的总学分。
        演示了 MySQL 函数的创建与调用。

        规则：
        - 只统计成绩 >= 60 的课程
        - 使用 SUM + 多表连接
        - 无记录时返回 0
        """
        try:
            self.cursor.execute("DROP FUNCTION IF EXISTS fn_GetTotalCreditBySID")
        except Error:
            pass

        # 直接拼接 SQL 语句，将函数体的分号替换为其他分隔符
        # mysql-connector 会把整个字符串作为单条语句发送
        sql = "CREATE FUNCTION fn_GetTotalCreditBySID(p_sid INT) RETURNS DECIMAL(5,1) DETERMINISTIC READS SQL DATA BEGIN DECLARE total_credit DECIMAL(5,1) DEFAULT 0; SELECT IFNULL(SUM(c.Credit), 0) INTO total_credit FROM student_course sc JOIN course c ON sc.CourseID = c.ID WHERE sc.StudentID = p_sid AND sc.Grade >= 60; RETURN total_credit; END"
        self.cursor.execute(sql)
        return True

    def call_fn_get_total_credit(self, student_id):
        """调用自定义函数 —— 演示嵌入式 SQL 中函数的调用方式"""
        sql = "SELECT fn_GetTotalCreditBySID(%s) AS TotalCredit"
        self.cursor.execute(sql, (student_id,))
        result = self.cursor.fetchone()
        return result['TotalCredit'] if result else 0

    # ==================== 存储过程演示 ====================

    def create_procedure_course_stat(self):
        """创建存储过程 sp_CourseStat

        该存储过程对应实验任务2：统计课程修读情况。
        演示了 MySQL 存储过程的创建、输入输出参数、流程控制。

        一条聚合查询 SELECT ... INTO 实现所有统计。
        """
        # 先删除旧过程
        try:
            self.cursor.execute("DROP PROCEDURE IF EXISTS sp_CourseStat")
        except Error:
            pass

        sql = "CREATE PROCEDURE sp_CourseStat(IN p_cid INT, OUT out_avg_grade DECIMAL(5,2), OUT out_max_grade DECIMAL(5,2), OUT out_min_grade DECIMAL(5,2), OUT out_pass_num INT, OUT out_total_num INT) BEGIN SELECT IFNULL(AVG(Grade), 0), IFNULL(MAX(Grade), 0), IFNULL(MIN(Grade), 0), IFNULL(SUM(CASE WHEN Grade >= 60 THEN 1 ELSE 0 END), 0), COUNT(*) INTO out_avg_grade, out_max_grade, out_min_grade, out_pass_num, out_total_num FROM student_course WHERE CourseID = p_cid; END"
        self.cursor.execute(sql)
        return True

    def call_sp_course_stat(self, course_id):
        """调用存储过程 —— 演示 OUT 参数的使用

        存储过程的调用方式与普通 SQL 不同，使用 CALL 语句。
        输出参数通过用户变量 @ 传递回宿主语言。
        这体现了存储过程"减少通信量"的优势：
        一次调用返回多组统计值，而不是多次查询。
        """
        sql = """
            CALL sp_CourseStat(%s, @avg, @max, @min, @pass, @total)
        """
        self.cursor.execute(sql, (course_id,))
        # 获取输出参数值
        self.cursor.execute(
            "SELECT @avg AS avg_grade, @max AS max_grade, @min AS min_grade, @pass AS pass_num, @total AS total_num"
        )
        return self.cursor.fetchone()

    # ==================== 数据库初始化 ====================

    def run_sql_file(self, filepath):
        """执行 SQL 文件 —— 用于初始化数据库表结构和数据

        Args:
            filepath: SQL 文件的绝对路径
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 按语句分割执行（简单分割，适合教学用）
        statements = []
        current = []
        for line in sql_content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('SET'):
                continue
            if stripped:
                current.append(stripped)
            if stripped.endswith(';') and not stripped.upper().startswith('CREATE'):
                statements.append(' '.join(current))
                current = []

        for stmt in statements:
            try:
                self.cursor.execute(stmt)
            except Error as e:
                print(f"SQL 执行警告: {e}")

        self.connection.commit()
        print(f"SQL 文件执行完成: {filepath}")
        return True

    # ==================== 触发器演示 ====================

    def create_trigger_grade_check(self):
        """创建触发器 trg_grade_check

        在学生选课记录插入或更新时，自动检查成绩是否在 0-100 范围内。
        如果成绩不合法，抛出错误阻止操作。

        这演示了触发器作为"数据库完整性约束自动执行机制"的用法。
        """
        try:
            self.cursor.execute("DROP TRIGGER IF EXISTS trg_grade_check")
        except Error:
            pass

        sql = "CREATE TRIGGER trg_grade_check BEFORE INSERT ON student_course FOR EACH ROW BEGIN IF NEW.Grade IS NOT NULL AND (NEW.Grade < 0 OR NEW.Grade > 100) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '成绩必须在 0-100 之间'; END IF; END"
        self.cursor.execute(sql)
        return True

    def init_db_objects(self):
        """初始化数据库高级对象（函数、存储过程、触发器）

        在基础表和数据就绪后调用，创建教学演示所需的函数、存储过程和触发器。
        """
        self.create_function_get_total_credit()
        print("函数 fn_GetTotalCreditBySID 创建完成")
        self.create_procedure_course_stat()
        print("存储过程 sp_CourseStat 创建完成")
        self.create_trigger_grade_check()
        print("触发器 trg_grade_check 创建完成")
        return True

    # ==================== 实验任务自动评测 ====================

    def grade_task1(self, student_sql):
        """评测任务1：自定义函数 fn_GetTotalCreditBySID

        执行学生提交的 SQL，创建函数后用测试用例验证。
        评测完成后清理（DROP FUNCTION）。

        Returns:
            dict: {
                'success': bool,
                'syntax_error': str or None,
                'test_cases': list,
                'score': int
            }
        """
        results = {
            'success': False,
            'syntax_error': None,
            'test_cases': [],
            'score': 0
        }

        # 清理可能存在的旧函数（避免命名冲突）
        try:
            self.cursor.execute("DROP FUNCTION IF EXISTS fn_GetTotalCreditBySID")
            self.connection.commit()
        except Error:
            pass

        # 执行学生提交的 SQL（将多行转为单行，避免内部 semicolon 被错误解析）
        try:
            single_line_sql = ' '.join(student_sql.split())
            self.cursor.execute(single_line_sql)
            self.connection.commit()
        except Error as e:
            results['syntax_error'] = str(e)
            return results

        # 测试用例：(学号, 预期结果, 描述)
        test_cases = [
            (200215121, 10.0, '李勇（3门及格课）'),
            (200215125, 0, '张立（无选课记录）'),
            (999999, 0, '不存在的学号'),
        ]

        for sid, expected, desc in test_cases:
            try:
                self.cursor.execute(
                    "SELECT fn_GetTotalCreditBySID(%s) AS result",
                    (sid,)
                )
                row = self.cursor.fetchone()
                actual = float(row['result']) if row and row['result'] is not None else 0
                passed = abs(actual - expected) < 0.01
                results['test_cases'].append({
                    'desc': desc,
                    'input': sid,
                    'expected': expected,
                    'actual': round(actual, 1),
                    'passed': passed
                })
            except Error as e:
                results['test_cases'].append({
                    'desc': desc,
                    'input': sid,
                    'expected': expected,
                    'actual': None,
                    'passed': False,
                    'error': str(e)
                })

        # 计算得分
        passed_count = sum(1 for tc in results['test_cases'] if tc['passed'])
        results['score'] = int(passed_count / len(test_cases) * 100)
        results['success'] = results['score'] == 100

        # 清理：删除学生创建的函数
        try:
            self.cursor.execute("DROP FUNCTION IF EXISTS fn_GetTotalCreditBySID")
            self.connection.commit()
        except Error:
            pass

        return results

    def grade_task2(self, student_sql):
        """评测任务2：存储过程 sp_CourseStat

        执行学生提交的 SQL，创建存储过程后用测试用例验证。
        评测完成后清理（DROP PROCEDURE）。

        Returns:
            dict: {
                'success': bool,
                'syntax_error': str or None,
                'test_cases': list,
                'score': int
            }
        """
        results = {
            'success': False,
            'syntax_error': None,
            'test_cases': [],
            'score': 0
        }

        # 清理可能存在的旧存储过程
        try:
            self.cursor.execute("DROP PROCEDURE IF EXISTS sp_CourseStat")
            self.connection.commit()
        except Error:
            pass

        # 执行学生提交的 SQL（将多行转为单行，避免内部 semicolon 被错误解析）
        try:
            single_line_sql = ' '.join(student_sql.split())
            self.cursor.execute(single_line_sql)
            self.connection.commit()
        except Error as e:
            results['syntax_error'] = str(e)
            return results

        # 测试用例：(课程ID, 预期结果, 描述)
        test_cases = [
            (1, {'avg': 93.0, 'max': 93.0, 'min': 93.0, 'pass': 1, 'total': 1}, '数据库（李勇 93.0）'),
            (2, {'avg': 88.5, 'max': 91.0, 'min': 86.0, 'pass': 2, 'total': 2}, '数学（李勇 86.0, 刘晨 91.0）'),
            (999, {'avg': 0, 'max': 0, 'min': 0, 'pass': 0, 'total': 0}, '不存在的课程'),
        ]

        for cid, expected, desc in test_cases:
            try:
                self.cursor.execute(
                    "CALL sp_CourseStat(%s, @avg, @max, @min, @pass, @total)",
                    (cid,)
                )
                self.cursor.execute(
                    "SELECT @avg AS avg_grade, @max AS max_grade, @min AS min_grade, @pass AS pass_num, @total AS total_num"
                )
                row = self.cursor.fetchone()

                actual = {
                    'avg': float(row['avg_grade']) if row and row['avg_grade'] is not None else 0,
                    'max': float(row['max_grade']) if row and row['max_grade'] is not None else 0,
                    'min': float(row['min_grade']) if row and row['min_grade'] is not None else 0,
                    'pass': int(row['pass_num']) if row and row['pass_num'] is not None else 0,
                    'total': int(row['total_num']) if row and row['total_num'] is not None else 0,
                }

                passed = (
                    abs(actual['avg'] - expected['avg']) < 0.01 and
                    abs(actual['max'] - expected['max']) < 0.01 and
                    abs(actual['min'] - expected['min']) < 0.01 and
                    actual['pass'] == expected['pass'] and
                    actual['total'] == expected['total']
                )

                results['test_cases'].append({
                    'desc': desc,
                    'input': cid,
                    'expected_display': f"avg={expected['avg']}, max={expected['max']}, min={expected['min']}, pass={expected['pass']}, total={expected['total']}",
                    'actual_display': f"avg={actual['avg']}, max={actual['max']}, min={actual['min']}, pass={actual['pass']}, total={actual['total']}",
                    'passed': passed
                })
            except Error as e:
                results['test_cases'].append({
                    'desc': desc,
                    'input': cid,
                    'expected_display': f"avg={expected['avg']}, max={expected['max']}, min={expected['min']}, pass={expected['pass']}, total={expected['total']}",
                    'actual_display': None,
                    'passed': False,
                    'error': str(e)
                })

        # 计算得分
        passed_count = sum(1 for tc in results['test_cases'] if tc['passed'])
        results['score'] = int(passed_count / len(test_cases) * 100)
        results['success'] = results['score'] == 100

        # 清理：删除学生创建的存储过程
        try:
            self.cursor.execute("DROP PROCEDURE IF EXISTS sp_CourseStat")
            self.connection.commit()
        except Error:
            pass

        return results
