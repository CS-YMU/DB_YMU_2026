"""DB05 数据模型类。

这些类不是数据库表本身，而是应用层用来临时承载用户输入的数据对象。
例如添加学生时，CLI 先把输入封装成 Student，再交给 database.py
生成 INSERT SQL。这样学生可以清楚区分：

1. models.py：Python 对象模型。
2. database.py：SQL 和数据库表操作。
3. main.py：用户交互流程。
"""


class Major:
    """专业，对应数据库表 major。

    major 表中真正的主键是 AID，自增生成；这里保存的是用户可见的业务字段。
    """
    def __init__(self, code, name, years=4.0):
        self.code = code
        self.name = name
        self.years = years

    def __str__(self):
        return f"专业代码：{self.code} | 名称：{self.name} | 学制：{self.years}年"


class Student:
    """学生，对应数据库表 student。

    注意：主修专业、辅修专业、电话不直接放在 student 表中，而是分别
    存在 student_major1、student_major2、student_phone 表中。这正是
    数据库设计里“关系”和“多值属性拆分”的体现。
    """
    def __init__(self, code, name, sex_aid, birthday, year_inroll,
                 address_cv_aid=None, address_detail=None):
        self.code = code
        self.name = name
        self.sex_aid = sex_aid
        self.birthday = birthday
        self.year_inroll = year_inroll
        self.address_cv_aid = address_cv_aid
        self.address_detail = address_detail

    def __str__(self):
        return (f"学号：{self.code} | 姓名：{self.name} | "
                f"入学年份：{self.year_inroll}")


class Course:
    """课程，对应数据库表 course。"""
    def __init__(self, code, name, hours, credit):
        self.code = code
        self.name = name
        self.hours = hours
        self.credit = credit

    def __str__(self):
        return (f"课程代码：{self.code} | 名称：{self.name} | "
                f"学时：{self.hours} | 学分：{self.credit}")


class Teacher:
    """教师，对应数据库表 teacher。

    职称不是直接存文字，而是通过 TitleAID 引用 dd_professional_title。
    """
    def __init__(self, code, name, title_aid):
        self.code = code
        self.name = name
        self.title_aid = title_aid

    def __str__(self):
        return f"工号：{self.code} | 姓名：{self.name}"


class StudentCourse:
    """选课记录，对应数据库表 student_course。

    这是学生和课程的 m:n 关系表，并带有关系属性：
    选课日期、学年、学期、成绩、主修/辅修。
    HasPassed 是数据库虚拟列，不需要 Python 手工赋值。
    """
    def __init__(self, student_aid, course_aid, for_major=True,
                 regist_date=None, academic_year=None, semester=0, score=None):
        self.student_aid = student_aid
        self.course_aid = course_aid
        self.for_major = for_major
        self.regist_date = regist_date
        self.academic_year = academic_year
        self.semester = semester
        self.score = score

    def __str__(self):
        score_str = str(self.score) if self.score is not None else "未录入"
        return (f"学生AID：{self.student_aid} | 课程AID：{self.course_aid} | "
                f"成绩：{score_str}")


class StudentPhone:
    """学生电话，对应数据库表 student_phone。

    电话是多值属性，一个学生可以有多个电话，因此单独建表。
    """
    def __init__(self, student_aid, phone_number, flag_type='2', is_commonly_used=True):
        self.student_aid = student_aid
        self.phone_number = phone_number
        self.flag_type = flag_type
        self.is_commonly_used = is_commonly_used


class MajorCourse:
    """专业开设课程，对应补充表 major_course。

    原始业务描述要求“一门课程可以为多个专业开设，一个专业可以开设多门课”。
    DB05 示例 SQL 的 16 张表未包含该关系，因此完整业务版补充此关系表。
    """
    def __init__(self, major_aid, course_aid):
        self.major_aid = major_aid
        self.course_aid = course_aid


class TeacherGuidance:
    """教师指导学生，对应补充表 teacher_guidance。

    原始业务描述要求：教师可指导 0~n 个学生；学生被 1 个教师指导，
    并记录指导起止日期。StudentAID 作为主键，保证一个学生最多一条指导关系。
    """
    def __init__(self, student_aid, teacher_aid, start_date, end_date=None):
        self.student_aid = student_aid
        self.teacher_aid = teacher_aid
        self.start_date = start_date
        self.end_date = end_date
