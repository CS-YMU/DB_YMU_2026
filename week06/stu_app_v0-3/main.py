from models import Student, Course, SC
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
        print("  【选课管理】")
        print("  11. 学生选课")
        print("  12. 查看某学生选课情况")
        print("  13. 查看所有选课记录")
        print("  14. 退课")
        print("  15. 录入/修改成绩")
        print()
        print("  【成绩统计】")
        print("  16. 查询学生总学分")
        print("  17. 查询学生平均成绩")
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
        teacher_name = input("请输入任课教师：").strip()

        while True:
            try:
                credit = float(input("请输入学分：").strip())
                if credit <= 0 or credit > 10:
                    print("❌ 学分需要在 0.1-10 之间")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效的数字")

        course = Course(course_id, course_name, teacher_name, credit)
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
        teacher_name = input("任课教师：").strip()

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
        if teacher_name:
            update_data['teacher_name'] = teacher_name
        if credit is not None:
            update_data['credit'] = credit

        if not update_data:
            print("❌ 没有提供任何更新内容")
            return

        # 填充原值
        original = self.db.get_course_by_id(course_id)
        if original:
            for key in ['course_name', 'teacher_name', 'credit']:
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
                self.add_course_selection_ui()
            elif choice == '12':
                self.view_student_courses_ui()
            elif choice == '13':
                self.view_all_course_selections_ui()
            elif choice == '14':
                self.drop_course_ui()
            elif choice == '15':
                self.update_score_ui()
            elif choice == '16':
                self.query_total_credits_ui()
            elif choice == '17':
                self.query_average_score_ui()
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
