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
    def __init__(self, course_id, course_name, teacher_id, credit):
        self.course_id = course_id      # 课程号
        self.course_name = course_name  # 课程名
        self.teacher_id = teacher_id    # 授课教师编号
        self.credit = credit            # 学分

    def __str__(self):
        return f"课程号：{self.course_id} | 课程名：{self.course_name} | 教师编号：{self.teacher_id} | 学分：{self.credit}"


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


class Teacher:
    """教师信息类"""
    def __init__(self, teacher_id, name, gender, age, title, phone):
        self.teacher_id = teacher_id    # 教师编号
        self.name = name                # 姓名
        self.gender = gender            # 性别
        self.age = age                  # 年龄
        self.title = title              # 职称（教授/副教授/讲师/助教）
        self.phone = phone              # 电话

    def __str__(self):
        return f"教师编号：{self.teacher_id} | 姓名：{self.name} | 性别：{self.gender} | 年龄：{self.age} | 职称：{self.title} | 电话：{self.phone}"


class CoursePrerequisite:
    """课程先修关系类"""
    def __init__(self, course_id, prerequisite_id):
        self.course_id = course_id          # 课程号
        self.prerequisite_id = prerequisite_id  # 先修课程号

    def __str__(self):
        return f"课程：{self.course_id} | 先修课程：{self.prerequisite_id}"
