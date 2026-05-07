"""DB05 学生选课管理系统 —— 主程序。

本文件负责“用户交互”，即显示菜单、读取输入、调用 database.py。
教学时可以把它理解为数据库应用设计中的“外模式/应用层”：

- 用户看到的是学号、姓名、课程名等业务信息。
- 程序内部再把这些操作转换成对 16 张 DB05 表的增删改查。
- 本文件不直接拼复杂 SQL，复杂 SQL 统一放在 database.py，便于分层讲解。
"""
from models import Major, Student, Course, Teacher, StudentCourse
from database import Database
from config import DB_CONFIG
from datetime import date


class StudentCourseSystem:
    """命令行版学生选课系统。

    一个 StudentCourseSystem 对象持有一个 Database 对象。
    main.py 只处理流程，真正的数据库读写由 self.db 完成。
    """

    def __init__(self, **kwargs):
        config = {**DB_CONFIG, **kwargs}
        self.db = Database(
            config['host'], config['database'],
            config['user'], config['password'])

    def show_menu(self):
        # 菜单按照 DB05 作业中的实体和关系组织：
        # 学生、课程、教师、专业是核心实体；选课、先修、负责人等是关系表。
        print("\n" + "=" * 55)
        print("          🎓 学生选课管理系统 (DB05)")
        print("=" * 55)
        print("  【学生管理】")
        print("  1. 添加学生      2. 查看所有学生   3. 搜索学生")
        print("  4. 修改学生信息  5. 删除学生")
        print()
        print("  【课程管理】")
        print("  6. 添加课程      7. 查看所有课程   8. 搜索课程")
        print("  9. 修改课程信息  10. 删除课程")
        print()
        print("  【教师管理】")
        print("  11. 添加教师     12. 查看所有教师  13. 搜索教师")
        print("  14. 修改教师信息 15. 删除教师")
        print()
        print("  【选课管理】")
        print("  16. 学生选课     17. 查看学生选课  18. 查看所有选课")
        print("  19. 退课         20. 录入/修改成绩")
        print()
        print("  【专业、先修课程 & 统计】")
        print("  21. 专业管理     22. 先修课程管理")
        print("  23. 查询总学分   24. 查询平均成绩")
        print()
        print("  【数据库对象管理】")
        print("  25. 视图管理     26. 触发器管理    27. 存储过程管理")
        print("  28. 函数管理     29. 完整性约束管理")
        print()
        print("  【完整业务补充】")
        print("  30. 专业开课管理 31. 教师指导管理")
        print()
        print("  0. 退出系统")
        print("=" * 55)

    # ==================== 学生管理 ====================
    # student：学生基本信息
    # student_major1：学生主修专业
    # student_major2：学生辅修专业
    # student_phone：学生电话

    def _pick_sex(self):
        """选择性别，返回 dd_sex.AID。

        DB05 设计把性别做成数据字典表，而不是在 student 表里直接存“男/女”。
        """
        options = self.db.get_sex_options()
        print("\n性别选项：")
        for o in options:
            print(f"  {o['AID']}. {o['Name']}")
        while True:
            try:
                choice = int(input("请选择性别编号：").strip())
                if any(o['AID'] == choice for o in options):
                    return choice
            except ValueError:
                pass
            print("❌ 无效选择")

    def _pick_title(self):
        """选择职称，返回 dd_professional_title.AID。"""
        options = self.db.get_title_options()
        print("\n职称选项：")
        for o in options:
            print(f"  {o['AID']}. {o['Name']}（等级{o['Level']}）")
        while True:
            try:
                choice = int(input("请选择职称编号：").strip())
                if any(o['AID'] == choice for o in options):
                    return choice
            except ValueError:
                pass
            print("❌ 无效选择")

    def _pick_major(self, optional=False):
        """选择专业，返回 major.AID（可选时返回 None）。"""
        majors = self.db.get_all_majors()
        if not majors:
            print("❌ 当前没有专业数据")
            return None
        print("\n专业列表：")
        for m in majors:
            print(f"  {m['AID']}. {m['Code']} - {m['Name']}（{m['Years']}年）")
        while True:
            prompt = "请选择专业编号" + ("（0=跳过）：" if optional else "：")
            try:
                choice = int(input(prompt).strip())
                if optional and choice == 0:
                    return None
                if any(m['AID'] == choice for m in majors):
                    return choice
            except ValueError:
                pass
            print("❌ 无效选择")

    def _pick_teacher(self, optional=False):
        """选择教师，返回 teacher.AID（可选时返回 None）。"""
        teachers = self.db.get_all_teachers()
        if not teachers:
            print("❌ 当前没有教师数据")
            return None
        print("\n教师列表：")
        for t in teachers:
            print(f"  {t['AID']}. {t['Code']} - {t['Name']}（{t['TitleName']}）")
        while True:
            prompt = "请选择教师AID" + ("（0=跳过）：" if optional else "：")
            try:
                choice = int(input(prompt).strip())
                if optional and choice == 0:
                    return None
                if any(t['AID'] == choice for t in teachers):
                    return choice
            except ValueError:
                pass
            print("❌ 无效选择")

    def _pick_division(self):
        """选择行政区划，返回 dd_administrative_divisions.AID。"""
        divisions = self.db.get_division_options()
        print("\n行政区划（前20条）：")
        for d in divisions[:20]:
            print(f"  {d['AID']}. {d['FullName']}")
        while True:
            try:
                choice = int(input("请选择地址编号（0=跳过）：").strip())
                if choice == 0:
                    return None
                if any(d['AID'] == choice for d in divisions):
                    return choice
            except ValueError:
                pass
            print("❌ 无效选择")

    def add_student_ui(self):
        print("\n--- 添加新学生 ---")
        code = input("请输入学号：").strip()
        name = input("请输入姓名：").strip()
        sex_aid = self._pick_sex()

        birthday = None
        b_input = input("请输入生日（YYYY-MM-DD，可回车跳过）：").strip()
        if b_input:
            try:
                birthday = date.fromisoformat(b_input)
            except ValueError:
                print("❌ 日期格式无效，设为空")
                birthday = None

        while True:
            try:
                year_inroll = int(input("请输入入学年份：").strip())
                if 2000 <= year_inroll <= 2030:
                    break
                print("❌ 请输入合理的年份（2000-2030）")
            except ValueError:
                print("❌ 请输入有效整数")

        address_cv_aid = self._pick_division()
        address_detail = input("请输入详细地址（可回车跳过）：").strip() or None

        student = Student(code, name, sex_aid, birthday, year_inroll,
                          address_cv_aid, address_detail)
        student_aid = self.db.add_student(student)

        if student_aid:
            # 作业要求：一个学生必须且只能主修一个专业。
            # 这里向 student_major1 插入一条记录。
            major_aid = self._pick_major()
            if major_aid:
                self.db.set_student_major1(student_aid, major_aid)

            # 作业要求：一个学生最多辅修一个专业。
            # 这里向 student_major2 插入零或一条记录。
            if input("是否设置辅修专业？(y/n)：").strip().lower() == 'y':
                major2_aid = self._pick_major(optional=True)
                if major2_aid:
                    self.db.set_student_major2(student_aid, major2_aid)

            # 电话是多值属性，拆到 student_phone 表。
            phone = input("请输入电话号码（可回车跳过）：").strip()
            if phone:
                self.db.add_student_phone(student_aid, phone, '2', True)

    def view_all_students(self):
        print("\n--- 所有学生信息 ---")
        students = self.db.get_all_students()
        if students:
            print(f"\n{'AID':<6} {'学号':<14} {'姓名':<8} {'性别':<4} "
                  f"{'生日':<12} {'入学':<6} {'专业':<16} {'地址':<20}")
            print("-" * 95)
            for s in students[:50]:
                bd = str(s['Birthday']) if s['Birthday'] else ''
                print(f"{s['AID']:<6} {s['Code']:<14} {s['Name']:<8} "
                      f"{s['SexName']:<4} {bd:<12} {s['YearInroll']:<6} "
                      f"{s['MajorName'] or '':<16} {s['AddressFullName'] or '':<20}")
            if len(students) > 50:
                print(f"\n... 共 {len(students)} 条记录（仅显示前50条）")
            else:
                print(f"\n共 {len(students)} 条记录")
        else:
            print("暂无学生信息")

    def search_student_ui(self):
        print("\n--- 搜索学生 ---")
        keyword = input("请输入学号或姓名关键词：").strip()
        results = self.db.search_student(keyword)
        if results:
            print(f"\n找到 {len(results)} 条记录：")
            print(f"{'AID':<6} {'学号':<14} {'姓名':<8} {'性别':<4} {'生日':<12} {'入学':<6} {'专业':<16}")
            print("-" * 70)
            for s in results[:20]:
                bd = str(s['Birthday']) if s['Birthday'] else ''
                print(f"{s['AID']:<6} {s['Code']:<14} {s['Name']:<8} "
                      f"{s['SexName']:<4} {bd:<12} {s['YearInroll']:<6} "
                      f"{s['MajorName'] or '':<16}")
            if len(results) > 20:
                print(f"... 共 {len(results)} 条")
        else:
            print("未找到匹配的学生")

    def update_student_ui(self):
        print("\n--- 修改学生信息 ---")
        code = input("请输入要修改的学生学号：").strip()
        student = self.db.get_student_by_code(code)
        if not student:
            print(f"❌ 学号 {code} 不存在")
            return

        print(f"当前信息：{student['Name']}，入学{student['YearInroll']}")
        print("请输入新信息（直接回车保持原值）：")

        update_data = {}
        name = input("姓名：").strip()
        if name:
            update_data['Name'] = name

        if input("修改性别？(y/n)：").strip().lower() == 'y':
            update_data['SexAID'] = self._pick_sex()

        b_input = input("生日（YYYY-MM-DD）：").strip()
        if b_input:
            try:
                date.fromisoformat(b_input)
                update_data['Birthday'] = b_input
            except ValueError:
                print("❌ 日期格式无效，跳过")

        yr = input("入学年份：").strip()
        if yr:
            try:
                update_data['YearInroll'] = int(yr)
            except ValueError:
                print("❌ 无效年份，跳过")

        detail = input("详细地址：").strip()
        if detail:
            update_data['AddressDetail'] = detail

        if update_data:
            self.db.update_student(student['AID'], update_data)

        # 修改主修专业
        if input("修改主修专业？(y/n)：").strip().lower() == 'y':
            major_aid = self._pick_major()
            if major_aid:
                self.db.set_student_major1(student['AID'], major_aid)

    def delete_student_ui(self):
        print("\n--- 删除学生 ---")
        code = input("请输入要删除的学生学号：").strip()
        student = self.db.get_student_by_code(code)
        if not student:
            print(f"❌ 学号 {code} 不存在")
            return

        confirm = input(f"⚠️ 确认删除 {student['Name']}（{code}）？\n"
                        f"输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_student(student['AID'])
        else:
            print("已取消删除")

    # ==================== 课程管理 ====================
    # course：课程实体
    # teacher_course：课程由哪位教师讲授
    # course_leader：课程负责人

    def add_course_ui(self):
        print("\n--- 添加新课程 ---")
        code = input("请输入课程代码：").strip()
        name = input("请输入课程名：").strip()

        while True:
            try:
                hours = int(input("请输入学时：").strip())
                if hours > 0:
                    break
                print("❌ 学时需大于0")
            except ValueError:
                print("❌ 请输入有效整数")

        while True:
            try:
                credit = float(input("请输入学分：").strip())
                if credit > 0:
                    break
                print("❌ 学分需大于0")
            except ValueError:
                print("❌ 请输入有效数字")

        course = Course(code, name, hours, credit)
        course_aid = self.db.add_course(course)

        if course_aid:
            # DB05 要求：每门课程由一名教师讲授；课程负责人单独存 course_leader。
            teachers = self.db.get_all_teachers()
            if teachers:
                print("\n可选教师：")
                for t in teachers:
                    print(f"  {t['AID']}. {t['Code']} {t['Name']}（{t['TitleName']}）")
                try:
                    t_aid = int(input("请选择授课教师AID（0=跳过）：").strip())
                    if t_aid > 0:
                        self.db.set_course_teacher(course_aid, t_aid)
                        # 同时设为课程负责人
                        if input("是否同时设为课程负责人？(y/n)：").strip().lower() == 'y':
                            self.db.set_course_leader(course_aid, t_aid)
                except ValueError:
                    pass

    def view_all_courses(self):
        print("\n--- 所有课程信息 ---")
        courses = self.db.get_all_courses()
        if courses:
            print(f"\n{'AID':<6} {'代码':<10} {'课程名':<18} {'学时':<6} "
                  f"{'学分':<6} {'授课教师':<10} {'负责人':<10}")
            print("-" * 75)
            for c in courses:
                print(f"{c['AID']:<6} {c['Code']:<10} {c['Name']:<18} "
                      f"{c['Hours']:<6} {c['Credit']:<6} "
                      f"{c['TeacherName'] or '':<10} {c['LeaderName'] or '':<10}")
            print(f"\n共 {len(courses)} 门课程")
        else:
            print("暂无课程信息")

    def search_course_ui(self):
        print("\n--- 搜索课程 ---")
        keyword = input("请输入课程代码或名称关键词：").strip()
        results = self.db.search_course(keyword)
        if results:
            print(f"\n找到 {len(results)} 条：")
            print(f"{'AID':<6} {'代码':<10} {'课程名':<18} {'学时':<6} {'学分':<6} {'教师':<10}")
            print("-" * 60)
            for c in results:
                print(f"{c['AID']:<6} {c['Code']:<10} {c['Name']:<18} "
                      f"{c['Hours']:<6} {c['Credit']:<6} {c['TeacherName'] or '':<10}")
        else:
            print("未找到匹配的课程")

    def update_course_ui(self):
        print("\n--- 修改课程信息 ---")
        code = input("请输入要修改的课程代码：").strip()
        course = self.db.get_course_by_code(code)
        if not course:
            print(f"❌ 课程代码 {code} 不存在")
            return

        print(f"当前：{course['Name']}，学时{course['Hours']}，学分{course['Credit']}")
        print("请输入新信息（直接回车保持原值）：")

        update_data = {}
        name = input("课程名：").strip()
        if name:
            update_data['Name'] = name

        h = input("学时：").strip()
        if h:
            try:
                update_data['Hours'] = int(h)
            except ValueError:
                print("❌ 无效，跳过")

        c = input("学分：").strip()
        if c:
            try:
                update_data['Credit'] = float(c)
            except ValueError:
                print("❌ 无效，跳过")

        if update_data:
            self.db.update_course(course['AID'], update_data)

        if input("修改授课教师？(y/n)：").strip().lower() == 'y':
            teachers = self.db.get_all_teachers()
            for t in teachers:
                print(f"  {t['AID']}. {t['Code']} {t['Name']}")
            try:
                t_aid = int(input("请选择教师AID：").strip())
                self.db.set_course_teacher(course['AID'], t_aid)
            except ValueError:
                print("❌ 无效，跳过")

    def delete_course_ui(self):
        print("\n--- 删除课程 ---")
        code = input("请输入要删除的课程代码：").strip()
        course = self.db.get_course_by_code(code)
        if not course:
            print(f"❌ 课程 {code} 不存在")
            return

        confirm = input(f"⚠️ 确认删除 {course['Name']}（{code}）？\n"
                        f"输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_course(course['AID'])
        else:
            print("已取消删除")

    # ==================== 教师管理 ====================
    # teacher：教师实体
    # teacher_major：教师所属专业

    def add_teacher_ui(self):
        print("\n--- 添加新教师 ---")
        code = input("请输入工号：").strip()
        name = input("请输入姓名：").strip()
        title_aid = self._pick_title()

        teacher = Teacher(code, name, title_aid)
        teacher_aid = self.db.add_teacher(teacher)

        if teacher_aid:
            if input("是否设置所属专业？(y/n)：").strip().lower() == 'y':
                major_aid = self._pick_major()
                if major_aid:
                    self.db.set_teacher_major(teacher_aid, major_aid)

    def view_all_teachers(self):
        print("\n--- 所有教师信息 ---")
        teachers = self.db.get_all_teachers()
        if teachers:
            print(f"\n{'AID':<6} {'工号':<12} {'姓名':<8} {'职称':<10} {'职称等级':<8} {'专业':<16}")
            print("-" * 65)
            for t in teachers:
                print(f"{t['AID']:<6} {t['Code']:<12} {t['Name']:<8} "
                      f"{t['TitleName']:<10} {t['TitleLevel']:<8} "
                      f"{t['MajorName'] or '':<16}")
            print(f"\n共 {len(teachers)} 位教师")
        else:
            print("暂无教师信息")

    def search_teacher_ui(self):
        print("\n--- 搜索教师 ---")
        keyword = input("请输入工号或姓名关键词：").strip()
        results = self.db.search_teacher(keyword)
        if results:
            print(f"\n找到 {len(results)} 条：")
            print(f"{'AID':<6} {'工号':<12} {'姓名':<8} {'职称':<10} {'专业':<16}")
            print("-" * 55)
            for t in results:
                print(f"{t['AID']:<6} {t['Code']:<12} {t['Name']:<8} "
                      f"{t['TitleName']:<10} {t['MajorName'] or '':<16}")
        else:
            print("未找到匹配的教师")

    def update_teacher_ui(self):
        print("\n--- 修改教师信息 ---")
        code = input("请输入要修改的教师工号：").strip()
        teacher = self.db.get_teacher_by_code(code)
        if not teacher:
            print(f"❌ 工号 {code} 不存在")
            return

        print(f"当前：{teacher['Name']}，{teacher['TitleName']}")
        print("请输入新信息（直接回车保持原值）：")

        update_data = {}
        name = input("姓名：").strip()
        if name:
            update_data['Name'] = name

        if input("修改职称？(y/n)：").strip().lower() == 'y':
            update_data['TitleAID'] = self._pick_title()

        if update_data:
            self.db.update_teacher(teacher['AID'], update_data)

    def delete_teacher_ui(self):
        print("\n--- 删除教师 ---")
        code = input("请输入要删除的教师工号：").strip()
        teacher = self.db.get_teacher_by_code(code)
        if not teacher:
            print(f"❌ 工号 {code} 不存在")
            return

        confirm = input(f"⚠️ 确认删除 {teacher['Name']}（{code}）？\n"
                        f"输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_teacher(teacher['AID'])
        else:
            print("已取消删除")

    # ==================== 选课管理 ====================
    # student_course 是学生和课程之间的 m:n 关系表。
    # 该关系本身有属性：RegistDate、AcademicYear、Semester、Score、ForMajor。

    def add_course_selection_ui(self):
        print("\n--- 学生选课 ---")
        student_code = input("请输入学号：").strip()
        student = self.db.get_student_by_code(student_code)
        if not student:
            print(f"❌ 学号 {student_code} 不存在")
            return

        courses = self.db.get_all_courses()
        if not courses:
            print("❌ 暂无课程可选")
            return

        print("\n可选课程：")
        print(f"{'AID':<6} {'代码':<10} {'课程名':<18} {'教师':<10} {'学分':<6}")
        print("-" * 55)
        for c in courses:
            print(f"{c['AID']:<6} {c['Code']:<10} {c['Name']:<18} "
                  f"{c['TeacherName'] or '':<10} {c['Credit']:<6}")

        try:
            course_aid = int(input("\n请输入课程AID：").strip())
        except ValueError:
            print("❌ 无效输入")
            return

        # ForMajor 对应 student_course.ForMajor，按 SQL 注释：1=主修，0=辅修。
        for_major = input("主修课程？(y/n，默认y)：").strip().lower() != 'n'

        try:
            academic_year = int(input("学年（如2024）：").strip())
        except ValueError:
            academic_year = date.today().year

        semester = input("学期（0=上学期/1=下学期，默认0）：").strip()
        semester = 1 if semester == '1' else 0

        sc = StudentCourse(student['AID'], course_aid, for_major,
                           date.today(), academic_year, semester)
        self.db.add_course_selection(sc)

    def view_student_courses_ui(self):
        print("\n--- 查看学生选课情况 ---")
        code = input("请输入学号：").strip()
        student = self.db.get_student_by_code(code)
        if not student:
            print(f"❌ 学号 {code} 不存在")
            return

        courses = self.db.get_student_courses(student['AID'])
        if courses:
            print(f"\n{student['Name']}（{code}）的选课记录：")
            print(f"{'AID':<6} {'课程代码':<10} {'课程名':<15} {'教师':<8} "
                  f"{'学分':<6} {'学年':<6} {'学期':<6} {'成绩':<8} {'是否通过':<8}")
            print("-" * 80)
            for c in courses:
                score_str = str(c['Score']) if c['Score'] is not None else "未录入"
                sem = "下" if c['Semester'] == 1 else "上"
                passed = "是" if c['HasPassed'] == 1 else ("否" if c['Score'] is not None else "-")
                print(f"{c['AID']:<6} {c['CourseCode']:<10} {c['CourseName']:<15} "
                      f"{c['TeacherName'] or '':<8} {c['Credit']:<6} "
                      f"{c['AcademicYear']:<6} {sem:<6} {score_str:<8} {passed:<8}")
            print(f"\n共 {len(courses)} 条选课记录")
        else:
            print(f"学号 {code} 暂无选课记录")

    def view_all_course_selections_ui(self):
        print("\n--- 所有选课记录 ---")
        records = self.db.get_all_course_selections()
        if records:
            print(f"\n{'AID':<6} {'学号':<14} {'姓名':<8} {'课程代码':<10} "
                  f"{'课程名':<15} {'学分':<6} {'学年':<6} {'学期':<4} {'成绩':<8}")
            print("-" * 85)
            for r in records[:50]:
                score_str = str(r['Score']) if r['Score'] is not None else "-"
                sem = "下" if r['Semester'] == 1 else "上"
                print(f"{r['AID']:<6} {r['StudentCode']:<14} {r['StudentName']:<8} "
                      f"{r['CourseCode']:<10} {r['CourseName']:<15} "
                      f"{r['Credit']:<6} {r['AcademicYear']:<6} {sem:<4} {score_str:<8}")
            if len(records) > 50:
                print(f"\n... 共 {len(records)} 条（仅显示前50条）")
            else:
                print(f"\n共 {len(records)} 条选课记录")
        else:
            print("暂无选课记录")

    def drop_course_ui(self):
        print("\n--- 退课 ---")
        try:
            sc_aid = int(input("请输入选课记录AID：").strip())
        except ValueError:
            print("❌ 无效输入")
            return

        confirm = input(f"⚠️ 确认退课（AID={sc_aid}）？输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.drop_course_selection(sc_aid)
        else:
            print("已取消退课")

    def update_score_ui(self):
        print("\n--- 录入/修改成绩 ---")
        try:
            sc_aid = int(input("请输入选课记录AID：").strip())
        except ValueError:
            print("❌ 无效输入")
            return

        while True:
            score_input = input("请输入成绩（0-100，直接回车留空）：").strip()
            if score_input == '':
                print("✅ 成绩已设为空")
                return
            try:
                score = float(score_input)
                if 0 <= score <= 100:
                    break
                print("❌ 成绩需在 0-100 之间")
            except ValueError:
                print("❌ 请输入有效数字")

        # 只更新 Score；HasPassed 是数据库虚拟列，会自动根据 Score >= 60 计算。
        self.db.update_score(sc_aid, score)

    # ==================== 成绩统计 ====================
    # 这里演示如何通过 JOIN 和聚合函数从 student_course + course 中得到统计结果。

    def query_total_credits_ui(self):
        print("\n--- 查询学生总学分 ---")
        code = input("请输入学号：").strip()
        student = self.db.get_student_by_code(code)
        if not student:
            print(f"❌ 学号 {code} 不存在")
            return
        self.db.get_student_total_credits(student['AID'])

    def query_average_score_ui(self):
        print("\n--- 查询学生平均成绩 ---")
        code = input("请输入学号：").strip()
        student = self.db.get_student_by_code(code)
        if not student:
            print(f"❌ 学号 {code} 不存在")
            return
        self.db.get_student_average_score(student['AID'])

    # ==================== 专业管理 ====================
    # major：专业实体
    # major_leader：专业负责人关系

    def major_management_menu(self):
        while True:
            print("\n--- 专业管理 ---")
            print("  1. 添加专业       2. 查看所有专业")
            print("  3. 搜索专业       4. 修改专业")
            print("  5. 删除专业       6. 设置专业负责人")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                code = input("请输入专业代码（6位）：").strip()
                name = input("请输入专业名称：").strip()
                try:
                    years = float(input("请输入学制（默认4.0）：").strip() or "4.0")
                except ValueError:
                    print("❌ 学制无效")
                    continue
                self.db.add_major(Major(code, name, years))
            elif choice == '2':
                majors = self.db.get_all_majors_detail()
                if majors:
                    print(f"\n{'AID':<6} {'代码':<8} {'名称':<20} {'学制':<6} {'负责人':<10}")
                    print("-" * 60)
                    for m in majors:
                        print(f"{m['AID']:<6} {m['Code']:<8} {m['Name']:<20} "
                              f"{m['Years']:<6} {m['LeaderName'] or '':<10}")
                    print(f"\n共 {len(majors)} 个专业")
                else:
                    print("暂无专业")
            elif choice == '3':
                keyword = input("请输入专业代码或名称关键词：").strip()
                majors = self.db.search_major(keyword)
                if majors:
                    for m in majors:
                        print(f"  {m['AID']}. {m['Code']} {m['Name']} "
                              f"学制{m['Years']} 负责人：{m['LeaderName'] or '-'}")
                else:
                    print("未找到匹配的专业")
            elif choice == '4':
                code = input("请输入要修改的专业代码：").strip()
                major = self.db.get_major_by_code(code)
                if not major:
                    print(f"❌ 专业代码 {code} 不存在")
                    continue
                update_data = {}
                name = input("专业名称（回车保持）：").strip()
                if name:
                    update_data['Name'] = name
                years = input("学制（回车保持）：").strip()
                if years:
                    try:
                        update_data['Years'] = float(years)
                    except ValueError:
                        print("❌ 学制无效，跳过")
                if update_data:
                    self.db.update_major(major['AID'], update_data)
            elif choice == '5':
                code = input("请输入要删除的专业代码：").strip()
                major = self.db.get_major_by_code(code)
                if not major:
                    print(f"❌ 专业代码 {code} 不存在")
                    continue
                confirm = input(f"⚠️ 确认删除 {major['Name']}（{code}）？输入 'yes' 确认：").strip()
                if confirm.lower() == 'yes':
                    self.db.delete_major(major['AID'])
                else:
                    print("已取消删除")
            elif choice == '6':
                major_aid = self._pick_major()
                teacher_aid = self._pick_teacher()
                if major_aid and teacher_aid:
                    self.db.set_major_leader(major_aid, teacher_aid)
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    # ==================== 先修课程管理 ====================
    # course_prerequisite 是课程到课程自身的 m:n 自关联表。
    # CourseAID 表示当前课程，PreCourseAID 表示它的先修课程。

    def prerequisite_management_menu(self):
        while True:
            print("\n--- 先修课程管理 ---")
            print("  1. 设置先修关系")
            print("  2. 查看某课程先修链")
            print("  3. 查看所有先修关系")
            print("  4. 删除先修关系")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                courses = self.db.get_all_courses()
                print("\n课程列表：")
                for c in courses:
                    print(f"  {c['AID']}. {c['Code']} {c['Name']}")
                try:
                    ca = int(input("课程AID：").strip())
                    pa = int(input("先修课程AID：").strip())
                    if ca == pa:
                        print("❌ 不能作为自己的先修课程")
                    else:
                        self.db.add_prerequisite(ca, pa)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '2':
                try:
                    ca = int(input("课程AID：").strip())
                except ValueError:
                    print("❌ 无效输入")
                    continue
                prereqs = self.db.get_prerequisites(ca)
                if prereqs:
                    print(f"\n先修课程：")
                    for p in prereqs:
                        print(f"  {p['Code']} - {p['Name']}")
                else:
                    print("暂无先修课程")
            elif choice == '3':
                relations = self.db.get_all_prerequisites()
                if relations:
                    print(f"\n{'课程':<12} {'先修课程':<12}")
                    print("-" * 28)
                    for r in relations:
                        print(f"{r['CourseCode']:<12} ← {r['PreCode']:<12}")
                else:
                    print("暂无先修关系")
            elif choice == '4':
                try:
                    ca = int(input("课程AID：").strip())
                    pa = int(input("先修课程AID：").strip())
                    self.db.delete_prerequisite(ca, pa)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    # ==================== 专业开课管理 ====================
    # major_course 补充原始业务描述中的“专业开设课程”m:n 关系。

    def major_course_management_menu(self):
        while True:
            print("\n--- 专业开课管理 ---")
            print("  1. 设置专业开课")
            print("  2. 查看某专业开设课程")
            print("  3. 查看所有专业开课关系")
            print("  4. 删除专业开课关系")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                major_aid = self._pick_major()
                courses = self.db.get_all_courses()
                for c in courses:
                    print(f"  {c['AID']}. {c['Code']} {c['Name']}")
                try:
                    course_aid = int(input("课程AID：").strip())
                except ValueError:
                    print("❌ 无效输入")
                    continue
                if major_aid:
                    self.db.add_major_course(major_aid, course_aid)
            elif choice == '2':
                major_aid = self._pick_major()
                if not major_aid:
                    continue
                rows = self.db.get_major_courses(major_aid)
                if rows:
                    for r in rows:
                        print(f"  {r['Code']} {r['Name']} 学时{r['Hours']} 学分{r['Credit']}")
                else:
                    print("该专业暂无开设课程")
            elif choice == '3':
                rows = self.db.get_all_major_courses()
                if rows:
                    for r in rows:
                        print(f"  {r['MajorCode']} {r['MajorName']} -> {r['CourseCode']} {r['CourseName']}")
                else:
                    print("暂无专业开课关系")
            elif choice == '4':
                major_aid = self._pick_major()
                try:
                    course_aid = int(input("课程AID：").strip())
                except ValueError:
                    print("❌ 无效输入")
                    continue
                if major_aid:
                    self.db.delete_major_course(major_aid, course_aid)
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    # ==================== 教师指导管理 ====================
    # teacher_guidance 补充原始业务描述中的“教师指导学生并记录起止日期”。

    def teacher_guidance_management_menu(self):
        while True:
            print("\n--- 教师指导管理 ---")
            print("  1. 设置/修改指导关系")
            print("  2. 查看某学生指导教师")
            print("  3. 查看所有指导关系")
            print("  4. 删除指导关系")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                student_code = input("学生学号：").strip()
                student = self.db.get_student_by_code(student_code)
                if not student:
                    print("❌ 学生不存在")
                    continue
                teacher_aid = self._pick_teacher()
                if not teacher_aid:
                    continue
                start_input = input("开始日期（YYYY-MM-DD，默认今天）：").strip()
                end_input = input("结束日期（YYYY-MM-DD，可空）：").strip()
                try:
                    start_date = date.fromisoformat(start_input) if start_input else date.today()
                    end_date = date.fromisoformat(end_input) if end_input else None
                except ValueError:
                    print("❌ 日期格式无效")
                    continue
                self.db.set_teacher_guidance(student['AID'], teacher_aid, start_date, end_date)
            elif choice == '2':
                student_code = input("学生学号：").strip()
                student = self.db.get_student_by_code(student_code)
                if not student:
                    print("❌ 学生不存在")
                    continue
                row = self.db.get_student_guidance(student['AID'])
                if row:
                    end = row['EndDate'] or ''
                    print(f"  {row['StudentCode']} {row['StudentName']} <- "
                          f"{row['TeacherCode']} {row['TeacherName']} "
                          f"{row['StartDate']} 至 {end}")
                else:
                    print("该学生暂无指导教师")
            elif choice == '3':
                rows = self.db.get_all_teacher_guidance()
                if rows:
                    for r in rows[:80]:
                        end = r['EndDate'] or ''
                        print(f"  {r['TeacherCode']} {r['TeacherName']} -> "
                              f"{r['StudentCode']} {r['StudentName']} "
                              f"{r['StartDate']} 至 {end}")
                    if len(rows) > 80:
                        print(f"... 共 {len(rows)} 条，仅显示前80条")
                else:
                    print("暂无指导关系")
            elif choice == '4':
                student_code = input("学生学号：").strip()
                student = self.db.get_student_by_code(student_code)
                if not student:
                    print("❌ 学生不存在")
                    continue
                self.db.delete_teacher_guidance(student['AID'])
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    # ==================== 数据库对象管理子菜单 ====================
    # 这些菜单用于教学演示视图、触发器、存储过程、函数、约束。
    # 它们不创建 DB05 之外的基础业务表。

    def view_management_menu(self):
        while True:
            print("\n--- 视图管理 ---")
            print("  1. 创建学生成绩视图   2. 创建课程统计视图")
            print("  3. 查看所有视图       4. 查询视图内容")
            print("  5. 删除视图           6. 创建学生学分统计视图")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_view_student_scores()
            elif choice == '2':
                self.db.create_view_course_stats()
            elif choice == '3':
                views = self.db.list_views()
                if views:
                    for v in views:
                        print(f"  - {v['view_name']}")
                else:
                    print("暂无视图")
            elif choice == '4':
                vn = input("视图名：").strip()
                rows = self.db.query_view(vn)
                if rows:
                    keys = list(rows[0].keys())
                    print("  ".join([f"{k:<15}" for k in keys]))
                    print("-" * (len(keys) * 17))
                    for r in rows[:20]:
                        print("  ".join([f"{str(v):<15}" for v in r.values()]))
                    print(f"共 {len(rows)} 条")
                else:
                    print("视图无数据或不存在")
            elif choice == '5':
                vn = input("视图名：").strip()
                self.db.drop_view(vn)
            elif choice == '6':
                self.db.create_view_student_credits()
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def trigger_management_menu(self):
        while True:
            print("\n--- 触发器管理 ---")
            print("  1. 创建成绩检查触发器")
            print("  2. 查看所有触发器")
            print("  3. 删除触发器")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_trigger_score_check()
            elif choice == '2':
                triggers = self.db.list_triggers()
                if triggers:
                    for t in triggers:
                        print(f"  {t['TRIGGER_NAME']} ({t['EVENT_MANIPULATION']} {t['EVENT_OBJECT_TABLE']} {t['ACTION_TIMING']})")
                else:
                    print("暂无触发器")
            elif choice == '3':
                tn = input("触发器名：").strip()
                self.db.drop_trigger(tn)
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def procedure_management_menu(self):
        while True:
            print("\n--- 存储过程管理 ---")
            print("  1. 创建学生排名过程    2. 创建课程及格率过程")
            print("  3. 调用学生排名        4. 调用课程及格率")
            print("  5. 查看所有存储过程    6. 删除存储过程")
            print("  7. 创建并调用成绩加分  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_proc_student_rank()
            elif choice == '2':
                self.db.create_proc_course_pass_rate()
            elif choice == '3':
                try:
                    aid = int(input("学生AID：").strip())
                    self.db.call_proc_student_rank(aid)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '4':
                try:
                    aid = int(input("课程AID：").strip())
                    self.db.call_proc_course_pass_rate(aid)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '5':
                procs = self.db.list_procedures()
                for p in procs:
                    print(f"  - {p['ROUTINE_NAME']}")
            elif choice == '6':
                pn = input("存储过程名：").strip()
                self.db.drop_procedure(pn)
            elif choice == '7':
                try:
                    aid = int(input("课程AID：").strip())
                    bonus = float(input("加分值：").strip())
                    self.db.create_proc_score_bonus()
                    self.db.call_proc_score_bonus(aid, bonus)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def function_management_menu(self):
        while True:
            print("\n--- 函数管理 ---")
            print("  1. 创建成绩等级函数    2. 调用函数测试")
            print("  3. 查询演示函数        4. 查看所有函数")
            print("  5. 删除函数            6. 创建GPA函数")
            print("  7. 调用GPA测试         8. 查询演示GPA")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_func_grade_level()
            elif choice == '2':
                try:
                    s = float(input("成绩：").strip())
                    self.db.call_func_grade_level(s)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '3':
                rows = self.db.demo_func_in_query()
                if rows:
                    for r in rows:
                        print(f"  {r['Code']} {r['Name']} {r['CourseName']} {r['Score']} → {r['grade_level']}")
                else:
                    print("暂无数据")
            elif choice == '4':
                funcs = self.db.list_functions()
                for f in funcs:
                    print(f"  - {f['ROUTINE_NAME']}")
            elif choice == '5':
                fn = input("函数名：").strip()
                self.db.drop_function(fn)
            elif choice == '6':
                self.db.create_func_gpa()
            elif choice == '7':
                try:
                    s = float(input("成绩：").strip())
                    self.db.call_func_gpa(s)
                except ValueError:
                    print("❌ 无效输入")
            elif choice == '8':
                rows = self.db.demo_func_gpa_in_query()
                if rows:
                    for r in rows:
                        print(f"  {r['Code']} {r['Name']} {r['CourseName']} {r['Score']} → GPA {r['gpa']}")
                else:
                    print("暂无数据")
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def constraint_management_menu(self):
        while True:
            print("\n--- 完整性约束管理 ---")
            print("  1. 查看表约束         2. 添加CHECK约束")
            print("  3. 删除约束           4. 添加手机号格式约束")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                tn = input("表名：").strip()
                cs = self.db.show_table_constraints(tn)
                if cs:
                    for c in cs:
                        print(f"  {c['CONSTRAINT_NAME']} ({c['CONSTRAINT_TYPE']})")
                else:
                    print("未找到约束")
            elif choice == '2':
                cn = input("约束名：").strip()
                tn = input("表名：").strip()
                cond = input("CHECK条件：").strip()
                self.db.add_check_constraint(cn, tn, cond)
            elif choice == '3':
                tn = input("表名：").strip()
                cn = input("约束名：").strip()
                self.db.drop_constraint(tn, cn)
            elif choice == '4':
                self.db.add_demo_phone_constraint()
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    # ==================== 主循环 ====================

    def run(self):
        print("\n" + "=" * 55)
        print("        🎓 欢迎使用学生选课管理系统 (DB05)")
        print("=" * 55)

        if not self.db.connect():
            print("无法启动系统：数据库连接失败")
            return

        while True:
            self.show_menu()
            choice = input("请选择操作（输入数字）：").strip()

            if choice == '1':
                self.add_student_ui()
            elif choice == '2':
                self.view_all_students()
            elif choice == '3':
                self.search_student_ui()
            elif choice == '4':
                self.update_student_ui()
            elif choice == '5':
                self.delete_student_ui()
            elif choice == '6':
                self.add_course_ui()
            elif choice == '7':
                self.view_all_courses()
            elif choice == '8':
                self.search_course_ui()
            elif choice == '9':
                self.update_course_ui()
            elif choice == '10':
                self.delete_course_ui()
            elif choice == '11':
                self.add_teacher_ui()
            elif choice == '12':
                self.view_all_teachers()
            elif choice == '13':
                self.search_teacher_ui()
            elif choice == '14':
                self.update_teacher_ui()
            elif choice == '15':
                self.delete_teacher_ui()
            elif choice == '16':
                self.add_course_selection_ui()
            elif choice == '17':
                self.view_student_courses_ui()
            elif choice == '18':
                self.view_all_course_selections_ui()
            elif choice == '19':
                self.drop_course_ui()
            elif choice == '20':
                self.update_score_ui()
            elif choice == '21':
                self.major_management_menu()
            elif choice == '22':
                self.prerequisite_management_menu()
            elif choice == '23':
                self.query_total_credits_ui()
            elif choice == '24':
                self.query_average_score_ui()
            elif choice == '25':
                self.view_management_menu()
            elif choice == '26':
                self.trigger_management_menu()
            elif choice == '27':
                self.procedure_management_menu()
            elif choice == '28':
                self.function_management_menu()
            elif choice == '29':
                self.constraint_management_menu()
            elif choice == '30':
                self.major_course_management_menu()
            elif choice == '31':
                self.teacher_guidance_management_menu()
            elif choice == '0':
                print("\n感谢使用学生选课管理系统，再见！👋")
                self.db.close()
                break
            else:
                print("❌ 无效选择，请重新输入")

            input("\n按回车键继续...")


if __name__ == "__main__":
    system = StudentCourseSystem()
    system.run()
