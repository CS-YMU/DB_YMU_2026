import mysql.connector
from mysql.connector import Error


class Database:
    """数据库操作类"""

    def __init__(self, host, database, user, password):
        self.connection_config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

        # 创建课程表
        create_course_query = """
        CREATE TABLE IF NOT EXISTS course (
            course_id VARCHAR(20) PRIMARY KEY,
            course_name VARCHAR(100) NOT NULL,
            teacher_name VARCHAR(50) NOT NULL,
            credit DECIMAL(3,1) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        try:
            self.cursor.execute(create_students_query)
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
        INSERT INTO course (course_id, course_name, teacher_name, credit)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                course.course_id, course.course_name,
                course.teacher_name, course.credit
            ))
            self.connection.commit()
            print(f"✅ 课程 {course.course_name} 添加成功")
            return True
        except Error as e:
            print(f"❌ 添加失败：{e}")
            return False

    def get_all_courses(self):
        """获取所有课程"""
        query = "SELECT * FROM course ORDER BY course_id"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 查询失败：{e}")
            return []

    def search_course(self, keyword):
        """搜索课程（支持课程号、课程名模糊查询）"""
        query = """
        SELECT * FROM course
        WHERE course_id LIKE %s OR course_name LIKE %s
        ORDER BY course_id
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
        query = "SELECT * FROM course WHERE course_id = %s"
        try:
            self.cursor.execute(query, (course_id,))
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

    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 数据库连接已关闭")
