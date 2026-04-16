"""初始化测试数据"""
from models import Student, Course, SC
from database import Database

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'student_db',
    'user': 'dylan',
    'password': 'P@ssw0rd'
}


def init_data():
    """初始化测试数据"""
    db = Database(**DB_CONFIG)

    if not db.connect():
        print("数据库连接失败")
        return

    # 先删除旧表（如果存在），重新创建
    print("\n--- 重建数据表 ---")
    try:
        db.cursor.execute("DROP TABLE IF EXISTS sc")
        db.cursor.execute("DROP TABLE IF EXISTS course")
        db.cursor.execute("DROP TABLE IF EXISTS students")
        db.connection.commit()
        print("✅ 旧表已删除")
    except Exception as e:
        print(f"⚠️ 删除旧表时出现警告：{e}")

    # 创建表
    db.create_tables()

    # ==================== 添加学生 ====================
    students = [
        Student('2024001', '张三', '男', 20, '计算机科学与技术', '13800138001'),
        Student('2024002', '李四', '女', 19, '软件工程', '13800138002'),
        Student('2024003', '王五', '男', 21, '信息安全', '13800138003'),
        Student('2024004', '赵六', '女', 20, '计算机科学与技术', '13800138004'),
    ]

    print("\n--- 添加学生 ---")
    for s in students:
        db.add_student(s)

    # ==================== 添加课程 ====================
    courses = [
        Course('CS101', '数据结构', '李老师', 3.0),
        Course('CS102', '操作系统', '王老师', 3.0),
        Course('CS103', '计算机网络', '张老师', 2.5),
        Course('CS104', '数据库原理', '刘老师', 3.0),
        Course('MATH101', '高等数学', '陈老师', 4.0),
        Course('EN101', '大学英语', '周老师', 2.0),
    ]

    print("\n--- 添加课程 ---")
    for c in courses:
        db.add_course(c)

    # ==================== 添加选课记录 ====================
    selections = [
        SC('2024001', 'CS101', '2024-1'),
        SC('2024001', 'CS102', '2024-1'),
        SC('2024001', 'MATH101', '2024-1'),
        SC('2024002', 'CS101', '2024-1'),
        SC('2024002', 'CS104', '2024-1'),
        SC('2024002', 'EN101', '2024-1'),
        SC('2024003', 'CS102', '2024-1'),
        SC('2024003', 'CS103', '2024-1'),
        SC('2024004', 'CS101', '2024-1'),
        SC('2024004', 'CS104', '2024-1'),
        SC('2024004', 'MATH101', '2024-1'),
        # 第二学期选课
        SC('2024001', 'CS103', '2024-2'),
        SC('2024001', 'CS104', '2024-2'),
        SC('2024002', 'CS102', '2024-2'),
        SC('2024002', 'MATH101', '2024-2'),
    ]

    print("\n--- 添加选课记录 ---")
    for sc in selections:
        db.add_course_selection(sc)

    # ==================== 录入成绩 ====================
    print("\n--- 录入成绩 ---")
    score_updates = [
        ('2024001', 'CS101', '2024-1', 85),
        ('2024001', 'CS102', '2024-1', 90),
        ('2024001', 'MATH101', '2024-1', 78),
        ('2024002', 'CS101', '2024-1', 92),
        ('2024002', 'CS104', '2024-1', 88),
        ('2024002', 'EN101', '2024-1', 85),
        ('2024003', 'CS102', '2024-1', 76),
        ('2024003', 'CS103', '2024-1', 80),
        ('2024004', 'CS101', '2024-1', 91),
        ('2024004', 'CS104', '2024-1', 87),
        ('2024004', 'MATH101', '2024-1', 82),
        # 第二学期成绩
        ('2024001', 'CS103', '2024-2', 83),
        ('2024001', 'CS104', '2024-2', 89),
        ('2024002', 'CS102', '2024-2', 90),
        ('2024002', 'MATH101', '2024-2', 75),
    ]

    for student_id, course_id, semester, score in score_updates:
        db.update_score(student_id, course_id, semester, score)

    # ==================== 显示统计 ====================
    print("\n" + "=" * 50)
    print("           📊 初始化数据统计")
    print("=" * 50)

    print(f"\n📚 学生总数：{len(students)}")
    print(f"📖 课程总数：{len(courses)}")
    print(f"📝 选课记录总数：{len(selections)}")

    print("\n--- 各学生学分和平均成绩 ---")
    for s in students:
        db.get_student_total_credits(s.student_id)
        db.get_student_average_score(s.student_id)

    print("\n--- 各课程最高分和最低分 ---")
    for c in courses:
        db.get_course_max_score(c.course_id)
        db.get_course_min_score(c.course_id)

    print("\n✅ 测试数据初始化完成！")
    db.close()


if __name__ == "__main__":
    init_data()
