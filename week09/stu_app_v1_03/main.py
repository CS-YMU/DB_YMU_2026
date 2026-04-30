from models import Student, Course, SC, Teacher
from database import Database


class StudentCourseSystem:
    """学生选课管理系统"""

    def __init__(self, host='localhost', database='student_db', user='dylan', password='P@ssw0rd'):
        """初始化系统，可自定义数据库连接参数"""
        self.db = Database(host, database, user, password)

    def show_menu(self):
        """显示系统主菜单"""
        print("\n" + "=" * 55)
        print("               🎓 学生选课管理系统")
        print("=" * 55)
        print("  【学生管理】")
        print("  1. 添加学生")
        print("  2. 查看所有学生")
        print("  3. 搜索学生")
        print("  4. 修改学生信息")
        print("  5. 删除学生")
        print()
        print("  【课程管理】")
        print("  6. 添加课程")
        print("  7. 查看所有课程")
        print("  8. 搜索课程")
        print("  9. 修改课程信息")
        print("  10. 删除课程")
        print()
        print("  【教师管理】")
        print("  11. 添加教师")
        print("  12. 查看所有教师")
        print("  13. 搜索教师")
        print("  14. 修改教师信息")
        print("  15. 删除教师")
        print()
        print("  【选课管理】")
        print("  16. 学生选课")
        print("  17. 查看某学生选课情况")
        print("  18. 查看所有选课记录")
        print("  19. 退课")
        print("  20. 录入/修改成绩")
        print()
        print("  【先修课程管理】")
        print("  21. 先修课程管理")
        print()
        print("  【成绩统计】")
        print("  22. 查询学生总学分")
        print("  23. 查询学生平均成绩")
        print()
        print("  【数据库对象管理】")
        print("  24. 视图管理")
        print("  25. 触发器管理")
        print("  26. 存储过程管理")
        print("  27. 函数管理")
        print("  28. 完整性约束管理")
        print()
        print("  0. 退出系统")
        print("=" * 55)

    # ==================== 学生管理功能 ====================

    def add_student_ui(self):
        """添加学生界面"""
        print("\n--- 添加新学生 ---")
        student_id = input("请输入学号：").strip()
        name = input("请输入姓名：").strip()

        while True:
            gender = input("请输入性别（男/女/其他）：").strip()
            if gender in ['男', '女', '其他']:
                break
            print("❌ 输入无效，请输入男、女 或 其他")

        while True:
            try:
                age = int(input("请输入年龄：").strip())
                if age <= 0 or age > 150:
                    print("❌ 年龄需要在 1-150 之间")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的整数")

        major = input("请输入专业：").strip()
        phone = input("请输入电话：").strip()

        student = Student(student_id, name, gender, age, major, phone)
        self.db.add_student(student)

    def view_all_students(self):
        """查看所有学生"""
        print("\n--- 所有学生信息 ---")
        students = self.db.get_all_students()
        if students:
            print(f"\n{'学号':<12} {'姓名':<10} {'性别':<6} {'年龄':<6} {'专业':<15} {'电话':<15}")
            print("-" * 70)
            for s in students:
                print(f"{s['student_id']:<12} {s['name']:<10} {s['gender']:<6} "
                      f"{s['age']:<6} {s['major']:<15} {s['phone']:<15}")
            print(f"\n共 {len(students)} 条记录")
        else:
            print("暂无学生信息")

    def search_student_ui(self):
        """搜索学生界面"""
        print("\n--- 搜索学生 ---")
        keyword = input("请输入学号或姓名关键词：").strip()
        results = self.db.search_student(keyword)
        if results:
            print(f"\n找到 {len(results)} 条记录：")
            print(f"\n{'学号':<12} {'姓名':<10} {'性别':<6} {'年龄':<6} {'专业':<15}")
            print("-" * 60)
            for s in results:
                print(f"{s['student_id']:<12} {s['name']:<10} {s['gender']:<6} "
                      f"{s['age']:<6} {s['major']:<15}")
        else:
            print("未找到匹配的学生")

    def update_student_ui(self):
        """修改学生信息界面"""
        print("\n--- 修改学生信息 ---")
        student_id = input("请输入要修改的学号：").strip()

        if not self.db.student_exists(student_id):
            print(f"❌ 学号 {student_id} 不存在")
            return

        print("请输入新的学生信息（直接回车保持原值）：")
        name = input("姓名：").strip()
        gender = input("性别（男/女/其他）：").strip()

        age = None
        while True:
            age_input = input("年龄：").strip()
            if age_input == '':
                break
            try:
                age = int(age_input)
                if age <= 0 or age > 150:
                    print("❌ 年龄需要在 1-150 之间，请重新输入")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的整数")

        major = input("专业：").strip()
        phone = input("电话：").strip()

        update_data = {}
        if name:
            update_data['name'] = name
        if gender:
            if gender not in ['男', '女', '其他']:
                print("❌ 性别输入无效，跳过该字段")
            else:
                update_data['gender'] = gender
        if age is not None:
            update_data['age'] = age
        if major:
            update_data['major'] = major
        if phone:
            update_data['phone'] = phone

        if not update_data:
            print("❌ 没有提供任何更新内容")
            return

        students = self.db.search_student(student_id)
        if students:
            original = students[0]
            for key in ['name', 'gender', 'age', 'major', 'phone']:
                if key not in update_data:
                    update_data[key] = original[key]

        self.db.update_student(student_id, update_data)

    def delete_student_ui(self):
        """删除学生界面"""
        print("\n--- 删除学生 ---")
        student_id = input("请输入要删除的学号：").strip()

        if not self.db.student_exists(student_id):
            print(f"❌ 学号 {student_id} 不存在")
            return

        confirm = input(f"⚠️ 确认删除学号 {student_id} ？（该操作将同时删除其所有选课记录）\n"
                        f"请输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_student(student_id)
        else:
            print("已取消删除")

    # ==================== 课程管理功能 ====================

    def add_course_ui(self):
        """添加课程界面"""
        print("\n--- 添加新课程 ---")
        course_id = input("请输入课程号：").strip()
        course_name = input("请输入课程名：").strip()

        # 选择授课教师
        teachers = self.db.get_all_teachers()
        if not teachers:
            print("❌ 暂无教师可选，请先添加教师")
            return

        print("\n可选教师列表：")
        print(f"\n{'教师编号':<12} {'姓名':<10} {'职称':<10}")
        print("-" * 35)
        for t in teachers:
            print(f"{t['teacher_id']:<12} {t['name']:<10} {t['title']:<10}")

        teacher_id = input("\n请输入授课教师编号：").strip()
        if not self.db.teacher_exists(teacher_id):
            print(f"❌ 教师编号 {teacher_id} 不存在")
            return

        while True:
            try:
                credit = float(input("请输入学分：").strip())
                if credit <= 0 or credit > 10:
                    print("❌ 学分需要在 0.1-10 之间")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的数字")

        course = Course(course_id, course_name, teacher_id, credit)
        self.db.add_course(course)

    def view_all_courses(self):
        """查看所有课程"""
        print("\n--- 所有课程信息 ---")
        courses = self.db.get_all_courses()
        if courses:
            print(f"\n{'课程号':<12} {'课程名':<20} {'任课教师':<15} {'学分':<8}")
            print("-" * 60)
            for c in courses:
                print(f"{c['course_id']:<12} {c['course_name']:<20} "
                      f"{c['teacher_name']:<15} {c['credit']:<8}")
            print(f"\n共 {len(courses)} 门课程")
        else:
            print("暂无课程信息")

    def search_course_ui(self):
        """搜索课程界面"""
        print("\n--- 搜索课程 ---")
        keyword = input("请输入课程号或课程名关键词：").strip()
        results = self.db.search_course(keyword)
        if results:
            print(f"\n找到 {len(results)} 条记录：")
            print(f"\n{'课程号':<12} {'课程名':<20} {'任课教师':<15} {'学分':<8}")
            print("-" * 60)
            for c in results:
                print(f"{c['course_id']:<12} {c['course_name']:<20} "
                      f"{c['teacher_name']:<15} {c['credit']:<8}")
        else:
            print("未找到匹配的课程")

    def update_course_ui(self):
        """修改课程信息界面"""
        print("\n--- 修改课程信息 ---")
        course_id = input("请输入要修改的课程号：").strip()

        if not self.db.course_exists(course_id):
            print(f"❌ 课程号 {course_id} 不存在")
            return

        print("请输入新的课程信息（直接回车保持原值）：")
        course_name = input("课程名：").strip()

        # 显示教师列表供选择
        teachers = self.db.get_all_teachers()
        if teachers:
            print("\n可选教师列表（直接回车保持原教师）：")
            print(f"{'教师编号':<12} {'姓名':<10} {'职称':<10}")
            print("-" * 35)
            for t in teachers:
                print(f"{t['teacher_id']:<12} {t['name']:<10} {t['title']:<10}")
        teacher_id = input("请输入授课教师编号：").strip()

        credit = None
        while True:
            credit_input = input("学分：").strip()
            if credit_input == '':
                break
            try:
                credit = float(credit_input)
                if credit <= 0 or credit > 10:
                    print("❌ 学分需要在 0.1-10 之间，请重新输入")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的数字")

        update_data = {}
        if course_name:
            update_data['course_name'] = course_name
        if teacher_id:
            if not self.db.teacher_exists(teacher_id):
                print(f"❌ 教师编号 {teacher_id} 不存在，跳过该字段")
            else:
                update_data['teacher_id'] = teacher_id
        if credit is not None:
            update_data['credit'] = credit

        if not update_data:
            print("❌ 没有提供任何更新内容")
            return

        # 填充原值
        original = self.db.get_course_by_id(course_id)
        if original:
            for key in ['course_name', 'teacher_id', 'credit']:
                if key not in update_data:
                    update_data[key] = original[key]

        self.db.update_course(course_id, update_data)

    def delete_course_ui(self):
        """删除课程界面"""
        print("\n--- 删除课程 ---")
        course_id = input("请输入要删除的课程号：").strip()

        if not self.db.course_exists(course_id):
            print(f"❌ 课程号 {course_id} 不存在")
            return

        confirm = input(f"⚠️ 确认删除课程号 {course_id}？\n"
                        f"（如有学生已选修该课程，将无法删除）\n"
                        f"请输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_course(course_id)
        else:
            print("已取消删除")

    # ==================== 教师管理功能 ====================

    def add_teacher_ui(self):
        """添加教师界面"""
        print("\n--- 添加新教师 ---")
        teacher_id = input("请输入教师编号：").strip()
        name = input("请输入姓名：").strip()

        while True:
            gender = input("请输入性别（男/女/其他）：").strip()
            if gender in ['男', '女', '其他']:
                break
            print("❌ 输入无效，请输入男、女 或 其他")

        while True:
            try:
                age = int(input("请输入年龄：").strip())
                if age <= 0 or age > 150:
                    print("❌ 年龄需要在 1-150 之间")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的整数")

        while True:
            title = input("请输入职称（教授/副教授/讲师/助教）：").strip()
            if title in ['教授', '副教授', '讲师', '助教']:
                break
            print("❌ 输入无效，请输入教授、副教授、讲师 或 助教")

        phone = input("请输入电话：").strip()

        teacher = Teacher(teacher_id, name, gender, age, title, phone)
        self.db.add_teacher(teacher)

    def view_all_teachers(self):
        """查看所有教师"""
        print("\n--- 所有教师信息 ---")
        teachers = self.db.get_all_teachers()
        if teachers:
            print(f"\n{'教师编号':<12} {'姓名':<10} {'性别':<6} {'年龄':<6} {'职称':<10} {'电话':<15}")
            print("-" * 65)
            for t in teachers:
                print(f"{t['teacher_id']:<12} {t['name']:<10} {t['gender']:<6} "
                      f"{t['age']:<6} {t['title']:<10} {t['phone']:<15}")
            print(f"\n共 {len(teachers)} 位教师")
        else:
            print("暂无教师信息")

    def search_teacher_ui(self):
        """搜索教师界面"""
        print("\n--- 搜索教师 ---")
        keyword = input("请输入教师编号或姓名关键词：").strip()
        results = self.db.search_teacher(keyword)
        if results:
            print(f"\n找到 {len(results)} 条记录：")
            print(f"\n{'教师编号':<12} {'姓名':<10} {'性别':<6} {'年龄':<6} {'职称':<10}")
            print("-" * 55)
            for t in results:
                print(f"{t['teacher_id']:<12} {t['name']:<10} {t['gender']:<6} "
                      f"{t['age']:<6} {t['title']:<10}")
        else:
            print("未找到匹配的教师")

    def update_teacher_ui(self):
        """修改教师信息界面"""
        print("\n--- 修改教师信息 ---")
        teacher_id = input("请输入要修改的教师编号：").strip()

        if not self.db.teacher_exists(teacher_id):
            print(f"❌ 教师编号 {teacher_id} 不存在")
            return

        print("请输入新的教师信息（直接回车保持原值）：")
        name = input("姓名：").strip()
        gender = input("性别（男/女/其他）：").strip()

        age = None
        while True:
            age_input = input("年龄：").strip()
            if age_input == '':
                break
            try:
                age = int(age_input)
                if age <= 0 or age > 150:
                    print("❌ 年龄需要在 1-150 之间，请重新输入")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的整数")

        title = input("职称（教授/副教授/讲师/助教）：").strip()
        phone = input("电话：").strip()

        update_data = {}
        if name:
            update_data['name'] = name
        if gender:
            if gender not in ['男', '女', '其他']:
                print("❌ 性别输入无效，跳过该字段")
            else:
                update_data['gender'] = gender
        if age is not None:
            update_data['age'] = age
        if title:
            if title not in ['教授', '副教授', '讲师', '助教']:
                print("❌ 职称输入无效，跳过该字段")
            else:
                update_data['title'] = title
        if phone:
            update_data['phone'] = phone

        if not update_data:
            print("❌ 没有提供任何更新内容")
            return

        # 填充原值
        original = self.db.get_teacher_by_id(teacher_id)
        if original:
            for key in ['name', 'gender', 'age', 'title', 'phone']:
                if key not in update_data:
                    update_data[key] = original[key]

        self.db.update_teacher(teacher_id, update_data)

    def delete_teacher_ui(self):
        """删除教师界面"""
        print("\n--- 删除教师 ---")
        teacher_id = input("请输入要删除的教师编号：").strip()

        if not self.db.teacher_exists(teacher_id):
            print(f"❌ 教师编号 {teacher_id} 不存在")
            return

        confirm = input(f"⚠️ 确认删除教师编号 {teacher_id}？（该操作将同时删除其所有选课记录）\n"
                        f"请输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_teacher(teacher_id)
        else:
            print("已取消删除")

    # ==================== 选课管理功能 ====================

    def add_course_selection_ui(self):
        """学生选课界面"""
        print("\n--- 学生选课 ---")
        student_id = input("请输入学号：").strip()

        if not self.db.student_exists(student_id):
            print(f"❌ 学号 {student_id} 不存在，请先添加学生")
            return

        # 显示所有可选课程
        courses = self.db.get_all_courses()
        if not courses:
            print("❌ 暂无课程可选，请先添加课程")
            return

        print("\n可选课程列表：")
        print(f"\n{'课程号':<12} {'课程名':<20} {'任课教师':<15} {'学分':<8}")
        print("-" * 60)
        for c in courses:
            print(f"{c['course_id']:<12} {c['course_name']:<20} "
                  f"{c['teacher_name']:<15} {c['credit']:<8}")

        print()
        course_id = input("请输入要选修的课程号：").strip()

        if not self.db.course_exists(course_id):
            print(f"❌ 课程号 {course_id} 不存在")
            return

        semester = input("请输入学期（如：2024-1、2024-2）：").strip()

        sc_record = SC(student_id, course_id, semester)
        self.db.add_course_selection(sc_record)

    def view_student_courses_ui(self):
        """查看某学生选课情况界面"""
        print("\n--- 查看学生选课情况 ---")
        student_id = input("请输入学号：").strip()

        courses = self.db.get_student_courses(student_id)
        if courses:
            print(f"\n学生 {student_id} 的选课记录：")
            print(f"\n{'课程号':<12} {'课程名':<15} {'教师':<10} {'学分':<6} {'学期':<10} {'成绩':<8}")
            print("-" * 65)
            for c in courses:
                score_str = str(c['score']) if c['score'] is not None else "未录入"
                course_name = c['course_name'] if c['course_name'] else "未知"
                teacher_name = c['teacher_name'] if c['teacher_name'] else "未知"
                credit = c['credit'] if c['credit'] else 0
                print(f"{c['course_id']:<12} {course_name:<15} {teacher_name:<10} "
                      f"{credit:<6} {c['semester']:<10} {score_str:<8}")
            print(f"\n共选修 {len(courses)} 门课程")
        else:
            print(f"学号 {student_id} 暂无选课记录")

    def view_all_course_selections_ui(self):
        """查看所有选课记录界面"""
        print("\n--- 所有选课记录 ---")
        records = self.db.get_all_course_selections()
        if records:
            print(f"\n{'学号':<10} {'姓名':<10} {'课程号':<10} {'课程名':<15} {'教师':<10} "
                  f"{'学分':<6} {'学期':<10} {'成绩':<8}")
            print("-" * 85)
            for r in records:
                score_str = str(r['score']) if r['score'] is not None else "未录入"
                student_name = r['student_name'] if r['student_name'] else "未知"
                course_name = r['course_name'] if r['course_name'] else "未知"
                teacher_name = r['teacher_name'] if r['teacher_name'] else "未知"
                credit = r['credit'] if r['credit'] else 0
                print(f"{r['student_id']:<10} {student_name:<10} {r['course_id']:<10} "
                      f"{course_name:<15} {teacher_name:<10} {credit:<6} "
                      f"{r['semester']:<10} {score_str:<8}")
            print(f"\n共 {len(records)} 条选课记录")
        else:
            print("暂无选课记录")

    def drop_course_ui(self):
        """退课界面"""
        print("\n--- 退课 ---")
        student_id = input("请输入学号：").strip()
        course_id = input("请输入课程号：").strip()
        semester = input("请输入学期：").strip()

        # 确认退课
        confirm = input(f"⚠️ 确认退课：{student_id} - {course_id}（{semester}）？\n"
                        f"请输入 'yes' 确认：").strip()
        if confirm.lower() == 'yes':
            self.db.drop_course_selection(student_id, course_id, semester)
        else:
            print("已取消退课")

    def update_score_ui(self):
        """录入/修改成绩界面"""
        print("\n--- 录入/修改成绩 ---")
        student_id = input("请输入学号：").strip()
        course_id = input("请输入课程号：").strip()
        semester = input("请输入学期：").strip()

        # 先检查该选课记录是否存在
        courses = self.db.get_student_courses(student_id)
        found = False
        for c in courses:
            if c['course_id'] == course_id and c['semester'] == semester:
                found = True
                break

        if not found:
            print(f"❌ 未找到对应的选课记录：{student_id} - {course_id}（{semester}）")
            return

        # 成绩输入，允许为空
        while True:
            score_input = input("请输入成绩（0-100，直接回车留空）：").strip()
            if score_input == '':
                print("✅ 成绩已设为空（未录入）")
                return
            try:
                score = float(score_input)
                if score < 0 or score > 100:
                    print("❌ 成绩需要在 0-100 之间")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的数字")

        self.db.update_score(student_id, course_id, semester, score)

    # ==================== 成绩统计功能 ====================

    def query_total_credits_ui(self):
        """查询学生总学分界面"""
        print("\n--- 查询学生总学分 ---")
        student_id = input("请输入学号：").strip()

        if not self.db.student_exists(student_id):
            print(f"❌ 学号 {student_id} 不存在")
            return

        self.db.get_student_total_credits(student_id)

    def query_average_score_ui(self):
        """查询学生平均成绩界面"""
        print("\n--- 查询学生平均成绩 ---")
        student_id = input("请输入学号：").strip()

        if not self.db.student_exists(student_id):
            print(f"❌ 学号 {student_id} 不存在")
            return

        self.db.get_student_average_score(student_id)

    # ==================== 先修课程管理功能 ====================

    def prerequisite_management_menu(self):
        """先修课程管理子菜单"""
        while True:
            print("\n--- 先修课程管理 ---")
            print("  1. 设置课程先修关系")
            print("  2. 查看某课程的先修链")
            print("  3. 查看所有先修关系")
            print("  4. 删除先修关系")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                course_id = input("请输入课程号（需要设置先修的课程）：").strip()
                if not self.db.course_exists(course_id):
                    print(f"❌ 课程号 {course_id} 不存在")
                    continue
                prereq_id = input("请输入先修课程号：").strip()
                if not self.db.course_exists(prereq_id):
                    print(f"❌ 先修课程号 {prereq_id} 不存在")
                    continue
                if course_id == prereq_id:
                    print("❌ 课程不能作为自己的先修课程")
                    continue
                self.db.add_prerequisite(course_id, prereq_id)
            elif choice == '2':
                course_id = input("请输入课程号：").strip()
                if not self.db.course_exists(course_id):
                    print(f"❌ 课程号 {course_id} 不存在")
                    continue
                prereqs = self.db.get_prerequisites(course_id)
                if prereqs:
                    print(f"\n课程 {course_id} 的先修课程：")
                    print(f"{'先修课程号':<12} {'课程名':<20}")
                    print("-" * 35)
                    for p in prereqs:
                        print(f"{p['prerequisite_id']:<12} {p['course_name']:<20}")
                else:
                    print(f"课程 {course_id} 暂无先修课程")
            elif choice == '3':
                relations = self.db.get_all_prerequisites()
                if relations:
                    print(f"\n{'课程号':<12} {'课程名':<20} {'先修课程号':<12} {'先修课程名':<20}")
                    print("-" * 68)
                    for r in relations:
                        print(f"{r['course_id']:<12} {r['course_name']:<20} "
                              f"{r['prerequisite_id']:<12} {r['prerequisite_name']:<20}")
                else:
                    print("暂无先修关系")
            elif choice == '4':
                course_id = input("请输入课程号：").strip()
                prereq_id = input("请输入先修课程号：").strip()
                self.db.delete_prerequisite(course_id, prereq_id)
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    # ==================== 数据库对象管理功能（教学演示用） ====================

    def view_management_menu(self):
        """视图管理子菜单"""
        while True:
            print("\n--- 视图管理 ---")
            print("  1. 创建学生成绩视图（v_student_scores）")
            print("  2. 创建课程统计视图（v_course_stats）")
            print("  3. 查看所有视图")
            print("  4. 查询视图内容")
            print("  5. 删除视图")
            print("  6. 【课后作业】创建学生学分统计视图（v_student_credits）")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_view_student_scores()
            elif choice == '2':
                self.db.create_view_course_stats()
            elif choice == '3':
                views = self.db.list_views()
                if views:
                    print(f"\n{'视图名':<30}")
                    print("-" * 30)
                    for v in views:
                        print(f"{v['view_name']:<30}")
                else:
                    print("当前数据库暂无视图")
            elif choice == '4':
                view_name = input("请输入要查询的视图名：").strip()
                rows = self.db.query_view(view_name)
                if rows:
                    print(f"\n共查询到 {len(rows)} 条记录：")
                    # 取第一条的 keys 作为表头
                    keys = list(rows[0].keys())
                    print("  ".join([f"{k:<15}" for k in keys]))
                    print("-" * (len(keys) * 17))
                    for r in rows[:20]:  # 最多显示20条，避免刷屏
                        print("  ".join([f"{str(v):<15}" for v in r.values()]))
                else:
                    print("视图无数据或不存在")
            elif choice == '5':
                view_name = input("请输入要删除的视图名：").strip()
                self.db.drop_view(view_name)
            elif choice == '6':
                self.db.create_view_student_credits()
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def trigger_management_menu(self):
        """触发器管理子菜单"""
        while True:
            print("\n--- 触发器管理 ---")
            print("  1. 创建成绩范围检查触发器（INSERT/UPDATE）")
            print("  2. 创建学生删除日志触发器（AFTER DELETE）")
            print("  3. 查看所有触发器")
            print("  4. 查看删除日志")
            print("  5. 删除触发器")
            print("  6. 【课后作业】创建专业变更日志触发器（AFTER UPDATE）")
            print("  7. 【课后作业】查看专业变更日志")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_trigger_score_check()
            elif choice == '2':
                self.db.create_trigger_student_delete_log()
            elif choice == '3':
                triggers = self.db.list_triggers()
                if triggers:
                    print(f"\n{'触发器名':<35} {'事件':<10} {'表名':<15} {'时机':<10}")
                    print("-" * 75)
                    for t in triggers:
                        print(f"{t['TRIGGER_NAME']:<35} {t['EVENT_MANIPULATION']:<10} {t['EVENT_OBJECT_TABLE']:<15} {t['ACTION_TIMING']:<10}")
                else:
                    print("当前数据库暂无触发器")
            elif choice == '4':
                logs = self.db.get_delete_logs()
                if logs:
                    print(f"\n{'学号':<12} {'姓名':<10} {'专业':<15} {'删除时间':<20}")
                    print("-" * 60)
                    for log in logs:
                        print(f"{log['student_id']:<12} {log['name']:<10} {log['major']:<15} {str(log['deleted_at']):<20}")
                else:
                    print("暂无删除日志记录")
            elif choice == '5':
                trigger_name = input("请输入要删除的触发器名：").strip()
                self.db.drop_trigger(trigger_name)
            elif choice == '6':
                self.db.create_trigger_major_change_log()
            elif choice == '7':
                logs = self.db.get_major_change_logs()
                if logs:
                    print(f"\n{'学号':<12} {'旧专业':<15} {'新专业':<15} {'变更时间':<20}")
                    print("-" * 65)
                    for log in logs:
                        print(f"{log['student_id']:<12} {log['old_major']:<15} {log['new_major']:<15} {str(log['changed_at']):<20}")
                else:
                    print("暂无专业变更日志记录")
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def procedure_management_menu(self):
        """存储过程管理子菜单"""
        while True:
            print("\n--- 存储过程管理 ---")
            print("  1. 创建学生排名存储过程（sp_student_rank）")
            print("  2. 创建课程及格率存储过程（sp_course_pass_rate）")
            print("  3. 调用学生排名存储过程")
            print("  4. 调用课程及格率存储过程")
            print("  5. 查看所有存储过程")
            print("  6. 删除存储过程")
            print("  7. 【课后作业】创建并调用成绩加分存储过程（sp_score_bonus）")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_proc_student_rank()
            elif choice == '2':
                self.db.create_proc_course_pass_rate()
            elif choice == '3':
                student_id = input("请输入学号：").strip()
                self.db.call_proc_student_rank(student_id)
            elif choice == '4':
                course_id = input("请输入课程号：").strip()
                self.db.call_proc_course_pass_rate(course_id)
            elif choice == '5':
                procs = self.db.list_procedures()
                if procs:
                    print("\n存储过程列表：")
                    for p in procs:
                        print(f"  - {p['ROUTINE_NAME']}")
                else:
                    print("当前数据库暂无存储过程")
            elif choice == '6':
                proc_name = input("请输入要删除的存储过程名：").strip()
                self.db.drop_procedure(proc_name)
            elif choice == '7':
                course_id = input("请输入课程号：").strip()
                try:
                    bonus = float(input("请输入加分值：").strip())
                    self.db.create_proc_score_bonus()
                    self.db.call_proc_score_bonus(course_id, bonus)
                except ValueError:
                    print("❌ 请输入有效的数字")
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def function_management_menu(self):
        """函数管理子菜单"""
        while True:
            print("\n--- 函数管理 ---")
            print("  1. 创建成绩等级函数（fn_grade_level）")
            print("  2. 调用函数测试")
            print("  3. 在查询中演示函数（显示学生成绩等级）")
            print("  4. 查看所有函数")
            print("  5. 删除函数")
            print("  6. 【课后作业】创建 GPA 转换函数（fn_gpa）")
            print("  7. 【课后作业】调用 GPA 函数测试")
            print("  8. 【课后作业】在查询中演示 GPA 函数")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                self.db.create_func_grade_level()
            elif choice == '2':
                score_input = input("请输入成绩（0-100）：").strip()
                try:
                    score = float(score_input)
                    self.db.call_func_grade_level(score)
                except ValueError:
                    print("❌ 请输入有效数字")
            elif choice == '3':
                rows = self.db.demo_func_in_query()
                if rows:
                    print(f"\n{'学号':<10} {'姓名':<8} {'课程名':<12} {'成绩':<6} {'等级':<6}")
                    print("-" * 50)
                    for r in rows:
                        print(f"{r['student_id']:<10} {r['name']:<8} {r['course_name']:<12} {str(r['score']):<6} {r['grade_level']:<6}")
                else:
                    print("暂无数据或函数未创建")
            elif choice == '4':
                funcs = self.db.list_functions()
                if funcs:
                    print("\n函数列表：")
                    for f in funcs:
                        print(f"  - {f['ROUTINE_NAME']}")
                else:
                    print("当前数据库暂无自定义函数")
            elif choice == '5':
                func_name = input("请输入要删除的函数名：").strip()
                self.db.drop_function(func_name)
            elif choice == '6':
                self.db.create_func_gpa()
            elif choice == '7':
                score_input = input("请输入成绩（0-100）：").strip()
                try:
                    score = float(score_input)
                    self.db.call_func_gpa(score)
                except ValueError:
                    print("❌ 请输入有效数字")
            elif choice == '8':
                rows = self.db.demo_func_gpa_in_query()
                if rows:
                    print(f"\n{'学号':<10} {'姓名':<8} {'课程名':<12} {'成绩':<6} {'GPA':<6}")
                    print("-" * 50)
                    for r in rows:
                        print(f"{r['student_id']:<10} {r['name']:<8} {r['course_name']:<12} {str(r['score']):<6} {r['gpa']:<6}")
                else:
                    print("暂无数据或函数未创建")
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def constraint_management_menu(self):
        """完整性约束管理子菜单"""
        while True:
            print("\n--- 完整性约束管理 ---")
            print("  1. 查看指定表的所有约束")
            print("  2. 添加 CHECK 约束（示例：course 表 credit > 0）")
            print("  3. 删除指定约束")
            print("  4. 【课后作业】添加手机号格式 CHECK 约束")
            print("  0. 返回上级菜单")
            choice = input("请选择：").strip()

            if choice == '1':
                table_name = input("请输入表名（students / course / sc）：").strip()
                constraints = self.db.show_table_constraints(table_name)
                if constraints:
                    print(f"\n{'约束名':<35} {'约束类型':<15}")
                    print("-" * 55)
                    for c in constraints:
                        print(f"{c['CONSTRAINT_NAME']:<35} {c['CONSTRAINT_TYPE']:<15}")
                else:
                    print("未找到约束信息")
            elif choice == '2':
                print("示例：为 course 表添加 credit > 0 的 CHECK 约束")
                constraint_name = input("请输入约束名（如 chk_credit_positive）：").strip()
                table_name = input("请输入表名：").strip()
                condition = input("请输入 CHECK 条件（如 credit > 0）：").strip()
                self.db.add_check_constraint(constraint_name, table_name, condition)
            elif choice == '3':
                table_name = input("请输入表名：").strip()
                constraint_name = input("请输入约束名：").strip()
                self.db.drop_constraint(table_name, constraint_name)
            elif choice == '4':
                self.db.add_demo_phone_constraint()
            elif choice == '0':
                break
            else:
                print("❌ 无效选择")

    def run(self):
        """系统主循环"""
        print("\n" + "=" * 55)
        print("        🎓 欢迎使用学生选课管理系统 🎓")
        print("=" * 55)

        if not self.db.connect():
            print("无法启动系统：数据库连接失败")
            return

        self.db.create_tables()

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
                self.prerequisite_management_menu()
            elif choice == '22':
                self.query_total_credits_ui()
            elif choice == '23':
                self.query_average_score_ui()
            elif choice == '24':
                self.view_management_menu()
            elif choice == '25':
                self.trigger_management_menu()
            elif choice == '26':
                self.procedure_management_menu()
            elif choice == '27':
                self.function_management_menu()
            elif choice == '28':
                self.constraint_management_menu()
            elif choice == '0':
                print("\n感谢使用学生选课管理系统，再见！👋")
                self.db.close()
                break
            else:
                print("❌ 无效选择，请重新输入")

            input("\n按回车键继续...")


if __name__ == "__main__":
    system = StudentCourseSystem(
        host='localhost',
        database='student_db',
        user='dylan',
        password='P@ssw0rd'
    )
    system.run()
