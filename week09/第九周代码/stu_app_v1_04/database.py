"""DB05 数据库操作类 —— 适配 dbsample 16 表架构。

本文件集中放置 SQL，是课堂讲解数据库应用设计的重点文件。

分层关系：
- main.py 负责和用户交互。
- models.py 负责承载用户输入。
- database.py 负责把业务操作翻译成 SQL。

当前版本：
- DB05 示例 SQL 的 16 张表作为基础。
- 为覆盖原始业务描述，补充 major_course 和 teacher_guidance 两张关系表。
- 高级对象演示只创建视图、触发器、存储过程、函数。
- 所有用户输入值尽量使用参数化 SQL，避免把值直接拼进 SQL。
"""
import mysql.connector
from mysql.connector import Error
from datetime import date
import re


class Database:
    """数据库操作类。

    每个方法通常对应一个数据库应用功能，例如“添加学生”“设置主修专业”。
    学生阅读时可以从方法名反推它操作的表。
    """

    def __init__(self, host, database, user, password):
        # DB05 物理设计要求字符集 gb18030，这里保持和建表 SQL 一致。
        self.connection_config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'charset': 'gb18030',
            'use_unicode': True
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """建立 MySQL 连接。

        cursor(dictionary=True) 会让查询结果以字典形式返回，
        例如 row['Name']，比按列下标 row[1] 更适合教学阅读。
        """
        try:
            self.connection = mysql.connector.connect(**self.connection_config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ 数据库连接成功")
            return True
        except Error as e:
            print(f"❌ 数据库连接失败：{e}")
            return False

    # ==================== 数据字典查询 ====================
    # 三张 dd_ 开头的表是标准/枚举数据。
    # 应用程序通常只读取它们，用作下拉选项或外键引用。

    def get_sex_options(self):
        """获取性别选项"""
        self.cursor.execute("SELECT AID, Code, Name FROM dd_sex")
        return self.cursor.fetchall()

    def get_title_options(self):
        """获取职称选项"""
        self.cursor.execute("SELECT AID, Code, Name, Level FROM dd_professional_title ORDER BY Level")
        return self.cursor.fetchall()

    def get_division_options(self, level=None):
        """获取行政区划选项"""
        if level:
            self.cursor.execute(
                "SELECT AID, Code, Name, FullName FROM dd_administrative_divisions WHERE Level=%s",
                (level,))
        else:
            self.cursor.execute(
                "SELECT AID, Code, Name, FullName, Level FROM dd_administrative_divisions ORDER BY Level, Code")
        return self.cursor.fetchall()

    # ==================== 专业相关 ====================
    # major 是专业实体表；major_leader 是“专业-负责人教师”的 1:1 关系表。

    def get_all_majors(self):
        self.cursor.execute("SELECT AID, Code, Name, Years FROM major ORDER BY Code")
        return self.cursor.fetchall()

    def get_all_majors_detail(self):
        # LEFT JOIN 用来显示专业负责人；没有负责人时专业仍然应该显示。
        query = """
        SELECT m.AID, m.Code, m.Name, m.Years,
               t.Code AS LeaderCode, t.Name AS LeaderName
        FROM major m
        LEFT JOIN major_leader ml ON m.AID = ml.MajorAID
        LEFT JOIN teacher t ON ml.LeaderAID = t.AID
        ORDER BY m.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_major_by_code(self, code):
        self.cursor.execute("SELECT AID, Code, Name, Years FROM major WHERE Code=%s", (code,))
        return self.cursor.fetchone()

    def get_major_by_aid(self, aid):
        self.cursor.execute("SELECT AID, Code, Name, Years FROM major WHERE AID=%s", (aid,))
        return self.cursor.fetchone()

    def add_major(self, major):
        """新增专业。

        AID 是数据库自增主键，应用层只提交 Code/Name/Years。
        Code 和 Name 的唯一性由数据库唯一索引保证。
        """
        try:
            self.cursor.execute(
                "INSERT INTO major (Code, Name, Years) VALUES (%s,%s,%s)",
                (major.code, major.name, major.years))
            major_aid = self.cursor.lastrowid
            self.connection.commit()
            print(f"✅ 专业 {major.name}（{major.code}）添加成功，AID={major_aid}")
            return major_aid
        except Error as e:
            print(f"❌ 添加专业失败：{e}")
            return None

    def search_major(self, keyword):
        pattern = f"%{keyword}%"
        query = """
        SELECT m.AID, m.Code, m.Name, m.Years,
               t.Code AS LeaderCode, t.Name AS LeaderName
        FROM major m
        LEFT JOIN major_leader ml ON m.AID = ml.MajorAID
        LEFT JOIN teacher t ON ml.LeaderAID = t.AID
        WHERE m.Code LIKE %s OR m.Name LIKE %s
        ORDER BY m.Code
        """
        self.cursor.execute(query, (pattern, pattern))
        return self.cursor.fetchall()

    def update_major(self, aid, update_data):
        fields = []
        values = []
        for k, v in update_data.items():
            if v is not None:
                fields.append(f"{k}=%s")
                values.append(v)
        if not fields:
            return False
        values.append(aid)
        query = f"UPDATE major SET {', '.join(fields)} WHERE AID=%s"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("✅ 专业信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新专业失败：{e}")
            return False

    def delete_major(self, aid):
        try:
            self.cursor.execute("DELETE FROM major WHERE AID=%s", (aid,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 专业删除成功")
                return True
            print("❌ 专业不存在")
            return False
        except Error as e:
            print(f"❌ 删除专业失败：{e}")
            return False

    def set_major_leader(self, major_aid, teacher_aid):
        """设置专业负责人，对应 major_leader 表。

        major_leader.MajorAID 是主键，表示一个专业最多一名负责人；
        LeaderAID 有唯一索引，表示一个教师最多负责一个专业。
        """
        try:
            self.cursor.execute(
                "INSERT INTO major_leader (MajorAID, LeaderAID) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE LeaderAID=VALUES(LeaderAID)",
                (major_aid, teacher_aid))
            self.connection.commit()
            print("✅ 专业负责人设置成功")
            return True
        except Error as e:
            print(f"❌ 设置专业负责人失败：{e}")
            return False

    # ==================== 学生相关 ====================
    # student 只保存学生基本属性。
    # 主修、辅修、电话分别拆到 student_major1、student_major2、student_phone。

    def add_student(self, student):
        """添加学生基本信息，只写 student 表。

        主修专业、辅修专业、电话由调用方随后分别写入关系表。
        这样可以对应课堂中的“实体表”和“联系表/多值属性表”。
        """
        try:
            self.connection.start_transaction()
            self.cursor.execute(
                "INSERT INTO student (Code, Name, SexAID, Birthday, YearInroll, AddressCVAID, AddressDetail) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (student.code, student.name, student.sex_aid, student.birthday,
                 student.year_inroll, student.address_cv_aid, student.address_detail))
            student_aid = self.cursor.lastrowid
            self.connection.commit()
            print(f"✅ 学生 {student.name}（{student.code}）添加成功，AID={student_aid}")
            return student_aid
        except Error as e:
            self.connection.rollback()
            print(f"❌ 添加失败：{e}")
            return None

    def set_student_major1(self, student_aid, major_aid):
        """设置学生主修专业，对应 student_major1。

        StudentAID 是主键，所以一个学生只能有一个主修专业。
        ON DUPLICATE KEY UPDATE 用于“已有则修改，没有则新增”。
        """
        try:
            self.cursor.execute(
                "INSERT INTO student_major1 (StudentAID, MajorAID) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE MajorAID=VALUES(MajorAID)",
                (student_aid, major_aid))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ 设置主修专业失败：{e}")
            return False

    def set_student_major2(self, student_aid, major_aid):
        """设置学生辅修专业，对应 student_major2。

        StudentAID 是主键，所以一个学生最多一个辅修专业。
        """
        try:
            self.cursor.execute(
                "INSERT INTO student_major2 (StudentAID, MajorAID) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE MajorAID=VALUES(MajorAID)",
                (student_aid, major_aid))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ 设置辅修专业失败：{e}")
            return False

    def add_student_phone(self, student_aid, phone_number, flag_type='2', is_commonly_used=True):
        """添加学生电话，对应 student_phone。

        电话号码 PhoneNumber 是主键，体现电话作为多值属性被单独建表。
        """
        try:
            self.cursor.execute(
                "INSERT INTO student_phone (StudentAID, PhoneNumber, FlagType, IsCommonlyUsed) "
                "VALUES (%s,%s,%s,%s)",
                (student_aid, phone_number, flag_type,
                 1 if is_commonly_used else 0))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ 添加电话失败：{e}")
            return False

    def get_all_students(self):
        # 学生列表需要跨表展示：student + 性别字典 + 主修专业 + 行政区划。
        query = """
        SELECT s.AID, s.Code, s.Name, sx.Name AS SexName,
               s.Birthday, s.YearInroll, s.AddressDetail,
               m.Code AS MajorCode, m.Name AS MajorName,
               d.FullName AS AddressFullName
        FROM student s
        JOIN dd_sex sx ON s.SexAID = sx.AID
        LEFT JOIN student_major1 sm1 ON s.AID = sm1.StudentAID
        LEFT JOIN major m ON sm1.MajorAID = m.AID
        LEFT JOIN dd_administrative_divisions d ON s.AddressCVAID = d.AID
        ORDER BY s.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_student(self, keyword):
        query = """
        SELECT s.AID, s.Code, s.Name, sx.Name AS SexName,
               s.Birthday, s.YearInroll, s.AddressDetail,
               m.Code AS MajorCode, m.Name AS MajorName,
               d.FullName AS AddressFullName
        FROM student s
        JOIN dd_sex sx ON s.SexAID = sx.AID
        LEFT JOIN student_major1 sm1 ON s.AID = sm1.StudentAID
        LEFT JOIN major m ON sm1.MajorAID = m.AID
        LEFT JOIN dd_administrative_divisions d ON s.AddressCVAID = d.AID
        WHERE s.Code LIKE %s OR s.Name LIKE %s
        ORDER BY s.Code
        """
        pattern = f"%{keyword}%"
        self.cursor.execute(query, (pattern, pattern))
        return self.cursor.fetchall()

    def get_student_by_code(self, code):
        query = """
        SELECT s.*, sx.Name AS SexName
        FROM student s
        JOIN dd_sex sx ON s.SexAID = sx.AID
        WHERE s.Code=%s
        """
        self.cursor.execute(query, (code,))
        return self.cursor.fetchone()

    def get_student_by_aid(self, aid):
        query = """
        SELECT s.*, sx.Name AS SexName
        FROM student s
        JOIN dd_sex sx ON s.SexAID = sx.AID
        WHERE s.AID=%s
        """
        self.cursor.execute(query, (aid,))
        return self.cursor.fetchone()

    def update_student(self, aid, update_data):
        fields = []
        values = []
        for k, v in update_data.items():
            if v is not None:
                fields.append(f"{k}=%s")
                values.append(v)
        if not fields:
            return False
        values.append(aid)
        query = f"UPDATE student SET {', '.join(fields)} WHERE AID=%s"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("✅ 学生信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新失败：{e}")
            return False

    def delete_student(self, aid):
        try:
            # DB05 外键是 ON DELETE RESTRICT。
            # 因此删除学生前，应用层先删除依赖该学生的关系记录。
            self.connection.start_transaction()
            self.cursor.execute("DELETE FROM student_course WHERE StudentAID=%s", (aid,))
            self.cursor.execute("DELETE FROM student_phone WHERE StudentAID=%s", (aid,))
            self.cursor.execute("DELETE FROM student_major2 WHERE StudentAID=%s", (aid,))
            self.cursor.execute("DELETE FROM student_major1 WHERE StudentAID=%s", (aid,))
            self.cursor.execute("DELETE FROM teacher_guidance WHERE StudentAID=%s", (aid,))
            self.cursor.execute("DELETE FROM student WHERE AID=%s", (aid,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 学生删除成功")
                return True
            else:
                print("❌ 学生不存在")
                return False
        except Error as e:
            self.connection.rollback()
            print(f"❌ 删除失败：{e}")
            return False

    def get_student_phones(self, student_aid):
        self.cursor.execute(
            "SELECT PhoneNumber, FlagType, IsCommonlyUsed FROM student_phone WHERE StudentAID=%s",
            (student_aid,))
        return self.cursor.fetchall()

    # ==================== 教师相关 ====================
    # teacher 是教师实体表；teacher_major 表示教师属于哪个专业。

    def add_teacher(self, teacher):
        try:
            self.cursor.execute(
                "INSERT INTO teacher (Code, Name, TitleAID) VALUES (%s,%s,%s)",
                (teacher.code, teacher.name, teacher.title_aid))
            teacher_aid = self.cursor.lastrowid
            self.connection.commit()
            print(f"✅ 教师 {teacher.name}（{teacher.code}）添加成功，AID={teacher_aid}")
            return teacher_aid
        except Error as e:
            print(f"❌ 添加失败：{e}")
            return None

    def set_teacher_major(self, teacher_aid, major_aid):
        """设置教师所属专业，对应 teacher_major。

        TeacherAID 是主键，所以一个教师必须/最多属于一个专业的规则
        可以通过该表结构表达。
        """
        try:
            self.cursor.execute(
                "INSERT INTO teacher_major (TeacherAID, MajorAID) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE MajorAID=VALUES(MajorAID)",
                (teacher_aid, major_aid))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ 设置教师专业失败：{e}")
            return False

    def get_all_teachers(self):
        query = """
        SELECT t.AID, t.Code, t.Name, pt.Name AS TitleName, pt.Level AS TitleLevel,
               m.Code AS MajorCode, m.Name AS MajorName
        FROM teacher t
        JOIN dd_professional_title pt ON t.TitleAID = pt.AID
        LEFT JOIN teacher_major tm ON t.AID = tm.TeacherAID
        LEFT JOIN major m ON tm.MajorAID = m.AID
        ORDER BY t.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_teacher(self, keyword):
        query = """
        SELECT t.AID, t.Code, t.Name, pt.Name AS TitleName, pt.Level AS TitleLevel,
               m.Code AS MajorCode, m.Name AS MajorName
        FROM teacher t
        JOIN dd_professional_title pt ON t.TitleAID = pt.AID
        LEFT JOIN teacher_major tm ON t.AID = tm.TeacherAID
        LEFT JOIN major m ON tm.MajorAID = m.AID
        WHERE t.Code LIKE %s OR t.Name LIKE %s
        ORDER BY t.Code
        """
        pattern = f"%{keyword}%"
        self.cursor.execute(query, (pattern, pattern))
        return self.cursor.fetchall()

    def get_teacher_by_code(self, code):
        query = """
        SELECT t.*, pt.Name AS TitleName
        FROM teacher t
        JOIN dd_professional_title pt ON t.TitleAID = pt.AID
        WHERE t.Code=%s
        """
        self.cursor.execute(query, (code,))
        return self.cursor.fetchone()

    def get_teacher_by_aid(self, aid):
        query = """
        SELECT t.*, pt.Name AS TitleName
        FROM teacher t
        JOIN dd_professional_title pt ON t.TitleAID = pt.AID
        WHERE t.AID=%s
        """
        self.cursor.execute(query, (aid,))
        return self.cursor.fetchone()

    def update_teacher(self, aid, update_data):
        fields = []
        values = []
        for k, v in update_data.items():
            if v is not None:
                fields.append(f"{k}=%s")
                values.append(v)
        if not fields:
            return False
        values.append(aid)
        query = f"UPDATE teacher SET {', '.join(fields)} WHERE AID=%s"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("✅ 教师信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新失败：{e}")
            return False

    def delete_teacher(self, aid):
        try:
            self.cursor.execute("DELETE FROM teacher WHERE AID=%s", (aid,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 教师删除成功")
                return True
            else:
                print("❌ 教师不存在")
                return False
        except Error as e:
            print(f"❌ 删除失败：{e}")
            return False

    # ==================== 课程相关 ====================
    # course 是课程实体表。
    # teacher_course 表示授课教师；course_leader 表示课程负责人。

    def add_course(self, course):
        try:
            self.cursor.execute(
                "INSERT INTO course (Code, Name, Hours, Credit) VALUES (%s,%s,%s,%s)",
                (course.code, course.name, course.hours, course.credit))
            course_aid = self.cursor.lastrowid
            self.connection.commit()
            print(f"✅ 课程 {course.name}（{course.code}）添加成功，AID={course_aid}")
            return course_aid
        except Error as e:
            print(f"❌ 添加失败：{e}")
            return None

    def set_course_teacher(self, course_aid, teacher_aid):
        """设置授课教师（teacher_course 表，PK=CourseAID）"""
        try:
            self.cursor.execute(
                "INSERT INTO teacher_course (CourseAID, TeacherAID) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE TeacherAID=VALUES(TeacherAID)",
                (course_aid, teacher_aid))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ 设置授课教师失败：{e}")
            return False

    def set_course_leader(self, course_aid, teacher_aid):
        """设置课程负责人，对应 course_leader。

        CourseAID 是主键，表示一门课最多一个负责人；
        LeaderAID 唯一，表示一个教师最多负责一门课。
        """
        try:
            self.cursor.execute(
                "INSERT INTO course_leader (CourseAID, LeaderAID) VALUES (%s,%s) "
                "ON DUPLICATE KEY UPDATE LeaderAID=VALUES(LeaderAID)",
                (course_aid, teacher_aid))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ 设置课程负责人失败：{e}")
            return False

    def get_all_courses(self):
        query = """
        SELECT c.AID, c.Code, c.Name, c.Hours, c.Credit,
               t.Name AS TeacherName, t.Code AS TeacherCode,
               cl.Name AS LeaderName
        FROM course c
        LEFT JOIN teacher_course tc ON c.AID = tc.CourseAID
        LEFT JOIN teacher t ON tc.TeacherAID = t.AID
        LEFT JOIN course_leader clr ON c.AID = clr.CourseAID
        LEFT JOIN teacher cl ON clr.LeaderAID = cl.AID
        ORDER BY c.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_course(self, keyword):
        query = """
        SELECT c.AID, c.Code, c.Name, c.Hours, c.Credit,
               t.Name AS TeacherName, t.Code AS TeacherCode
        FROM course c
        LEFT JOIN teacher_course tc ON c.AID = tc.CourseAID
        LEFT JOIN teacher t ON tc.TeacherAID = t.AID
        WHERE c.Code LIKE %s OR c.Name LIKE %s
        ORDER BY c.Code
        """
        pattern = f"%{keyword}%"
        self.cursor.execute(query, (pattern, pattern))
        return self.cursor.fetchall()

    def get_course_by_code(self, code):
        query = """
        SELECT c.*, t.Name AS TeacherName, t.Code AS TeacherCode
        FROM course c
        LEFT JOIN teacher_course tc ON c.AID = tc.CourseAID
        LEFT JOIN teacher t ON tc.TeacherAID = t.AID
        WHERE c.Code=%s
        """
        self.cursor.execute(query, (code,))
        return self.cursor.fetchone()

    def get_course_by_aid(self, aid):
        query = """
        SELECT c.*, t.Name AS TeacherName, t.Code AS TeacherCode
        FROM course c
        LEFT JOIN teacher_course tc ON c.AID = tc.CourseAID
        LEFT JOIN teacher t ON tc.TeacherAID = t.AID
        WHERE c.AID=%s
        """
        self.cursor.execute(query, (aid,))
        return self.cursor.fetchone()

    def update_course(self, aid, update_data):
        fields = []
        values = []
        for k, v in update_data.items():
            if v is not None:
                fields.append(f"{k}=%s")
                values.append(v)
        if not fields:
            return False
        values.append(aid)
        query = f"UPDATE course SET {', '.join(fields)} WHERE AID=%s"
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("✅ 课程信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新失败：{e}")
            return False

    def delete_course(self, aid):
        try:
            self.cursor.execute("DELETE FROM course WHERE AID=%s", (aid,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 课程删除成功")
                return True
            else:
                print("❌ 课程不存在")
                return False
        except Error as e:
            if "foreign key constraint" in str(e).lower():
                print("❌ 删除失败：该课程有关联数据，无法删除")
            else:
                print(f"❌ 删除失败：{e}")
            return False

    # ==================== 选课相关 ====================
    # student_course 是学生和课程之间的 m:n 关系表。
    # 它同时保存选课日期、学年、学期、成绩、主修/辅修等关系属性。

    def add_course_selection(self, sc_record):
        # 应用层规则：选课前检查先修课程是否已经及格。
        # 这个规则不在 DB05 的外键中表达，所以放在程序逻辑里。
        unmet = self.check_prerequisites(sc_record.student_aid, sc_record.course_aid)
        if unmet:
            names = ", ".join([f"{p['PreCode']}({p['PreName']})" for p in unmet])
            print(f"❌ 选课失败：未通过先修课程 {names}")
            return False

        query = """
        INSERT INTO student_course (StudentAID, CourseAID, ForMajor, RegistDate,
                                     AcademicYear, Semester, Score)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """
        try:
            self.cursor.execute(query, (
                sc_record.student_aid, sc_record.course_aid,
                # ForMajor 存 bit：1=主修，0=辅修。
                1 if sc_record.for_major else 0,
                sc_record.regist_date or date.today(),
                sc_record.academic_year or date.today().year,
                1 if sc_record.semester else 0,
                sc_record.score
            ))
            self.connection.commit()
            print(f"✅ 选课成功")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                print("❌ 选课失败：该学生已选修此课程")
            else:
                print(f"❌ 选课失败：{e}")
            return False

    def check_prerequisites(self, student_aid, course_aid):
        """检查学生是否满足课程先修要求。

        course_prerequisite 记录“某课程需要哪些先修课程”。
        如果学生没有选过先修课，或先修课成绩低于 60，就不能选当前课程。
        """
        query = """
        SELECT cp.PreCourseAID, c.Code AS PreCode, c.Name AS PreName
        FROM course_prerequisite cp
        JOIN course c ON cp.PreCourseAID = c.AID
        LEFT JOIN student_course sc ON sc.StudentAID = %s
            AND sc.CourseAID = cp.PreCourseAID
            AND sc.Score IS NOT NULL AND sc.Score >= 60
        WHERE cp.CourseAID = %s AND sc.StudentAID IS NULL
        """
        self.cursor.execute(query, (student_aid, course_aid))
        return self.cursor.fetchall()

    def add_prerequisite(self, course_aid, pre_course_aid):
        try:
            self.cursor.execute(
                "INSERT INTO course_prerequisite (CourseAID, PreCourseAID) VALUES (%s,%s)",
                (course_aid, pre_course_aid))
            self.connection.commit()
            print("✅ 先修关系设置成功")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                print("❌ 该先修关系已存在")
            else:
                print(f"❌ 设置先修关系失败：{e}")
            return False

    def get_prerequisites(self, course_aid):
        query = """
        SELECT cp.PreCourseAID, c.Code, c.Name
        FROM course_prerequisite cp
        JOIN course c ON cp.PreCourseAID = c.AID
        WHERE cp.CourseAID = %s
        """
        self.cursor.execute(query, (course_aid,))
        return self.cursor.fetchall()

    def get_all_prerequisites(self):
        query = """
        SELECT c1.Code AS CourseCode, c1.Name AS CourseName,
               c2.Code AS PreCode, c2.Name AS PreName
        FROM course_prerequisite cp
        JOIN course c1 ON cp.CourseAID = c1.AID
        JOIN course c2 ON cp.PreCourseAID = c2.AID
        ORDER BY c1.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_prerequisite(self, course_aid, pre_course_aid):
        try:
            self.cursor.execute(
                "DELETE FROM course_prerequisite WHERE CourseAID=%s AND PreCourseAID=%s",
                (course_aid, pre_course_aid))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 先修关系删除成功")
                return True
            else:
                print("❌ 先修关系不存在")
                return False
        except Error as e:
            print(f"❌ 删除先修关系失败：{e}")
            return False

    # ==================== 专业开课相关 ====================
    # major_course 补充原始业务需求：
    # 一门课程可以为 0~n 个专业开设，一个专业可以开设 0~n 门课。

    def add_major_course(self, major_aid, course_aid):
        try:
            self.cursor.execute(
                "INSERT INTO major_course (MajorAID, CourseAID) VALUES (%s,%s)",
                (major_aid, course_aid))
            self.connection.commit()
            print("✅ 专业开课关系设置成功")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                print("❌ 该专业已开设此课程")
            else:
                print(f"❌ 设置专业开课失败：{e}")
            return False

    def get_all_major_courses(self):
        query = """
        SELECT m.AID AS MajorAID, m.Code AS MajorCode, m.Name AS MajorName,
               c.AID AS CourseAID, c.Code AS CourseCode, c.Name AS CourseName
        FROM major_course mc
        JOIN major m ON mc.MajorAID = m.AID
        JOIN course c ON mc.CourseAID = c.AID
        ORDER BY m.Code, c.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_major_courses(self, major_aid):
        query = """
        SELECT c.AID, c.Code, c.Name, c.Hours, c.Credit
        FROM major_course mc
        JOIN course c ON mc.CourseAID = c.AID
        WHERE mc.MajorAID = %s
        ORDER BY c.Code
        """
        self.cursor.execute(query, (major_aid,))
        return self.cursor.fetchall()

    def delete_major_course(self, major_aid, course_aid):
        try:
            self.cursor.execute(
                "DELETE FROM major_course WHERE MajorAID=%s AND CourseAID=%s",
                (major_aid, course_aid))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 专业开课关系删除成功")
                return True
            print("❌ 专业开课关系不存在")
            return False
        except Error as e:
            print(f"❌ 删除专业开课失败：{e}")
            return False

    # ==================== 教师指导相关 ====================
    # teacher_guidance 补充原始业务需求：
    # 教师指导 0~n 个学生；一个学生被 1 个教师指导，并记录起止日期。

    def set_teacher_guidance(self, student_aid, teacher_aid, start_date, end_date=None):
        try:
            self.cursor.execute(
                "INSERT INTO teacher_guidance (StudentAID, TeacherAID, StartDate, EndDate) "
                "VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE TeacherAID=VALUES(TeacherAID), "
                "StartDate=VALUES(StartDate), EndDate=VALUES(EndDate)",
                (student_aid, teacher_aid, start_date, end_date))
            self.connection.commit()
            print("✅ 教师指导关系保存成功")
            return True
        except Error as e:
            print(f"❌ 保存教师指导关系失败：{e}")
            return False

    def get_all_teacher_guidance(self):
        query = """
        SELECT tg.StudentAID, s.Code AS StudentCode, s.Name AS StudentName,
               tg.TeacherAID, t.Code AS TeacherCode, t.Name AS TeacherName,
               tg.StartDate, tg.EndDate
        FROM teacher_guidance tg
        JOIN student s ON tg.StudentAID = s.AID
        JOIN teacher t ON tg.TeacherAID = t.AID
        ORDER BY t.Code, s.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_student_guidance(self, student_aid):
        query = """
        SELECT tg.StudentAID, s.Code AS StudentCode, s.Name AS StudentName,
               tg.TeacherAID, t.Code AS TeacherCode, t.Name AS TeacherName,
               tg.StartDate, tg.EndDate
        FROM teacher_guidance tg
        JOIN student s ON tg.StudentAID = s.AID
        JOIN teacher t ON tg.TeacherAID = t.AID
        WHERE tg.StudentAID = %s
        """
        self.cursor.execute(query, (student_aid,))
        return self.cursor.fetchone()

    def delete_teacher_guidance(self, student_aid):
        try:
            self.cursor.execute("DELETE FROM teacher_guidance WHERE StudentAID=%s", (student_aid,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 教师指导关系删除成功")
                return True
            print("❌ 指导关系不存在")
            return False
        except Error as e:
            print(f"❌ 删除教师指导关系失败：{e}")
            return False

    def get_student_courses(self, student_aid):
        query = """
        SELECT sc.AID, sc.StudentAID, sc.CourseAID, sc.ForMajor,
               sc.RegistDate, sc.AcademicYear, sc.Semester, sc.Score, sc.HasPassed,
               c.Code AS CourseCode, c.Name AS CourseName, c.Credit,
               t.Name AS TeacherName
        FROM student_course sc
        JOIN course c ON sc.CourseAID = c.AID
        LEFT JOIN teacher_course tc ON c.AID = tc.CourseAID
        LEFT JOIN teacher t ON tc.TeacherAID = t.AID
        WHERE sc.StudentAID = %s
        ORDER BY sc.AcademicYear, sc.Semester, c.Code
        """
        self.cursor.execute(query, (student_aid,))
        return self.cursor.fetchall()

    def get_all_course_selections(self):
        query = """
        SELECT sc.AID, s.Code AS StudentCode, s.Name AS StudentName,
               c.Code AS CourseCode, c.Name AS CourseName,
               c.Credit, sc.ForMajor, sc.RegistDate,
               sc.AcademicYear, sc.Semester, sc.Score, sc.HasPassed,
               t.Name AS TeacherName
        FROM student_course sc
        JOIN student s ON sc.StudentAID = s.AID
        JOIN course c ON sc.CourseAID = c.AID
        LEFT JOIN teacher_course tc ON c.AID = tc.CourseAID
        LEFT JOIN teacher t ON tc.TeacherAID = t.AID
        ORDER BY s.Code, sc.AcademicYear, sc.Semester, c.Code
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def drop_course_selection(self, sc_aid):
        try:
            self.cursor.execute("DELETE FROM student_course WHERE AID=%s", (sc_aid,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("✅ 退课成功")
                return True
            else:
                print("❌ 退课失败：未找到对应的选课记录")
                return False
        except Error as e:
            print(f"❌ 退课失败：{e}")
            return False

    def update_score(self, sc_aid, score):
        """更新成绩。

        只写 Score 字段；HasPassed 是 MySQL 虚拟生成列，会自动计算。
        """
        try:
            self.cursor.execute(
                "UPDATE student_course SET Score=%s WHERE AID=%s",
                (score, sc_aid))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ 成绩录入成功 = {score}")
                return True
            else:
                print("❌ 成绩录入失败：未找到对应的选课记录")
                return False
        except Error as e:
            print(f"❌ 成绩录入失败：{e}")
            return False

    def get_student_total_credits(self, student_aid):
        query = """
        SELECT SUM(c.Credit) AS total_credits
        FROM student_course sc
        JOIN course c ON sc.CourseAID = c.AID
        WHERE sc.StudentAID = %s AND sc.Score IS NOT NULL
        """
        self.cursor.execute(query, (student_aid,))
        result = self.cursor.fetchone()
        total = result['total_credits'] if result['total_credits'] else 0
        print(f"📊 学生总学分：{total}")
        return total

    def get_student_average_score(self, student_aid):
        query = """
        SELECT AVG(Score) AS avg_score, COUNT(*) AS course_count
        FROM student_course
        WHERE StudentAID = %s AND Score IS NOT NULL
        """
        self.cursor.execute(query, (student_aid,))
        result = self.cursor.fetchone()
        if result['course_count'] > 0:
            avg = round(result['avg_score'], 2)
            print(f"📊 平均成绩：{avg}（共 {result['course_count']} 门课程）")
            return avg
        else:
            print("📊 暂无已录入成绩的课程")
            return None

    def get_course_max_score(self, course_aid):
        query = """
        SELECT sc.Score, s.Code, s.Name
        FROM student_course sc
        JOIN student s ON sc.StudentAID = s.AID
        WHERE sc.CourseAID = %s AND sc.Score IS NOT NULL
        ORDER BY sc.Score DESC
        LIMIT 1
        """
        self.cursor.execute(query, (course_aid,))
        result = self.cursor.fetchone()
        if result:
            print(f"🏆 最高分：{result['Name']}({result['Code']}) - {result['Score']}分")
        else:
            print("📊 该课程暂无成绩记录")
        return result

    def get_course_min_score(self, course_aid):
        query = """
        SELECT sc.Score, s.Code, s.Name
        FROM student_course sc
        JOIN student s ON sc.StudentAID = s.AID
        WHERE sc.CourseAID = %s AND sc.Score IS NOT NULL
        ORDER BY sc.Score ASC
        LIMIT 1
        """
        self.cursor.execute(query, (course_aid,))
        result = self.cursor.fetchone()
        if result:
            print(f"📉 最低分：{result['Name']}({result['Code']}) - {result['Score']}分")
        else:
            print("📊 该课程暂无成绩记录")
        return result

    # ==================== 视图管理 ====================
    # 视图是“保存好的 SELECT”，不额外保存业务数据。
    # 这里用于演示如何简化多表 JOIN 查询。

    def create_view_student_scores(self):
        """创建学生成绩明细视图。

        把 student、student_major1、major、course、student_course 关联起来，
        适合讲解外模式：应用可直接查询视图而不是每次手写 JOIN。
        """
        query = """
        CREATE OR REPLACE VIEW v_student_scores AS
        SELECT s.Code AS StudentCode, s.Name AS StudentName,
               m.Code AS MajorCode, m.Name AS MajorName,
               c.Code AS CourseCode, c.Name AS CourseName, c.Credit,
               sc.AcademicYear, sc.Semester, sc.Score, sc.HasPassed
        FROM student_course sc
        JOIN student s ON sc.StudentAID = s.AID
        LEFT JOIN student_major1 sm1 ON s.AID = sm1.StudentAID
        LEFT JOIN major m ON sm1.MajorAID = m.AID
        JOIN course c ON sc.CourseAID = c.AID
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 视图 v_student_scores 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建视图失败：{e}")
            return False

    def create_view_course_stats(self):
        """创建课程成绩统计视图，演示 GROUP BY 聚合。"""
        query = """
        CREATE OR REPLACE VIEW v_course_stats AS
        SELECT c.Code, c.Name, c.Credit,
               COUNT(sc.StudentAID) AS student_count,
               AVG(sc.Score) AS avg_score,
               MAX(sc.Score) AS max_score,
               MIN(sc.Score) AS min_score
        FROM course c
        LEFT JOIN student_course sc ON c.AID = sc.CourseAID AND sc.Score IS NOT NULL
        GROUP BY c.AID, c.Code, c.Name, c.Credit
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 视图 v_course_stats 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建视图失败：{e}")
            return False

    def create_view_student_credits(self):
        """创建学生学分统计视图，演示 LEFT JOIN + 聚合。"""
        query = """
        CREATE OR REPLACE VIEW v_student_credits AS
        SELECT s.Code, s.Name,
               IFNULL(SUM(c.Credit), 0) AS total_credits,
               AVG(sc.Score) AS avg_score
        FROM student s
        LEFT JOIN student_course sc ON s.AID = sc.StudentAID AND sc.Score IS NOT NULL
        LEFT JOIN course c ON sc.CourseAID = c.AID
        GROUP BY s.AID, s.Code, s.Name
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 视图 v_student_credits 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建视图失败：{e}")
            return False

    def list_views(self):
        query = """
        SELECT TABLE_NAME AS view_name
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = DATABASE()
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def drop_view(self, view_name):
        if not self._is_safe_identifier(view_name):
            print("❌ 无效视图名")
            return False
        try:
            self.cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
            self.connection.commit()
            print(f"✅ 视图 {view_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除视图失败：{e}")
            return False

    def query_view(self, view_name):
        if not self._is_safe_identifier(view_name):
            print("❌ 无效视图名")
            return []
        try:
            self.cursor.execute(f"SELECT * FROM {view_name}")
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询视图失败：{e}")
            return []

    # ==================== 触发器管理 ====================
    # 触发器用于演示数据库端业务规则。
    # 注意：这里只创建触发器，不创建任何额外基础表。

    def create_trigger_score_check(self):
        """创建成绩范围检查触发器。

        DB05 的 Score 字段允许 NULL；非 NULL 时应在 0~100 之间。
        触发器分别覆盖 INSERT 和 UPDATE 两种写入场景。
        """
        self.cursor.execute("DROP TRIGGER IF EXISTS trg_before_sc_score_check")
        query = """
        CREATE TRIGGER trg_before_sc_score_check
        BEFORE INSERT ON student_course
        FOR EACH ROW
        BEGIN
            IF NEW.Score IS NOT NULL AND (NEW.Score < 0 OR NEW.Score > 100) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = '成绩必须在 0~100 之间';
            END IF;
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 触发器 trg_before_sc_score_check 创建成功")
        except Error as e:
            print(f"❌ 创建触发器失败：{e}")
            return False

        self.cursor.execute("DROP TRIGGER IF EXISTS trg_before_sc_score_update_check")
        query2 = """
        CREATE TRIGGER trg_before_sc_score_update_check
        BEFORE UPDATE ON student_course
        FOR EACH ROW
        BEGIN
            IF NEW.Score IS NOT NULL AND (NEW.Score < 0 OR NEW.Score > 100) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = '成绩必须在 0~100 之间';
            END IF;
        END
        """
        try:
            self.cursor.execute(query2)
            self.connection.commit()
            print("✅ 触发器 trg_before_sc_score_update_check 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建触发器失败：{e}")
            return False

    def list_triggers(self):
        query = """
        SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_TIMING
        FROM INFORMATION_SCHEMA.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE()
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def drop_trigger(self, trigger_name):
        if not self._is_safe_identifier(trigger_name):
            print("❌ 无效触发器名")
            return False
        try:
            self.cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
            self.connection.commit()
            print(f"✅ 触发器 {trigger_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除触发器失败：{e}")
            return False

    # ==================== 存储过程管理 ====================
    # 存储过程用于演示把一段数据处理逻辑保存在数据库端。

    def create_proc_student_rank(self):
        """创建学生排名过程，演示窗口函数 RANK()。"""
        self.cursor.execute("DROP PROCEDURE IF EXISTS sp_student_rank")
        query = """
        CREATE PROCEDURE sp_student_rank(IN p_student_aid INT, OUT p_rank INT)
        BEGIN
            SELECT student_rank INTO p_rank
            FROM (
                SELECT StudentAID,
                       RANK() OVER (ORDER BY AVG(Score) DESC) AS student_rank
                FROM student_course
                WHERE Score IS NOT NULL
                GROUP BY StudentAID
            ) ranked
            WHERE StudentAID = p_student_aid;
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 存储过程 sp_student_rank 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建存储过程失败：{e}")
            return False

    def create_proc_course_pass_rate(self):
        """创建课程及格率过程，演示 OUT 参数和流程控制。"""
        self.cursor.execute("DROP PROCEDURE IF EXISTS sp_course_pass_rate")
        query = """
        CREATE PROCEDURE sp_course_pass_rate(IN p_course_aid INT, OUT p_pass_rate DECIMAL(5,2))
        BEGIN
            DECLARE total_count INT DEFAULT 0;
            DECLARE pass_count INT DEFAULT 0;

            SELECT COUNT(*) INTO total_count
            FROM student_course
            WHERE CourseAID = p_course_aid AND Score IS NOT NULL;

            SELECT COUNT(*) INTO pass_count
            FROM student_course
            WHERE CourseAID = p_course_aid AND Score >= 60;

            IF total_count > 0 THEN
                SET p_pass_rate = (pass_count / total_count) * 100;
            ELSE
                SET p_pass_rate = 0;
            END IF;
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 存储过程 sp_course_pass_rate 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建存储过程失败：{e}")
            return False

    def create_proc_score_bonus(self):
        """创建课程成绩加分过程，演示批量 UPDATE。"""
        self.cursor.execute("DROP PROCEDURE IF EXISTS sp_score_bonus")
        query = """
        CREATE PROCEDURE sp_score_bonus(IN p_course_aid INT, IN p_bonus DECIMAL(5,2))
        BEGIN
            UPDATE student_course
            SET Score = LEAST(Score + p_bonus, 100)
            WHERE CourseAID = p_course_aid AND Score IS NOT NULL;
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 存储过程 sp_score_bonus 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建存储过程失败：{e}")
            return False

    def call_proc_student_rank(self, student_aid):
        try:
            self.cursor.execute("SET @rank = 0")
            self.cursor.execute("CALL sp_student_rank(%s, @rank)", (student_aid,))
            self.cursor.execute("SELECT @rank AS `rank`")
            row = self.cursor.fetchone()
            rank = row['rank'] if row else None
            if rank:
                print(f"🏅 平均成绩排名：第 {int(rank)} 名")
            else:
                print("📊 暂无成绩，无法计算排名")
            return rank
        except Error as e:
            print(f"❌ 调用存储过程失败：{e}")
            return None

    def call_proc_course_pass_rate(self, course_aid):
        try:
            self.cursor.execute("SET @pass_rate = 0.0")
            self.cursor.execute("CALL sp_course_pass_rate(%s, @pass_rate)", (course_aid,))
            self.cursor.execute("SELECT @pass_rate AS pass_rate")
            row = self.cursor.fetchone()
            pass_rate = row['pass_rate'] if row else None
            if pass_rate is not None:
                print(f"📈 课程及格率：{round(float(pass_rate), 2)}%")
            return pass_rate
        except Error as e:
            print(f"❌ 调用存储过程失败：{e}")
            return None

    def call_proc_score_bonus(self, course_aid, bonus):
        try:
            self.cursor.execute("CALL sp_score_bonus(%s, %s)", (course_aid, bonus))
            self.connection.commit()
            print(f"✅ 成绩加分完成：加 {bonus} 分（上限 100）")
            return True
        except Error as e:
            print(f"❌ 调用存储过程失败：{e}")
            return None

    def list_procedures(self):
        query = """
        SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE'
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def drop_procedure(self, proc_name):
        if not self._is_safe_identifier(proc_name):
            print("❌ 无效存储过程名")
            return False
        try:
            self.cursor.execute(f"DROP PROCEDURE IF EXISTS {proc_name}")
            self.connection.commit()
            print(f"✅ 存储过程 {proc_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除存储过程失败：{e}")
            return False

    # ==================== 函数管理 ====================
    # 函数用于演示可复用的表达式逻辑，例如成绩等级和 GPA。

    def create_func_grade_level(self):
        """创建成绩等级函数。"""
        self.cursor.execute("DROP FUNCTION IF EXISTS fn_grade_level")
        query = """
        CREATE FUNCTION fn_grade_level(score DECIMAL(4,1))
        RETURNS VARCHAR(10)
        DETERMINISTIC
        BEGIN
            IF score IS NULL THEN RETURN '未录入';
            ELSEIF score >= 90 THEN RETURN '优';
            ELSEIF score >= 80 THEN RETURN '良';
            ELSEIF score >= 70 THEN RETURN '中';
            ELSEIF score >= 60 THEN RETURN '及格';
            ELSE RETURN '不及格';
            END IF;
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 函数 fn_grade_level 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建函数失败：{e}")
            return False

    def create_func_gpa(self):
        """创建 GPA 转换函数。"""
        self.cursor.execute("DROP FUNCTION IF EXISTS fn_gpa")
        query = """
        CREATE FUNCTION fn_gpa(score DECIMAL(4,1))
        RETURNS DECIMAL(2,1)
        DETERMINISTIC
        BEGIN
            IF score IS NULL THEN RETURN NULL;
            ELSEIF score >= 90 THEN RETURN 4.0;
            ELSEIF score >= 85 THEN RETURN 3.7;
            ELSEIF score >= 82 THEN RETURN 3.3;
            ELSEIF score >= 78 THEN RETURN 3.0;
            ELSEIF score >= 75 THEN RETURN 2.7;
            ELSEIF score >= 72 THEN RETURN 2.3;
            ELSEIF score >= 68 THEN RETURN 2.0;
            ELSEIF score >= 64 THEN RETURN 1.5;
            ELSEIF score >= 60 THEN RETURN 1.0;
            ELSE RETURN 0.0;
            END IF;
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 函数 fn_gpa 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建函数失败：{e}")
            return False

    def call_func_grade_level(self, score):
        self.cursor.execute("SELECT fn_grade_level(%s) AS grade_level", (score,))
        result = self.cursor.fetchone()
        level = result['grade_level']
        print(f"📝 成绩 {score} → 等级：{level}")
        return level

    def call_func_gpa(self, score):
        self.cursor.execute("SELECT fn_gpa(%s) AS gpa", (score,))
        result = self.cursor.fetchone()
        gpa = result['gpa']
        print(f"📝 成绩 {score} → GPA：{gpa}")
        return gpa

    def demo_func_in_query(self):
        query = """
        SELECT s.Code, s.Name, c.Name AS CourseName, sc.Score,
               fn_grade_level(sc.Score) AS grade_level
        FROM student_course sc
        JOIN student s ON sc.StudentAID = s.AID
        JOIN course c ON sc.CourseAID = c.AID
        WHERE sc.Score IS NOT NULL
        ORDER BY s.Code, c.Code
        LIMIT 10
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def demo_func_gpa_in_query(self):
        query = """
        SELECT s.Code, s.Name, c.Name AS CourseName, sc.Score,
               fn_gpa(sc.Score) AS gpa
        FROM student_course sc
        JOIN student s ON sc.StudentAID = s.AID
        JOIN course c ON sc.CourseAID = c.AID
        WHERE sc.Score IS NOT NULL
        ORDER BY s.Code, c.Code
        LIMIT 10
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def list_functions(self):
        query = """
        SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'FUNCTION'
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def drop_function(self, func_name):
        if not self._is_safe_identifier(func_name):
            print("❌ 无效函数名")
            return False
        try:
            self.cursor.execute(f"DROP FUNCTION IF EXISTS {func_name}")
            self.connection.commit()
            print(f"✅ 函数 {func_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除函数失败：{e}")
            return False

    # ==================== 完整性约束管理 ====================
    # 这些方法用于课堂演示查看/添加/删除约束。
    # 由于表名、约束名无法用普通参数占位，必须先校验标识符安全性。

    def show_table_constraints(self, table_name):
        query = """
        SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        ORDER BY CONSTRAINT_TYPE, CONSTRAINT_NAME
        """
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchall()

    def add_check_constraint(self, constraint_name, table_name, condition):
        if not self._is_safe_identifier(constraint_name) or not self._is_safe_identifier(table_name):
            print("❌ 无效约束名或表名")
            return False
        query = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} CHECK ({condition})"
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"✅ CHECK 约束 {constraint_name} 添加成功")
            return True
        except Error as e:
            print(f"❌ 添加约束失败：{e}")
            return False

    def drop_constraint(self, table_name, constraint_name):
        if not self._is_safe_identifier(table_name) or not self._is_safe_identifier(constraint_name):
            print("❌ 无效表名或约束名")
            return False
        try:
            self.cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}")
            self.connection.commit()
            print(f"✅ 约束 {constraint_name} 删除成功")
            return True
        except Error as e:
            try:
                self.cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}")
                self.connection.commit()
                print(f"✅ 外键约束 {constraint_name} 删除成功")
                return True
            except Error:
                pass
            print(f"❌ 删除约束失败：{e}")
            return False

    def add_demo_phone_constraint(self):
        return self.add_check_constraint(
            'chk_phone_format', 'student_phone',
            "PhoneNumber REGEXP '^[0-9]{11}$'"
        )

    @staticmethod
    def _is_safe_identifier(name):
        """校验 SQL 标识符。

        表名、视图名、过程名等位置不能用 %s 参数化，只能拼接字符串。
        为避免危险输入，这里只允许字母、数字和下划线组成的简单名称。
        """
        return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name or ""))

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 数据库连接已关闭")
