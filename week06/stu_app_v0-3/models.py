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


class Course:
    """课程信息类"""
    def __init__(self, course_id, course_name, teacher_name, credit):
        self.course_id = course_id      # 课程号
        self.course_name = course_name  # 课程名
        self.teacher_name = teacher_name  # 任课教师
        self.credit = credit            # 学分

    def __str__(self):
        return f"课程号：{self.course_id} | 课程名：{self.course_name} | 教师：{self.teacher_name} | 学分：{self.credit}"


class SC:
    """选课记录类（关联学生和课程）"""
    def __init__(self, student_id, course_id, semester, score=None):
        self.student_id = student_id    # 学号
        self.course_id = course_id      # 课程号（外键）
        self.semester = semester        # 学期
        self.score = score              # 成绩（可选）

    def __str__(self):
        score_str = str(self.score) if self.score is not None else "未录入"
        return f"学号：{self.student_id} | 课程号：{self.course_id} | 学期：{self.semester} | 成绩：{score_str}"
