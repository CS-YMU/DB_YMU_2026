"""数据模型 —— 数据库应用系统中的数据传输对象

定义 Python 类来承载数据库查询结果，便于在 Flask 视图和模板之间传递数据。
这体现了"共享变量"概念的延伸：数据库的字段映射为 Python 对象的属性。

参考：week09/stu_app_v1_04/models.py 的设计模式
"""


class Student:
    """学生实体模型"""

    def __init__(self, row):
        self.id = row['ID']
        self.name = row['Name']
        self.sex = row['Sex']
        self.age = row['Age']
        self.dept = row['Dept']
        self.rid = row.get('RID', '')
        self.total_credit = row.get('TotalCredit', 0)

    @property
    def sex_display(self):
        return '男' if self.sex == '男' else '女'

    @property
    def dept_display(self):
        dept_map = {'CS': '计算机科学系', 'MA': '数学系', 'IS': '信息系统系'}
        return dept_map.get(self.dept, self.dept)


class Course:
    """课程实体模型"""

    def __init__(self, row):
        self.id = row['ID']
        self.name = row['Name']
        self.credit = float(row['Credit']) if row.get('Credit') else 0
        self.pid = row.get('PID')
        self.prerequisite_name = row.get('PrerequisiteName', '')

    @property
    def has_prerequisite(self):
        return self.pid is not None


class StudentCourse:
    """学生选课记录模型"""

    def __init__(self, row):
        self.course_id = row['CourseID']
        self.course_name = row.get('CourseName', '')
        self.credit = float(row.get('Credit', 0))
        self.grade = float(row['Grade']) if row.get('Grade') else None
        self.grade_level = row.get('GradeLevel', '')

    @property
    def is_passed(self):
        return self.grade is not None and self.grade >= 60


class CourseStat:
    """课程统计模型 —— 存储过程 sp_CourseStat 的输出"""

    def __init__(self, row):
        if row:
            self.avg_grade = float(row['avg_grade']) if row['avg_grade'] else 0
            self.max_grade = float(row['max_grade']) if row['max_grade'] else 0
            self.min_grade = float(row['min_grade']) if row['min_grade'] else 0
            self.pass_num = int(row['pass_num']) if row['pass_num'] else 0
            self.total_num = int(row['total_num']) if row['total_num'] else 0
        else:
            self.avg_grade = 0
            self.max_grade = 0
            self.min_grade = 0
            self.pass_num = 0
            self.total_num = 0

    @property
    def pass_rate(self):
        if self.total_num > 0:
            return round(self.pass_num / self.total_num * 100, 1)
        return 0
