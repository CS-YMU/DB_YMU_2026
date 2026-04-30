"""运动会管理系统 —— 初始化测试数据"""
from models import SportsMeet, Event, Referee, Athlete, RefereeAssignment, Participation
from database import Database

DB_CONFIG = {
    'host': 'localhost',
    'database': 'sports_meet_db',
    'user': 'dylan',
    'password': 'P@ssw0rd'
}


def init_data():
    db = Database(**DB_CONFIG)
    if not db.connect():
        print("数据库连接失败")
        return

    # 清理旧数据
    print("\n--- 清理旧数据 ---")
    try:
        db.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        db.cursor.execute("DROP TABLE IF EXISTS participation")
        db.cursor.execute("DROP TABLE IF EXISTS referee_event")
        db.cursor.execute("DROP TABLE IF EXISTS athlete_phone")
        db.cursor.execute("DROP TABLE IF EXISTS athlete")
        db.cursor.execute("DROP TABLE IF EXISTS referee")
        db.cursor.execute("DROP TABLE IF EXISTS event")
        db.cursor.execute("DROP TABLE IF EXISTS sports_meet")
        db.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        db.connection.commit()
        print("旧数据已清理")
    except Exception as e:
        print(f"清理失败：{e}")
        db.close()
        return

    # 创建表
    db.create_tables()

    # ==================== 运动会 ====================
    print("\n--- 添加运动会 ---")
    meets = [
        SportsMeet('M2024', '第46届田径运动会', '2024-10-15', '学校田径场'),
        SportsMeet('M2025', '第47届田径运动会', '2025-10-20', '学校田径场'),
    ]
    for m in meets:
        db.add_sports_meet(m)

    # ==================== 竞赛项目 ====================
    print("\n--- 添加竞赛项目 ---")
    events = [
        Event('E001', '男子100米', '径赛', False, 'M2025'),
        Event('E002', '男子200米', '径赛', False, 'M2025'),
        Event('E003', '女子100米', '径赛', False, 'M2025'),
        Event('E004', '女子跳远', '田赛', False, 'M2025'),
        Event('E005', '男子铅球', '田赛', False, 'M2025'),
        Event('E006', '4x100米接力', '径赛', True, 'M2025'),
        Event('E007', '拔河比赛', '团体', True, 'M2025'),
    ]
    for e in events:
        db.add_event(e)

    # ==================== 裁判 ====================
    print("\n--- 添加裁判 ---")
    referees = [
        Referee('R001', '王裁判', '国家级'),
        Referee('R002', '李裁判', '一级'),
        Referee('R003', '张裁判', '一级'),
        Referee('R004', '刘裁判', '二级'),
        Referee('R005', '陈裁判', '国家级'),
    ]
    for r in referees:
        db.add_referee(r)

    # ==================== 运动员 ====================
    print("\n--- 添加运动员 ---")
    athletes = [
        Athlete('A001', '张三', '男', '计算机学院'),
        Athlete('A002', '李四', '男', '软件学院'),
        Athlete('A003', '王五', '男', '电子信息学院'),
        Athlete('A004', '赵六', '女', '计算机学院'),
        Athlete('A005', '孙七', '女', '管理学院'),
        Athlete('A006', '周八', '男', '机械学院'),
        Athlete('A007', '吴九', '女', '外国语学院'),
        Athlete('A008', '郑十', '男', '土木学院'),
    ]
    for a in athletes:
        db.add_athlete(a)

    # ==================== 运动员联系电话（多值属性）====================
    print("\n--- 添加运动员联系电话 ---")
    phones = {
        'A001': ['13800138001', '13900139001'],
        'A002': ['13800138002'],
        'A003': ['13800138003', '13600136003'],
        'A004': ['13800138004'],
        'A005': ['13800138005', '13700137005'],
    }
    for athlete_id, phone_list in phones.items():
        for phone in phone_list:
            db.add_athlete_phone(athlete_id, phone)

    # ==================== 执裁关系（裁判-项目 M:N）====================
    print("\n--- 分配裁判 ---")
    assignments = [
        RefereeAssignment('R001', 'E001', '主裁判'),
        RefereeAssignment('R002', 'E001', '计时裁判'),
        RefereeAssignment('R001', 'E002', '主裁判'),
        RefereeAssignment('R003', 'E003', '主裁判'),
        RefereeAssignment('R004', 'E004', '主裁判'),
        RefereeAssignment('R002', 'E005', '主裁判'),
        RefereeAssignment('R005', 'E006', '主裁判'),
        RefereeAssignment('R003', 'E006', '计时裁判'),
        RefereeAssignment('R005', 'E007', '主裁判'),
    ]
    for a in assignments:
        db.assign_referee(a)

    # ==================== 参赛关系（运动员-项目 M:N）====================
    print("\n--- 运动员报名 ---")
    participations = [
        Participation('A001', 'E001'),  # 张三 - 男子100米
        Participation('A002', 'E001'),  # 李四 - 男子100米
        Participation('A003', 'E001'),  # 王五 - 男子100米
        Participation('A006', 'E001'),  # 周八 - 男子100米
        Participation('A001', 'E002'),  # 张三 - 男子200米
        Participation('A003', 'E002'),  # 王五 - 男子200米
        Participation('A008', 'E002'),  # 郑十 - 男子200米
        Participation('A004', 'E003'),  # 赵六 - 女子100米
        Participation('A005', 'E003'),  # 孙七 - 女子100米
        Participation('A007', 'E003'),  # 吴九 - 女子100米
        Participation('A004', 'E004'),  # 赵六 - 女子跳远
        Participation('A005', 'E004'),  # 孙七 - 女子跳远
        Participation('A002', 'E005'),  # 李四 - 男子铅球
        Participation('A006', 'E005'),  # 周八 - 男子铅球
        Participation('A008', 'E005'),  # 郑十 - 男子铅球
    ]
    for p in participations:
        db.register_athlete(p)

    # ==================== 录入成绩 ====================
    print("\n--- 录入成绩 ---")
    scores = [
        # 男子100米 (E001) - 径赛，成绩越小越好
        ('A001', 'E001', 10.85, 2, False),
        ('A002', 'E001', 11.20, 3, False),
        ('A003', 'E001', 10.52, 1, True),   # 破纪录！
        ('A006', 'E001', 11.45, 4, False),
        # 男子200米 (E002)
        ('A001', 'E002', 21.80, 1, False),
        ('A003', 'E002', 22.15, 2, False),
        ('A008', 'E002', 22.60, 3, False),
        # 女子100米 (E003)
        ('A004', 'E003', 12.35, 1, True),   # 破纪录！
        ('A005', 'E003', 12.80, 2, False),
        ('A007', 'E003', 13.10, 3, False),
        # 女子跳远 (E004) - 田赛，成绩越大越好
        ('A004', 'E004', 5.68, 1, False),
        ('A005', 'E004', 5.42, 2, False),
        # 男子铅球 (E005) - 田赛，成绩越大越好
        ('A002', 'E005', 12.50, 2, False),
        ('A006', 'E005', 13.20, 1, True),   # 破纪录！
        ('A008', 'E005', 11.80, 3, False),
    ]
    for athlete_id, event_id, score, rank, is_record in scores:
        db.update_score(athlete_id, event_id, score, rank, is_record)

    # ==================== 显示统计 ====================
    print("\n" + "=" * 50)
    print("           初始化数据统计")
    print("=" * 50)
    print(f"运动会总数：{len(meets)}")
    print(f"竞赛项目总数：{len(events)}")
    print(f"裁判总数：{len(referees)}")
    print(f"运动员总数：{len(athletes)}")
    print(f"执裁关系总数：{len(assignments)}")
    print(f"参赛记录总数：{len(participations)}")

    print("\n--- 各项目成绩排名 ---")
    for e in events[:5]:
        rankings = db.get_event_rankings(e.event_id)
        if rankings:
            print(f"\n{e.event_name}：")
            for r in rankings:
                record_mark = " [破纪录]" if r['is_record'] else ""
                print(f"  第{r['rank_num']}名 {r['athlete_name']}({r['athlete_id']}) - {r['score']}{record_mark}")

    print("\n--- 破纪录运动员 ---")
    records = db.get_record_breakers()
    for r in records:
        print(f"  {r['athlete_name']} - {r['event_name']} - {r['score']}")

    print("\n测试数据初始化完成！")
    db.close()


if __name__ == "__main__":
    init_data()
