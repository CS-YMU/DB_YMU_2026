"""高级数据库对象初始化 —— DB05 版本。

本脚本用于教学演示数据库高级对象：
视图、触发器、存储过程、函数。

注意：
这些对象不属于完整业务版的 18 张基础表。它们可以帮助学生理解
数据库应用设计，但不会额外创建业务基础表。
"""
from database import Database
from config import DB_CONFIG


def init_advanced_objects():
    """一键创建所有教学演示用的高级数据库对象。

    建议先运行 init_data.py，保证 dbsample 已经是干净的 16 表状态。
    """
    db = Database(**DB_CONFIG)

    if not db.connect():
        print("数据库连接失败，请检查配置")
        return

    print("\n" + "=" * 60)
    print("     📚 开始初始化高级数据库对象 (DB05)")
    print("=" * 60)

    # 1. 视图：把常用多表查询保存成虚拟表，便于应用层直接查询。
    print("\n--- 1. 创建视图 ---")
    db.create_view_student_scores()
    db.create_view_course_stats()

    # 2. 触发器：在 INSERT/UPDATE 成绩时自动检查 Score 范围。
    print("\n--- 2. 创建触发器 ---")
    db.create_trigger_score_check()

    # 3. 存储过程：把排名、及格率等数据处理逻辑保存在数据库端。
    print("\n--- 3. 创建存储过程 ---")
    db.create_proc_student_rank()
    db.create_proc_course_pass_rate()

    # 4. 函数：把成绩等级等表达式逻辑封装成可复用函数。
    print("\n--- 4. 创建函数 ---")
    db.create_func_grade_level()

    # 5. 演示：调用刚创建的过程和函数，让学生看到运行结果。
    print("\n--- 5. 存储过程调用演示 ---")
    db.call_proc_student_rank(1)  # 学生AID=1
    db.call_proc_course_pass_rate(1)  # 课程AID=1

    print("\n--- 6. 函数调用演示 ---")
    db.call_func_grade_level(85)
    db.call_func_grade_level(92)
    db.call_func_grade_level(55)

    print("\n--- 7. 约束查看演示 ---")
    for tn in ['student', 'course', 'student_course']:
        print(f"【{tn} 表约束】")
        for c in db.show_table_constraints(tn):
            print(f"  - {c['CONSTRAINT_NAME']} ({c['CONSTRAINT_TYPE']})")

    print("\n" + "=" * 60)
    print("     ✅ 高级数据库对象初始化完成！")
    print("=" * 60)
    print("\n提示：请在主程序 main.py 的菜单 25~29 中交互式管理这些对象。")

    db.close()


if __name__ == "__main__":
    init_advanced_objects()
