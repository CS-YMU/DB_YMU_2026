from models import Student
from database import Database
import os

class StudentManagementSystem:
    def __init__(self):
        self.db = Database(
            host='localhost',
            database='stu_score',
            user='dylan',
            password='P@ssw0rd'
        )
    
    def show_menu(self):
        """显示系统菜单"""
        print("\n" + "="*50)
        print("        🎓 学生信息管理系统")
        print("="*50)
        print("1. 添加学生信息")
        print("2. 查看所有学生")
        print("3. 搜索学生")
        print("4. 修改学生信息")
        print("5. 删除学生信息")
        print("6. 统计信息")
        print("7. 数据备份")
        print("0. 退出系统")
        print("="*50)
    
    def add_student_ui(self):
        """添加学生界面"""
        print("\n--- 添加新学生 ---")
        student_id = input("请输入学号：").strip()
        name = input("请输入姓名：").strip()
        gender = input("请输入性别（男/女/其他）：").strip()
        age = int(input("请输入年龄：").strip())
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
            print("-"*70)
            for s in students:
                print(f"{s['student_id']:<12} {s['name']:<10} {s['gender']:<6} {s['age']:<6} {s['major']:<15} {s['phone']:<15}")
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
            for s in results:
                print(f"学号：{s['student_id']} | 姓名：{s['name']} | 专业：{s['major']}")
        else:
            print("未找到匹配的学生")
    
    def run(self):
        """系统主循环"""
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
                student_id = input("请输入要修改的学号：").strip()
                # 修改逻辑实现
            elif choice == '5':
                student_id = input("请输入要删除的学号：").strip()
                self.db.delete_student(student_id)
            elif choice == '6':
                # 统计信息
                students = self.db.get_all_students()
                print(f"\n📊 系统统计")
                print(f"总学生数：{len(students)}")
                if students:
                    majors = set(s['major'] for s in students)
                    print(f"专业数：{len(majors)}")
            elif choice == '0':
                print("感谢使用学生信息管理系统！")
                self.db.close()
                break
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")

if __name__ == "__main__":
    system = StudentManagementSystem()
    system.run()