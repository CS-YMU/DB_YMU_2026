"""
高级数据库对象初始化与演示脚本
用于课堂教学演示：视图、触发器、存储过程、函数、完整性约束
"""
from database import Database

# 数据库连接配置（与主程序保持一致）
DB_CONFIG = {
    'host': 'localhost',
    'database': 'student_db',
    'user': 'dylan',
    'password': 'P@ssw0rd'
}


def init_advanced_objects():
    """一键创建所有教学演示用的高级数据库对象"""
    db = Database(**DB_CONFIG)

    if not db.connect():
        print("数据库连接失败，请检查配置")
        return

    print("\n" + "=" * 60)
    print("     📚 开始初始化高级数据库对象（教学演示版）")
    print("=" * 60)

    # ==================== 1. 视图（View）演示 ====================
    # 视图是虚拟表，不存储实际数据，基于 SELECT 查询动态生成结果集
    print("\n--- 1. 创建视图 ---")
    db.create_view_student_scores()      # 学生成绩明细视图
    db.create_view_course_stats()        # 课程统计视图

    # ==================== 2. 触发器（Trigger）演示 ====================
    # 触发器在特定事件（INSERT/UPDATE/DELETE）发生时自动执行
    print("\n--- 2. 创建触发器 ---")
    db.create_trigger_score_check()         # BEFORE 触发器：成绩范围检查
    db.create_trigger_student_delete_log()  # AFTER 触发器：删除学生日志

    # ==================== 3. 存储过程（Stored Procedure）演示 ====================
    # 存储过程是预编译的 SQL 程序，可接收参数并在服务端执行复杂逻辑
    print("\n--- 3. 创建存储过程 ---")
    db.create_proc_student_rank()       # 学生平均成绩排名
    db.create_proc_course_pass_rate()   # 课程及格率统计

    # ==================== 4. 函数（Function）演示 ====================
    # 自定义函数像内置函数一样可在 SELECT 中调用，返回单个值
    print("\n--- 4. 创建函数 ---")
    db.create_func_grade_level()        # 成绩等级转换函数

    # ==================== 5. 快速调用演示 ====================
    print("\n--- 5. 存储过程调用演示 ---")
    db.call_proc_student_rank('2024001')
    db.call_proc_course_pass_rate('CS101')

    print("\n--- 6. 函数调用演示 ---")
    db.call_func_grade_level(85)
    db.call_func_grade_level(92)
    db.call_func_grade_level(55)

    print("\n--- 7. 约束查看演示 ---")
    print("【students 表约束】")
    for c in db.show_table_constraints('students'):
        print(f"  - {c['CONSTRAINT_NAME']} ({c['CONSTRAINT_TYPE']})")

    print("【course 表约束】")
    for c in db.show_table_constraints('course'):
        print(f"  - {c['CONSTRAINT_NAME']} ({c['CONSTRAINT_TYPE']})")

    print("【sc 表约束】")
    for c in db.show_table_constraints('sc'):
        print(f"  - {c['CONSTRAINT_NAME']} ({c['CONSTRAINT_TYPE']})")

    print("\n" + "=" * 60)
    print("     ✅ 高级数据库对象初始化完成！")
    print("=" * 60)
    print("\n提示：请在主程序 main.py 的菜单 18~22 中交互式管理这些对象。")

    db.close()


if __name__ == "__main__":
    init_advanced_objects()
