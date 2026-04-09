import mysql.connector
from mysql.connector import Error

class Database:
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
        """创建学生信息表"""
        create_table_query = """
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
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("✅ 数据表创建成功")
        except Error as e:
            print(f"❌ 创建表失败：{e}")
    
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
                update_data['age'], update_data['major'], 
                update_data['phone'], student_id
            ))
            self.connection.commit()
            print(f"✅ 学生信息更新成功")
            return True
        except Error as e:
            print(f"❌ 更新失败：{e}")
            return False
    
    def delete_student(self, student_id):
        """删除学生"""
        query = "DELETE FROM students WHERE student_id = %s"
        try:
            self.cursor.execute(query, (student_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f"✅ 学生删除成功")
                return True
            else:
                print(f"❌ 学号 {student_id} 不存在")
                return False
        except Error as e:
            print(f"❌ 删除失败：{e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 数据库连接已关闭")