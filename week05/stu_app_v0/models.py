class Student:
    """学生信息类"""
    def __init__(self, student_id, name, gender, age, major, phone):
        self.student_id = student_id  # 学号
        self.name = name              # 姓名
        self.gender = gender          # 性别
        self.age = age                # 年龄
        self.major = major            # 专业
        self.phone = phone            # 电话
    
    def __str__(self):
        return f"学号：{self.student_id} | 姓名：{self.name} | 性别：{self.gender} | 年龄：{self.age} | 专业：{self.major} | 电话：{self.phone}"