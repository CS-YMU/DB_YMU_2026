import mysql.connector
from mysql.connector import Error


class Database:
    """数据库操作类"""

    def __init__(self, host, database, user, password):
        self.connection_config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.connection_config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ 数据库连接成功")
            return True
        except Error as e:
            print(f"❌ 数据库连接失败：{e}")
            return False

    def create_tables(self):
        """创建数据表（学生表、课程表、选课表）"""
        # 创建学生表
        create_students_query = """
        CREATE TABLE IF NOT EXISTS students (
            student_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender ENUM('男', '女', '其他') NOT NULL,
            age INT CHECK (age > 0 AND age < 150),
            major VARCHAR(100),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 创建课程表
        create_course_query = """
        CREATE TABLE IF NOT EXISTS course (
            course_id VARCHAR(20) PRIMARY KEY,
            course_name VARCHAR(100) NOT NULL,
            teacher_id VARCHAR(20) NOT NULL,
            credit DECIMAL(3,1) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_course_teacher FOREIGN KEY (teacher_id)
                REFERENCES teacher(teacher_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 创建选课表（关联 students 和 course）
        # - 外键 student_id -> students(student_id)，级联删除
        # - 外键 course_id -> course(course_id)，级联删除
        # - 唯一约束 (student_id, course_id, semester) 防止重复选课
        create_sc_query = """
        CREATE TABLE IF NOT EXISTS sc (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20) NOT NULL,
            course_id VARCHAR(20) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            score DECIMAL(5,2) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_sc_student FOREIGN KEY (student_id)
                REFERENCES students(student_id) ON DELETE CASCADE,
            CONSTRAINT fk_sc_course FOREIGN KEY (course_id)
                REFERENCES course(course_id) ON DELETE RESTRICT,
            CONSTRAINT uk_student_course_semester UNIQUE (student_id, course_id, semester)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 创建教师表
        create_teacher_query = """
        CREATE TABLE IF NOT EXISTS teacher (
            teacher_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender ENUM('男', '女', '其他') NOT NULL,
            age INT CHECK (age > 0 AND age < 150),
            title VARCHAR(20) NOT NULL COMMENT '职称：教授/副教授/讲师/助教',
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        try:
            self.cursor.execute(create_students_query)
            self.cursor.execute(create_teacher_query)
            self.cursor.execute(create_course_query)
            self.cursor.execute(create_sc_query)
            self.connection.commit()
            print("✅ 数据表创建成功")
        except Error as e:
            print(f"❌ 创建表失败：{e}")

    # ==================== 学生相关操作 ====================

    def add_student(self, student):
        """添加学生"""
        query = """
        INSERT INTO students (student_id, name, gender, age, major, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                student.student_id, student.name, student.gender,
                student.age, student.major, student.phone
            ))
            self.connection.commit()
            print(f"✅ 学生 {student.name} 添加成功")
            return True
        except Error as e:
            print(f"❌ 添加失败：{e}")
            return False

    def get_all_students(self):
        """获取所有学生"""
        query = "SELECT * FROM students ORDER BY student_id"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return []

    def search_student(self, keyword):
        """搜索学生（支持学号、姓名模糊查询）"""
        query = """
        SELECT * FROM students
        WHERE student_id LIKE %s OR name LIKE %s
        ORDER BY student_id
        """
        pattern = f"%{keyword}%"
        try:
            self.cursor.execute(query, (pattern, pattern))
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 搜索失败：{e}")
            return []

    def update_student(self, student_id, update_data):
        """更新学生信息"""
        query = """
        UPDATE students
        SET name=%s, gender=%s, age=%s, major=%s, phone=%s
        WHERE student_id=%s
        """
        try:
            self.cursor.execute(query, (
                update_data['name'], update_data['gender'],
                int(update_data['age']), update_data['major'],
                update_data['phone'], student_id
            ))
            self.connection.commit()
            print(f"✅ 学生信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新失败：{e}")
            return False

    def delete_student(self, student_id):
        """删除学生（选课记录会因外键级联自动删除）"""
        query = "DELETE FROM students WHERE student_id = %s"
        try:
            self.cursor.execute(query, (student_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ 学生删除成功（已同步删除关联选课记录）")
                return True
            else:
                print(f"❌ 学号 {student_id} 不存在")
                return False
        except Error as e:
            print(f"❌ 删除失败：{e}")
            return False

    def student_exists(self, student_id):
        """检查学生是否存在"""
        query = "SELECT 1 FROM students WHERE student_id = %s"
        try:
            self.cursor.execute(query, (student_id,))
            return self.cursor.fetchone() is not None
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return False

    # ==================== 课程相关操作 ====================

    def add_course(self, course):
        """添加课程"""
        query = """
        INSERT INTO course (course_id, course_name, teacher_id, credit)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                course.course_id, course.course_name,
                course.teacher_id, course.credit
            ))
            self.connection.commit()
            print(f"✅ 课程 {course.course_name} 添加成功")
            return True
        except Error as e:
            print(f"❌ 添加失败：{e}")
            return False

    def get_all_courses(self):
        """获取所有课程（关联教师信息）"""
        query = """
        SELECT c.*, t.name as teacher_name, t.title as teacher_title
        FROM course c
        LEFT JOIN teacher t ON c.teacher_id = t.teacher_id
        ORDER BY c.course_id
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return []

    def search_course(self, keyword):
        """搜索课程（支持课程号、课程名模糊查询）"""
        query = """
        SELECT c.*, t.name as teacher_name, t.title as teacher_title
        FROM course c
        LEFT JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id LIKE %s OR c.course_name LIKE %s
        ORDER BY c.course_id
        """
        pattern = f"%{keyword}%"
        try:
            self.cursor.execute(query, (pattern, pattern))
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 搜索失败：{e}")
            return []

    def update_course(self, course_id, update_data):
        """更新课程信息"""
        query = """
        UPDATE course
        SET course_name=%s, teacher_name=%s, credit=%s
        WHERE course_id=%s
        """
        try:
            self.cursor.execute(query, (
                update_data['course_name'], update_data['teacher_name'],
                update_data['credit'], course_id
            ))
            self.connection.commit()
            print(f"✅ 课程信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新失败：{e}")
            return False

    def delete_course(self, course_id):
        """删除课程"""
        # 注意：如果有学生已选修该课程，外键级联会拒绝删除
        query = "DELETE FROM course WHERE course_id = %s"
        try:
            self.cursor.execute(query, (course_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ 课程删除成功")
                return True
            else:
                print(f"❌ 课程号 {course_id} 不存在")
                return False
        except Error as e:
            if "foreign key constraint" in str(e).lower():
                print(f"❌ 删除失败：该课程已有学生选修，无法删除")
            else:
                print(f"❌ 删除失败：{e}")
            return False

    def course_exists(self, course_id):
        """检查课程是否存在"""
        query = "SELECT 1 FROM course WHERE course_id = %s"
        try:
            self.cursor.execute(query, (course_id,))
            return self.cursor.fetchone() is not None
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return False

    def get_course_by_id(self, course_id):
        """根据课程号获取课程信息"""
        query = """
        SELECT c.*, t.name as teacher_name, t.title as teacher_title
        FROM course c
        LEFT JOIN teacher t ON c.teacher_id = t.teacher_id
        WHERE c.course_id = %s
        """
        try:
            self.cursor.execute(query, (course_id,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return None

    # ==================== 选课相关操作 ====================

    # ==================== 教师相关操作 ====================

    def add_teacher(self, teacher):
        """添加教师"""
        query = """
        INSERT INTO teacher (teacher_id, name, gender, age, title, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                teacher.teacher_id, teacher.name, teacher.gender,
                teacher.age, teacher.title, teacher.phone
            ))
            self.connection.commit()
            print(f"✅ 教师 {teacher.name} 添加成功")
            return True
        except Error as e:
            print(f"❌ 添加失败：{e}")
            return False

    def get_all_teachers(self):
        """获取所有教师"""
        query = "SELECT * FROM teacher ORDER BY teacher_id"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return []

    def search_teacher(self, keyword):
        """搜索教师（支持教师号、姓名模糊查询）"""
        query = """
        SELECT * FROM teacher
        WHERE teacher_id LIKE %s OR name LIKE %s
        ORDER BY teacher_id
        """
        pattern = f"%{keyword}%"
        try:
            self.cursor.execute(query, (pattern, pattern))
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 搜索失败：{e}")
            return []

    def update_teacher(self, teacher_id, update_data):
        """更新教师信息"""
        query = """
        UPDATE teacher
        SET name=%s, gender=%s, age=%s, title=%s, phone=%s
        WHERE teacher_id=%s
        """
        try:
            self.cursor.execute(query, (
                update_data['name'], update_data['gender'],
                int(update_data['age']), update_data['title'],
                update_data['phone'], teacher_id
            ))
            self.connection.commit()
            print(f"✅ 教师信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新失败：{e}")
            return False

    def delete_teacher(self, teacher_id):
        """删除教师"""
        query = "DELETE FROM teacher WHERE teacher_id = %s"
        try:
            self.cursor.execute(query, (teacher_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ 教师删除成功")
                return True
            else:
                print(f"❌ 教师编号 {teacher_id} 不存在")
                return False
        except Error as e:
            print(f"❌ 删除失败：{e}")
            return False

    def teacher_exists(self, teacher_id):
        """检查教师是否存在"""
        query = "SELECT 1 FROM teacher WHERE teacher_id = %s"
        try:
            self.cursor.execute(query, (teacher_id,))
            return self.cursor.fetchone() is not None
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return False

    def get_teacher_by_id(self, teacher_id):
        """根据教师号获取教师信息"""
        query = "SELECT * FROM teacher WHERE teacher_id = %s"
        try:
            self.cursor.execute(query, (teacher_id,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return None

    # ==================== 选课相关操作 ====================

    def add_course_selection(self, sc_record):
        """添加选课记录"""
        query = """
        INSERT INTO sc (student_id, course_id, semester)
        VALUES (%s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                sc_record.student_id, sc_record.course_id, sc_record.semester
            ))
            self.connection.commit()
            print(f"✅ 选课成功：{sc_record.student_id} - {sc_record.course_id}")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                print(f"❌ 选课失败：该学生已在同一学期选修过此课程")
            else:
                print(f"❌ 选课失败：{e}")
            return False

    def get_student_courses(self, student_id):
        """获取某个学生的所有选课记录（关联课程信息）"""
        query = """
        SELECT sc.*, c.course_name, c.teacher_name, c.credit
        FROM sc
        LEFT JOIN course c ON sc.course_id = c.course_id
        WHERE sc.student_id = %s
        ORDER BY sc.semester, sc.course_id
        """
        try:
            self.cursor.execute(query, (student_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return []

    def get_all_course_selections(self):
        """获取所有选课记录（关联学生和课程信息）"""
        query = """
        SELECT sc.*, s.name as student_name, c.course_name, c.teacher_name, c.credit
        FROM sc
        LEFT JOIN students s ON sc.student_id = s.student_id
        LEFT JOIN course c ON sc.course_id = c.course_id
        ORDER BY sc.student_id, sc.semester, sc.course_id
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return []

    def drop_course_selection(self, student_id, course_id, semester):
        """退课（删除指定学生的指定课程）"""
        query = """
        DELETE FROM sc
        WHERE student_id = %s AND course_id = %s AND semester = %s
        """
        try:
            self.cursor.execute(query, (student_id, course_id, semester))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ 退课成功")
                return True
            else:
                print(f"❌ 退课失败：未找到对应的选课记录")
                return False
        except Error as e:
            print(f"❌ 退课失败：{e}")
            return False

    def update_score(self, student_id, course_id, semester, score):
        """录入或修改成绩"""
        query = """
        UPDATE sc
        SET score = %s
        WHERE student_id = %s AND course_id = %s AND semester = %s
        """
        try:
            self.cursor.execute(query, (score, student_id, course_id, semester))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ 成绩录入/修改成功：{student_id} - {course_id} - {semester} = {score}")
                return True
            else:
                print(f"❌ 成绩录入失败：未找到对应的选课记录")
                return False
        except Error as e:
            print(f"❌ 成绩录入失败：{e}")
            return False

    def get_student_total_credits(self, student_id):
        """获取某个学生的总学分（只统计已录入成绩的课程）"""
        query = """
        SELECT SUM(c.credit) as total_credits
        FROM sc
        LEFT JOIN course c ON sc.course_id = c.course_id
        WHERE sc.student_id = %s AND sc.score IS NOT NULL
        """
        try:
            self.cursor.execute(query, (student_id,))
            result = self.cursor.fetchone()
            total = result['total_credits'] if result['total_credits'] else 0
            print(f"📊 学生 {student_id} 的总学分：{total}")
            return total
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return 0

    def get_student_average_score(self, student_id):
        """获取某个学生的平均成绩（只统计非空成绩）"""
        query = """
        SELECT AVG(score) as avg_score, COUNT(*) as course_count
        FROM sc
        WHERE student_id = %s AND score IS NOT NULL
        """
        try:
            self.cursor.execute(query, (student_id,))
            result = self.cursor.fetchone()
            if result['course_count'] > 0:
                avg = round(result['avg_score'], 2)
                print(f"📊 学生 {student_id} 的平均成绩：{avg}（共 {result['course_count']} 门课程）")
                return avg
            else:
                print(f"📊 学生 {student_id} 暂无已录入成绩的课程")
                return None
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return None

    def get_course_max_score(self, course_id):
        """获取某课程的最高分学生信息"""
        query = """
        SELECT sc.score, s.student_id, s.name, s.gender, s.major, sc.semester
        FROM sc
        LEFT JOIN students s ON sc.student_id = s.student_id
        WHERE sc.course_id = %s AND sc.score IS NOT NULL
        ORDER BY sc.score DESC
        LIMIT 1
        """
        try:
            self.cursor.execute(query, (course_id,))
            result = self.cursor.fetchone()
            if result:
                print(f"🏆 课程 {course_id} 最高分：{result['name']}({result['student_id']}) - {result['score']}分（{result['semester']}）")
                return result
            else:
                print(f"📊 课程 {course_id} 暂无成绩记录")
                return None
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return None

    def get_course_min_score(self, course_id):
        """获取某课程的最低分学生信息"""
        query = """
        SELECT sc.score, s.student_id, s.name, s.gender, s.major, sc.semester
        FROM sc
        LEFT JOIN students s ON sc.student_id = s.student_id
        WHERE sc.course_id = %s AND sc.score IS NOT NULL
        ORDER BY sc.score ASC
        LIMIT 1
        """
        try:
            self.cursor.execute(query, (course_id,))
            result = self.cursor.fetchone()
            if result:
                print(f"📉 课程 {course_id} 最低分：{result['name']}({result['student_id']}) - {result['score']}分（{result['semester']}）")
                return result
            else:
                print(f"📊 课程 {course_id} 暂无成绩记录")
                return None
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return None

    # ==================== 视图（View）管理 ====================
    # 视图是虚拟表，基于SQL查询结果，可用于简化复杂查询、数据安全隔离等教学演示

    def create_view_student_scores(self):
        """创建视图：学生成绩明细视图（演示多表关联查询的封装）"""
        query = """
        CREATE OR REPLACE VIEW v_student_scores AS
        SELECT
            s.student_id,
            s.name AS student_name,
            s.major,
            c.course_id,
            c.course_name,
            c.credit,
            sc.semester,
            sc.score
        FROM sc
        JOIN students s ON sc.student_id = s.student_id
        JOIN course c ON sc.course_id = c.course_id;
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
        """创建视图：课程统计视图（演示聚合查询的封装）"""
        query = """
        CREATE OR REPLACE VIEW v_course_stats AS
        SELECT
            c.course_id,
            c.course_name,
            c.teacher_name,
            COUNT(sc.student_id) AS student_count,
            AVG(sc.score) AS avg_score,
            MAX(sc.score) AS max_score,
            MIN(sc.score) AS min_score
        FROM course c
        LEFT JOIN sc ON c.course_id = sc.course_id AND sc.score IS NOT NULL
        GROUP BY c.course_id, c.course_name, c.teacher_name;
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 视图 v_course_stats 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建视图失败：{e}")
            return False

    def list_views(self):
        """列出当前数据库中所有的视图"""
        query = """
        SELECT TABLE_NAME AS view_name
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = DATABASE();
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询视图列表失败：{e}")
            return []

    def drop_view(self, view_name):
        """删除指定的视图"""
        query = f"DROP VIEW IF EXISTS {view_name}"
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"✅ 视图 {view_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除视图失败：{e}")
            return False

    def query_view(self, view_name):
        """查询视图内容（与查询表语法相同，体现视图的虚拟表特性）"""
        query = f"SELECT * FROM {view_name}"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询视图失败：{e}")
            return []

    # ==================== 课后作业 1：视图扩展 ====================
    # TODO：请补全下面的方法，创建一个名为 v_student_credits 的视图。
    # 该视图应展示每位学生的学号、姓名、总学分（SUM）和平均成绩（AVG）。
    # 提示：
    #   1. 需要关联 students、sc、course 三张表
    #   2. 只统计已录入成绩（score IS NOT NULL）的记录
    #   3. 使用 LEFT JOIN 保证没有选课的学生也能显示（总学分为 0）
    def create_view_student_credits(self):
        """【课后作业】创建视图：学生学分与平均成绩统计"""
        query = """
        CREATE OR REPLACE VIEW v_student_credits AS
        SELECT
            s.student_id,
            s.name,
            IFNULL(SUM(c.credit), 0) AS total_credits,
            AVG(sc.score) AS avg_score
        FROM students s
        LEFT JOIN sc ON s.student_id = sc.student_id AND sc.score IS NOT NULL
        LEFT JOIN course c ON sc.course_id = c.course_id
        GROUP BY s.student_id, s.name;
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 视图 v_student_credits 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建视图失败：{e}")
            return False

    # ==================== 触发器（Trigger）管理 ====================
    # 触发器是自动执行的存储程序，可在INSERT/UPDATE/DELETE前后触发，用于自动化业务规则

    def create_trigger_score_check(self):
        """
        创建触发器：在插入或更新成绩前，检查成绩范围是否在 0~100 之间。
        用于演示 BEFORE 触发器和完整性约束的互补关系。
        """
        # 先删除旧触发器，避免重复创建报错
        self.cursor.execute("DROP TRIGGER IF EXISTS trg_before_sc_score_check")
        query = """
        CREATE TRIGGER trg_before_sc_score_check
        BEFORE INSERT ON sc
        FOR EACH ROW
        BEGIN
            IF NEW.score IS NOT NULL AND (NEW.score < 0 OR NEW.score > 100) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = '成绩必须在 0~100 之间';
            END IF;
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 触发器 trg_before_sc_score_check（INSERT）创建成功")
        except Error as e:
            print(f"❌ 创建触发器失败：{e}")
            return False

        # 同时为 UPDATE 也创建相同的检查触发器
        self.cursor.execute("DROP TRIGGER IF EXISTS trg_before_sc_score_update_check")
        query2 = """
        CREATE TRIGGER trg_before_sc_score_update_check
        BEFORE UPDATE ON sc
        FOR EACH ROW
        BEGIN
            IF NEW.score IS NOT NULL AND (NEW.score < 0 OR NEW.score > 100) THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = '成绩必须在 0~100 之间';
            END IF;
        END
        """
        try:
            self.cursor.execute(query2)
            self.connection.commit()
            print("✅ 触发器 trg_before_sc_score_update_check（UPDATE）创建成功")
            return True
        except Error as e:
            print(f"❌ 创建触发器失败：{e}")
            return False

    def create_trigger_student_delete_log(self):
        """
        创建触发器：删除学生记录后，自动将删除信息写入日志表。
        用于演示 AFTER 触发器和审计日志的简单实现。
        """
        # 先创建日志表（如果不存在）
        create_log_table = """
        CREATE TABLE IF NOT EXISTS student_delete_log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20) NOT NULL,
            name VARCHAR(50),
            major VARCHAR(100),
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        try:
            self.cursor.execute(create_log_table)
        except Error as e:
            print(f"❌ 创建日志表失败：{e}")
            return False

        self.cursor.execute("DROP TRIGGER IF EXISTS trg_after_student_delete_log")
        query = """
        CREATE TRIGGER trg_after_student_delete_log
        AFTER DELETE ON students
        FOR EACH ROW
        BEGIN
            INSERT INTO student_delete_log (student_id, name, major)
            VALUES (OLD.student_id, OLD.name, OLD.major);
        END
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 触发器 trg_after_student_delete_log 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建触发器失败：{e}")
            return False

    def list_triggers(self):
        """列出当前数据库中所有的触发器"""
        query = """
        SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_TIMING
        FROM INFORMATION_SCHEMA.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE();
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询触发器列表失败：{e}")
            return []

    def drop_trigger(self, trigger_name):
        """删除指定的触发器"""
        query = f"DROP TRIGGER IF EXISTS {trigger_name}"
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"✅ 触发器 {trigger_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除触发器失败：{e}")
            return False

    def get_delete_logs(self):
        """查询学生删除日志表内容（配合触发器演示使用）"""
        query = "SELECT * FROM student_delete_log ORDER BY deleted_at DESC"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询删除日志失败：{e}")
            return []

    # ==================== 课后作业 2：触发器扩展 ====================
    # TODO：请补全下面的方法，创建一个 AFTER UPDATE 触发器。
    # 当 students 表的 major 字段被修改时，自动将旧专业和新专业记录到 major_change_log 表中。
    # 提示：
    #   1. 需要先创建日志表 major_change_log（包含 student_id, old_major, new_major, changed_at）
    #   2. 触发器体中使用 OLD.major 和 NEW.major
    #   3. 使用 DROP TRIGGER IF EXISTS 避免重复创建报错
    def create_trigger_major_change_log(self):
        """【课后作业】创建触发器：记录学生专业变更日志"""
        # TODO：先创建 major_change_log 表（如果不存在）
        create_log_table = """
        -- TODO：请填写 CREATE TABLE IF NOT EXISTS major_change_log ...
        """
        try:
            self.cursor.execute(create_log_table)
        except Error as e:
            print(f"❌ 创建日志表失败：{e}")
            return False

        self.cursor.execute("DROP TRIGGER IF EXISTS trg_after_student_major_change_log")
        query = """
        -- TODO：请填写 CREATE TRIGGER trg_after_student_major_change_log ...
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 触发器 trg_after_student_major_change_log 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建触发器失败：{e}")
            return False

    def get_major_change_logs(self):
        """【课后作业】查询专业变更日志表内容"""
        query = "SELECT * FROM major_change_log ORDER BY changed_at DESC"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询专业变更日志失败：{e}")
            return []

    # ==================== 存储过程（Stored Procedure）管理 ====================
    # 存储过程是预编译的SQL语句集合，可接受参数、执行复杂逻辑，用于演示服务端编程

    def create_proc_student_rank(self):
        """
        创建存储过程：查询某学生在所有学生中的平均成绩排名。
        演示 IN 参数和基于聚合查询的服务端计算。
        """
        self.cursor.execute("DROP PROCEDURE IF EXISTS sp_student_rank")
        query = """
        CREATE PROCEDURE sp_student_rank(IN p_student_id VARCHAR(20), OUT p_rank INT)
        BEGIN
            SELECT student_rank INTO p_rank
            FROM (
                SELECT
                    student_id,
                    RANK() OVER (ORDER BY AVG(score) DESC) AS student_rank
                FROM sc
                WHERE score IS NOT NULL
                GROUP BY student_id
            ) ranked
            WHERE student_id = p_student_id;
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
        """
        创建存储过程：查询某课程的及格率。
        演示基于条件统计的服务端计算。
        """
        self.cursor.execute("DROP PROCEDURE IF EXISTS sp_course_pass_rate")
        query = """
        CREATE PROCEDURE sp_course_pass_rate(IN p_course_id VARCHAR(20), OUT p_pass_rate DECIMAL(5,2))
        BEGIN
            DECLARE total_count INT DEFAULT 0;
            DECLARE pass_count INT DEFAULT 0;

            SELECT COUNT(*) INTO total_count
            FROM sc
            WHERE course_id = p_course_id AND score IS NOT NULL;

            SELECT COUNT(*) INTO pass_count
            FROM sc
            WHERE course_id = p_course_id AND score >= 60;

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

    def call_proc_student_rank(self, student_id):
        """调用存储过程 sp_student_rank，获取学生排名"""
        try:
            # 使用用户变量接收 OUT 参数，兼容性更好，便于课堂讲解
            self.cursor.execute("SET @rank = 0")
            self.cursor.execute("CALL sp_student_rank(%s, @rank)", (student_id,))
            self.cursor.execute("SELECT @rank AS `rank`")
            row = self.cursor.fetchone()
            rank = row['rank'] if row else None
            if rank:
                print(f"🏅 学生 {student_id} 的平均成绩排名：第 {int(rank)} 名")
            else:
                print(f"📊 学生 {student_id} 暂无成绩，无法计算排名")
            return rank
        except Error as e:
            print(f"❌ 调用存储过程失败：{e}")
            return None

    def call_proc_course_pass_rate(self, course_id):
        """调用存储过程 sp_course_pass_rate，获取课程及格率"""
        try:
            self.cursor.execute("SET @pass_rate = 0.0")
            self.cursor.execute("CALL sp_course_pass_rate(%s, @pass_rate)", (course_id,))
            self.cursor.execute("SELECT @pass_rate AS pass_rate")
            row = self.cursor.fetchone()
            pass_rate = row['pass_rate'] if row else None
            if pass_rate is not None:
                print(f"📈 课程 {course_id} 的及格率：{round(float(pass_rate), 2)}%")
            else:
                print(f"📊 课程 {course_id} 暂无成绩记录")
            return pass_rate
        except Error as e:
            print(f"❌ 调用存储过程失败：{e}")
            return None

    # ==================== 课后作业 3：存储过程扩展 ====================
    # TODO：请补全下面的方法，创建一个存储过程 sp_score_bonus。
    # 功能：为指定课程的所有学生成绩统一增加 bonus 分，但上限不超过 100 分。
    # 提示：
    #   1. 使用 IN 参数接收 course_id 和 bonus
    #   2. 在存储过程内部使用 UPDATE ... SET score = LEAST(score + bonus, 100) ...
    def create_proc_score_bonus(self):
        """【课后作业】创建存储过程：课程成绩统一加分"""
        self.cursor.execute("DROP PROCEDURE IF EXISTS sp_score_bonus")
        query = """
        -- TODO：请填写 CREATE PROCEDURE sp_score_bonus(IN p_course_id VARCHAR(20), IN p_bonus DECIMAL(5,2)) ...
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 存储过程 sp_score_bonus 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建存储过程失败：{e}")
            return False

    def call_proc_score_bonus(self, course_id, bonus):
        """【课后作业】调用存储过程 sp_score_bonus"""
        try:
            # TODO：请填写 CALL sp_score_bonus(%s, %s)
            pass
        except Error as e:
            print(f"❌ 调用存储过程失败：{e}")
            return None

    def list_procedures(self):
        """列出当前数据库中所有的存储过程"""
        query = """
        SELECT ROUTINE_NAME
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'PROCEDURE';
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询存储过程列表失败：{e}")
            return []

    def drop_procedure(self, proc_name):
        """删除指定的存储过程"""
        query = f"DROP PROCEDURE IF EXISTS {proc_name}"
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"✅ 存储过程 {proc_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除存储过程失败：{e}")
            return False

    # ==================== 函数（Function）管理 ====================
    # 自定义函数像内置函数一样可在SQL中调用，用于封装可复用的计算逻辑

    def create_func_grade_level(self):
        """
        创建函数：根据成绩返回等级（优/良/中/及格/不及格）。
        用于演示自定义标量函数在查询中的复用。
        """
        self.cursor.execute("DROP FUNCTION IF EXISTS fn_grade_level")
        query = """
        CREATE FUNCTION fn_grade_level(score DECIMAL(5,2))
        RETURNS VARCHAR(10)
        DETERMINISTIC
        BEGIN
            IF score IS NULL THEN
                RETURN '未录入';
            ELSEIF score >= 90 THEN
                RETURN '优';
            ELSEIF score >= 80 THEN
                RETURN '良';
            ELSEIF score >= 70 THEN
                RETURN '中';
            ELSEIF score >= 60 THEN
                RETURN '及格';
            ELSE
                RETURN '不及格';
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

    def call_func_grade_level(self, score):
        """调用函数 fn_grade_level，返回成绩等级（演示直接 SELECT 调用）"""
        query = "SELECT fn_grade_level(%s) AS grade_level"
        try:
            self.cursor.execute(query, (score,))
            result = self.cursor.fetchone()
            level = result['grade_level']
            print(f"📝 成绩 {score} 对应的等级：{level}")
            return level
        except Error as e:
            print(f"❌ 调用函数失败：{e}")
            return None

    def demo_func_in_query(self):
        """在查询中使用自定义函数，展示函数与SQL的结合应用"""
        query = """
        SELECT
            s.student_id,
            s.name,
            c.course_name,
            sc.score,
            fn_grade_level(sc.score) AS grade_level
        FROM sc
        JOIN students s ON sc.student_id = s.student_id
        JOIN course c ON sc.course_id = c.course_id
        WHERE sc.score IS NOT NULL
        ORDER BY s.student_id, c.course_id
        LIMIT 10;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 函数查询演示失败：{e}")
            return []

    # ==================== 课后作业 4：函数扩展 ====================
    # TODO：请补全下面的方法，创建一个函数 fn_gpa(score)。
    # 功能：将百分制成绩转换为 4.0 制 GPA。
    # 转换规则建议：
    #   score >= 90  -> 4.0
    #   score >= 85  -> 3.7
    #   score >= 82  -> 3.3
    #   score >= 78  -> 3.0
    #   score >= 75  -> 2.7
    #   score >= 72  -> 2.3
    #   score >= 68  -> 2.0
    #   score >= 64  -> 1.5
    #   score >= 60  -> 1.0
    #   score < 60   -> 0.0
    #   NULL         -> NULL
    def create_func_gpa(self):
        """【课后作业】创建函数：百分制转 4.0 制 GPA"""
        self.cursor.execute("DROP FUNCTION IF EXISTS fn_gpa")
        query = """
        -- TODO：请填写 CREATE FUNCTION fn_gpa(score DECIMAL(5,2)) ...
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ 函数 fn_gpa 创建成功")
            return True
        except Error as e:
            print(f"❌ 创建函数失败：{e}")
            return False

    def call_func_gpa(self, score):
        """【课后作业】调用函数 fn_gpa"""
        query = "SELECT fn_gpa(%s) AS gpa"
        try:
            self.cursor.execute(query, (score,))
            result = self.cursor.fetchone()
            gpa = result['gpa']
            print(f"📝 成绩 {score} 对应的 GPA：{gpa}")
            return gpa
        except Error as e:
            print(f"❌ 调用函数失败：{e}")
            return None

    def demo_func_gpa_in_query(self):
        """【课后作业】在查询中使用 fn_gpa 函数"""
        query = """
        SELECT
            s.student_id,
            s.name,
            c.course_name,
            sc.score,
            fn_gpa(sc.score) AS gpa
        FROM sc
        JOIN students s ON sc.student_id = s.student_id
        JOIN course c ON sc.course_id = c.course_id
        WHERE sc.score IS NOT NULL
        ORDER BY s.student_id, c.course_id
        LIMIT 10;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ GPA 查询演示失败：{e}")
            return []

    def list_functions(self):
        """列出当前数据库中所有的自定义函数"""
        query = """
        SELECT ROUTINE_NAME
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA = DATABASE() AND ROUTINE_TYPE = 'FUNCTION';
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询函数列表失败：{e}")
            return []

    def drop_function(self, func_name):
        """删除指定的自定义函数"""
        query = f"DROP FUNCTION IF EXISTS {func_name}"
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"✅ 函数 {func_name} 删除成功")
            return True
        except Error as e:
            print(f"❌ 删除函数失败：{e}")
            return False

    # ==================== 完整性约束（Integrity Constraint）管理 ====================
    # 用于课堂演示如何动态添加/删除/查看表的各类约束（CHECK、FOREIGN KEY、UNIQUE 等）

    def show_table_constraints(self, table_name):
        """查看指定表的所有约束信息"""
        query = """
        SELECT
            CONSTRAINT_NAME,
            CONSTRAINT_TYPE
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        ORDER BY CONSTRAINT_TYPE, CONSTRAINT_NAME;
        """
        try:
            self.cursor.execute(query, (table_name,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询约束失败：{e}")
            return []

    def add_check_constraint(self, constraint_name, table_name, condition):
        """
        为指定表动态添加 CHECK 约束。
        例如：add_check_constraint('chk_credit', 'course', 'credit > 0')
        """
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
        """删除指定表的指定约束"""
        query = f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name}"
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"✅ 约束 {constraint_name} 删除成功")
            return True
        except Error as e:
            # MySQL 8.0 之前使用 DROP FOREIGN KEY / DROP INDEX 区分约束类型，
            # 这里做简单兼容：如果 DROP CONSTRAINT 失败，尝试 DROP FOREIGN KEY
            if "foreign key" in str(e).lower() or "check" in str(e).lower():
                try:
                    self.cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}")
                    self.connection.commit()
                    print(f"✅ 外键约束 {constraint_name} 删除成功")
                    return True
                except Error:
                    pass
            print(f"❌ 删除约束失败：{e}")
            return False

    # ==================== 课后作业 5：完整性约束扩展 ====================
    # TODO：请补全下面的方法，为 students 表的 phone 列添加一个 CHECK 约束。
    # 要求：phone 必须是 11 位数字（允许为空）。
    # 提示：
    #   1. 使用 ALTER TABLE ... ADD CONSTRAINT ... CHECK (...)
    #   2. MySQL 8.0.16+ 支持在 CHECK 中使用 REGEXP，条件可写为：
    #      phone IS NULL OR phone REGEXP '^[0-9]{11}$'
    def add_demo_phone_constraint(self):
        """【课后作业】添加手机号格式 CHECK 约束"""
        # TODO：请填写调用 add_check_constraint 的代码，约束名建议为 chk_phone_format
        pass

    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 数据库连接已关闭")
