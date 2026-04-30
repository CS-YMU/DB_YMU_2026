from models import SportsMeet, Event, Referee, Athlete, RefereeAssignment, Participation
from database import Database


class SportsMeetSystem:
    """运动会管理系统 CLI"""

    def __init__(self, host='localhost', database='sports_meet_db', user='dylan', password='P@ssw0rd'):
        self.db = Database(host, database, user, password)

    def show_menu(self):
        print("\n" + "=" * 55)
        print("               🏃 运动会管理系统")
        print("=" * 55)
        print("  【运动会管理】")
        print("  1. 添加运动会")
        print("  2. 查看所有运动会")
        print("  3. 搜索运动会")
        print("  4. 修改运动会信息")
        print("  5. 删除运动会")
        print()
        print("  【竞赛项目管理】")
        print("  6. 添加竞赛项目")
        print("  7. 查看所有竞赛项目")
        print("  8. 搜索竞赛项目")
        print("  9. 修改竞赛项目信息")
        print("  10. 删除竞赛项目")
        print()
        print("  【裁判管理】")
        print("  11. 添加裁判")
        print("  12. 查看所有裁判")
        print("  13. 搜索裁判")
        print("  14. 修改裁判信息")
        print("  15. 删除裁判")
        print()
        print("  【运动员管理】")
        print("  16. 添加运动员")
        print("  17. 查看所有运动员")
        print("  18. 搜索运动员")
        print("  19. 修改运动员信息")
        print("  20. 删除运动员")
        print("  21. 管理运动员联系电话")
        print()
        print("  【执裁管理】")
        print("  22. 分配裁判到项目")
        print("  23. 查看项目裁判")
        print("  24. 查看裁判执裁项目")
        print("  25. 解除执裁关系")
        print()
        print("  【参赛管理】")
        print("  26. 运动员报名")
        print("  27. 查看项目参赛运动员")
        print("  28. 查看运动员参赛项目")
        print("  29. 录入/修改成绩")
        print("  30. 运动员退赛")
        print()
        print("  【成绩统计】")
        print("  31. 查看项目成绩排名")
        print("  32. 查看破纪录情况")
        print("  33. 运动员参赛统计")
        print()
        print("  0. 退出系统")
        print("=" * 55)

    # ==================== 运动会管理 ====================

    def add_sports_meet_ui(self):
        print("\n--- 添加运动会 ---")
        meet_id = input("请输入届次编号：").strip()
        name = input("请输入名称：").strip()
        date = input("请输入举办日期（YYYY-MM-DD）：").strip()
        location = input("请输入举办地点：").strip()
        meet = SportsMeet(meet_id, name, date, location)
        self.db.add_sports_meet(meet)

    def view_all_sports_meets(self):
        print("\n--- 所有运动会 ---")
        meets = self.db.get_all_sports_meets()
        if meets:
            print(f"{'届次编号':<12} {'名称':<20} {'日期':<12} {'地点':<15}")
            print("-" * 65)
            for m in meets:
                print(f"{m['meet_id']:<12} {m['name']:<20} {str(m['meet_date']):<12} {m['location'] or '':<15}")
            print(f"\n共 {len(meets)} 届")
        else:
            print("暂无运动会信息")

    def search_sports_meet_ui(self):
        print("\n--- 搜索运动会 ---")
        keyword = input("请输入届次编号或名称关键词：").strip()
        results = self.db.search_sports_meet(keyword)
        if results:
            for m in results:
                print(f"届次：{m['meet_id']} | {m['name']} | {m['meet_date']} | {m['location']}")
        else:
            print("未找到匹配的运动会")

    def update_sports_meet_ui(self):
        print("\n--- 修改运动会信息 ---")
        meet_id = input("请输入届次编号：").strip()
        if not self.db.sports_meet_exists(meet_id):
            print("届次编号不存在")
            return
        print("请输入新的信息（直接回车保持原值）：")
        name = input("名称：").strip()
        date = input("举办日期（YYYY-MM-DD）：").strip()
        location = input("举办地点：").strip()

        original = self.db.search_sports_meet(meet_id)[0]
        data = {
            'name': name or original['name'],
            'date': date or original['meet_date'],
            'location': location or original['location']
        }
        self.db.update_sports_meet(meet_id, data)

    def delete_sports_meet_ui(self):
        print("\n--- 删除运动会 ---")
        meet_id = input("请输入届次编号：").strip()
        if not self.db.sports_meet_exists(meet_id):
            print("届次编号不存在")
            return
        confirm = input("确认删除？请输入 'yes'：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_sports_meet(meet_id)

    # ==================== 竞赛项目管理 ====================

    def add_event_ui(self):
        print("\n--- 添加竞赛项目 ---")
        event_id = input("请输入项目编号：").strip()
        event_name = input("请输入项目名称：").strip()

        print("项目类别：1.田赛 2.径赛 3.团体")
        cat_map = {'1': '田赛', '2': '径赛', '3': '团体'}
        category = cat_map.get(input("请选择（1/2/3）：").strip(), '田赛')

        is_team = input("是否团体项目？（y/n）：").strip().lower() == 'y'

        meets = self.db.get_all_sports_meets()
        if not meets:
            print("暂无运动会，请先添加")
            return
        print("\n可选运动会：")
        for m in meets:
            print(f"  {m['meet_id']} - {m['name']}")
        meet_id = input("请输入所属运动会届次编号：").strip()
        if not self.db.sports_meet_exists(meet_id):
            print("届次编号不存在")
            return

        event = Event(event_id, event_name, category, is_team, meet_id)
        self.db.add_event(event)

    def view_all_events(self):
        print("\n--- 所有竞赛项目 ---")
        events = self.db.get_all_events()
        if events:
            print(f"{'项目号':<10} {'项目名':<18} {'类别':<6} {'团体':<4} {'所属运动会':<15}")
            print("-" * 60)
            for e in events:
                team_str = "是" if e['is_team'] else "否"
                print(f"{e['event_id']:<10} {e['event_name']:<18} {e['category']:<6} {team_str:<4} {e['meet_name']:<15}")
            print(f"\n共 {len(events)} 个项目")
        else:
            print("暂无竞赛项目")

    def search_event_ui(self):
        print("\n--- 搜索竞赛项目 ---")
        keyword = input("请输入项目编号或名称关键词：").strip()
        results = self.db.search_event(keyword)
        if results:
            for e in results:
                print(f"{e['event_id']} | {e['event_name']} | {e['category']} | 运动会：{e['meet_name']}")
        else:
            print("未找到匹配的竞赛项目")

    def update_event_ui(self):
        print("\n--- 修改竞赛项目信息 ---")
        event_id = input("请输入项目编号：").strip()
        if not self.db.event_exists(event_id):
            print("项目编号不存在")
            return
        print("请输入新的信息（直接回车保持原值）：")
        event_name = input("项目名称：").strip()

        print("项目类别：1.田赛 2.径赛 3.团体")
        cat_input = input("请选择（1/2/3，直接回车保持原值）：").strip()
        cat_map = {'1': '田赛', '2': '径赛', '3': '团体'}
        category = cat_map.get(cat_input) if cat_input else None

        team_input = input("是否团体项目？（y/n，直接回车保持原值）：").strip()
        is_team = {'y': True, 'n': False}.get(team_input.lower()) if team_input else None

        meet_id = input("所属运动会届次编号（直接回车保持原值）：").strip()
        if meet_id and not self.db.sports_meet_exists(meet_id):
            print("届次编号不存在")
            return

        # 获取原值填充未修改字段
        original = self.db.search_event(event_id)[0] if self.db.search_event(event_id) else None
        if not original:
            print("获取原信息失败")
            return

        data = {
            'event_name': event_name or original['event_name'],
            'category': category or original['category'],
            'is_team': is_team if is_team is not None else original['is_team'],
            'meet_id': meet_id or original['meet_id']
        }
        self.db.update_event(event_id, data)

    def delete_event_ui(self):
        print("\n--- 删除竞赛项目 ---")
        event_id = input("请输入项目编号：").strip()
        if not self.db.event_exists(event_id):
            print("项目编号不存在")
            return
        confirm = input("确认删除？请输入 'yes'：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_event(event_id)

    # ==================== 裁判管理 ====================

    def add_referee_ui(self):
        print("\n--- 添加裁判 ---")
        referee_id = input("请输入裁判编号：").strip()
        name = input("请输入姓名：").strip()
        level = input("请输入裁判等级（国家级/一级/二级）：").strip()
        referee = Referee(referee_id, name, level)
        self.db.add_referee(referee)

    def view_all_referees(self):
        print("\n--- 所有裁判 ---")
        referees = self.db.get_all_referees()
        if referees:
            print(f"{'裁判编号':<12} {'姓名':<10} {'等级':<10}")
            print("-" * 35)
            for r in referees:
                print(f"{r['referee_id']:<12} {r['name']:<10} {r['level']:<10}")
            print(f"\n共 {len(referees)} 位裁判")
        else:
            print("暂无裁判")

    def search_referee_ui(self):
        print("\n--- 搜索裁判 ---")
        keyword = input("请输入裁判编号或姓名关键词：").strip()
        results = self.db.search_referee(keyword)
        if results:
            for r in results:
                print(f"{r['referee_id']} | {r['name']} | {r['level']}")
        else:
            print("未找到匹配的裁判")

    def update_referee_ui(self):
        print("\n--- 修改裁判信息 ---")
        referee_id = input("请输入裁判编号：").strip()
        if not self.db.referee_exists(referee_id):
            print("裁判编号不存在")
            return
        print("请输入新的信息（直接回车保持原值）：")
        name = input("姓名：").strip()
        level = input("裁判等级：").strip()

        original = self.db.search_referee(referee_id)[0] if self.db.search_referee(referee_id) else None
        if not original:
            print("获取原信息失败")
            return

        data = {'name': name or original['name'], 'level': level or original['level']}
        self.db.update_referee(referee_id, data)

    def delete_referee_ui(self):
        print("\n--- 删除裁判 ---")
        referee_id = input("请输入裁判编号：").strip()
        if not self.db.referee_exists(referee_id):
            print("裁判编号不存在")
            return
        confirm = input("确认删除？请输入 'yes'：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_referee(referee_id)

    # ==================== 运动员管理 ====================

    def add_athlete_ui(self):
        print("\n--- 添加运动员 ---")
        athlete_id = input("请输入运动员编号：").strip()
        name = input("请输入姓名：").strip()
        gender = input("请输入性别（男/女）：").strip()
        college = input("请输入所属学院：").strip()
        athlete = Athlete(athlete_id, name, gender, college)
        self.db.add_athlete(athlete)

    def view_all_athletes(self):
        print("\n--- 所有运动员 ---")
        athletes = self.db.get_all_athletes()
        if athletes:
            print(f"{'运动员编号':<12} {'姓名':<10} {'性别':<6} {'学院':<15}")
            print("-" * 50)
            for a in athletes:
                print(f"{a['athlete_id']:<12} {a['name']:<10} {a['gender']:<6} {a['college']:<15}")
            print(f"\n共 {len(athletes)} 位运动员")
        else:
            print("暂无运动员")

    def search_athlete_ui(self):
        print("\n--- 搜索运动员 ---")
        keyword = input("请输入运动员编号或姓名关键词：").strip()
        results = self.db.search_athlete(keyword)
        if results:
            for a in results:
                print(f"{a['athlete_id']} | {a['name']} | {a['gender']} | {a['college']}")
        else:
            print("未找到匹配的运动员")

    def update_athlete_ui(self):
        print("\n--- 修改运动员信息 ---")
        athlete_id = input("请输入运动员编号：").strip()
        if not self.db.athlete_exists(athlete_id):
            print("运动员编号不存在")
            return
        print("请输入新的信息（直接回车保持原值）：")
        name = input("姓名：").strip()
        gender = input("性别（男/女）：").strip()
        college = input("所属学院：").strip()

        original = self.db.search_athlete(athlete_id)[0] if self.db.search_athlete(athlete_id) else None
        if not original:
            print("获取原信息失败")
            return

        data = {
            'name': name or original['name'],
            'gender': gender or original['gender'],
            'college': college or original['college']
        }
        self.db.update_athlete(athlete_id, data)

    def delete_athlete_ui(self):
        print("\n--- 删除运动员 ---")
        athlete_id = input("请输入运动员编号：").strip()
        if not self.db.athlete_exists(athlete_id):
            print("运动员编号不存在")
            return
        confirm = input("确认删除？请输入 'yes'：").strip()
        if confirm.lower() == 'yes':
            self.db.delete_athlete(athlete_id)

    def manage_athlete_phone_ui(self):
        print("\n--- 管理运动员联系电话 ---")
        athlete_id = input("请输入运动员编号：").strip()
        if not self.db.athlete_exists(athlete_id):
            print("运动员编号不存在")
            return

        while True:
            print("\n1. 添加电话")
            print("2. 查看所有电话")
            print("3. 删除电话")
            print("0. 返回")
            choice = input("请选择：").strip()

            if choice == '1':
                phone = input("请输入电话号码：").strip()
                self.db.add_athlete_phone(athlete_id, phone)
            elif choice == '2':
                phones = self.db.get_athlete_phones(athlete_id)
                if phones:
                    print(f"\n运动员 {athlete_id} 的联系电话：")
                    for p in phones:
                        print(f"  {p['phone']}")
                else:
                    print("暂无联系电话")
            elif choice == '3':
                phone = input("请输入要删除的电话号码：").strip()
                self.db.delete_athlete_phone(athlete_id, phone)
            elif choice == '0':
                break
            else:
                print("无效选择")

    # ==================== 执裁管理 ====================

    def assign_referee_ui(self):
        print("\n--- 分配裁判到项目 ---")
        referee_id = input("请输入裁判编号：").strip()
        if not self.db.referee_exists(referee_id):
            print("裁判编号不存在")
            return
        event_id = input("请输入项目编号：").strip()
        if not self.db.event_exists(event_id):
            print("项目编号不存在")
            return
        role = input("请输入职务（主裁判/计时裁判/发令裁判等）：").strip()
        assignment = RefereeAssignment(referee_id, event_id, role)
        self.db.assign_referee(assignment)

    def view_referees_by_event_ui(self):
        print("\n--- 查看项目裁判 ---")
        event_id = input("请输入项目编号：").strip()
        if not self.db.event_exists(event_id):
            print("项目编号不存在")
            return
        referees = self.db.get_referees_by_event(event_id)
        if referees:
            print(f"\n项目 {event_id} 的执裁裁判：")
            print(f"{'裁判编号':<12} {'姓名':<10} {'等级':<10} {'职务':<10}")
            print("-" * 45)
            for r in referees:
                print(f"{r['referee_id']:<12} {r['referee_name']:<10} {r['level']:<10} {r['role']:<10}")
        else:
            print("暂无执裁裁判")

    def view_events_by_referee_ui(self):
        print("\n--- 查看裁判执裁项目 ---")
        referee_id = input("请输入裁判编号：").strip()
        if not self.db.referee_exists(referee_id):
            print("裁判编号不存在")
            return
        events = self.db.get_events_by_referee(referee_id)
        if events:
            print(f"\n裁判 {referee_id} 执裁的项目：")
            print(f"{'项目号':<10} {'项目名':<18} {'类别':<6} {'职务':<10} {'运动会':<15}")
            print("-" * 65)
            for e in events:
                print(f"{e['event_id']:<10} {e['event_name']:<18} {e['category']:<6} {e['role']:<10} {e['meet_name']:<15}")
        else:
            print("暂无执裁项目")

    def unassign_referee_ui(self):
        print("\n--- 解除执裁关系 ---")
        referee_id = input("请输入裁判编号：").strip()
        event_id = input("请输入项目编号：").strip()
        self.db.unassign_referee(referee_id, event_id)

    # ==================== 参赛管理 ====================

    def register_athlete_ui(self):
        print("\n--- 运动员报名 ---")
        athlete_id = input("请输入运动员编号：").strip()
        if not self.db.athlete_exists(athlete_id):
            print("运动员编号不存在，请先添加运动员")
            return
        event_id = input("请输入项目编号：").strip()
        if not self.db.event_exists(event_id):
            print("项目编号不存在")
            return
        participation = Participation(athlete_id, event_id)
        self.db.register_athlete(participation)

    def view_participants_by_event_ui(self):
        print("\n--- 查看项目参赛运动员 ---")
        event_id = input("请输入项目编号：").strip()
        if not self.db.event_exists(event_id):
            print("项目编号不存在")
            return
        participants = self.db.get_participants_by_event(event_id)
        if participants:
            print(f"\n项目 {event_id} 的参赛运动员：")
            print(f"{'运动员编号':<12} {'姓名':<10} {'学院':<12} {'成绩':<10} {'名次':<6} {'破纪录':<6}")
            print("-" * 60)
            for p in participants:
                score_str = str(p['score']) if p['score'] is not None else "未录入"
                rank_str = str(p['rank_num']) if p['rank_num'] else "-"
                record_str = "是" if p['is_record'] else "否"
                print(f"{p['athlete_id']:<12} {p['athlete_name']:<10} {p['college']:<12} {score_str:<10} {rank_str:<6} {record_str:<6}")
        else:
            print("暂无参赛运动员")

    def view_events_by_athlete_ui(self):
        print("\n--- 查看运动员参赛项目 ---")
        athlete_id = input("请输入运动员编号：").strip()
        if not self.db.athlete_exists(athlete_id):
            print("运动员编号不存在")
            return
        events = self.db.get_events_by_athlete(athlete_id)
        if events:
            print(f"\n运动员 {athlete_id} 参加的项目：")
            print(f"{'项目号':<10} {'项目名':<18} {'类别':<6} {'成绩':<10} {'名次':<6} {'运动会':<15}")
            print("-" * 70)
            for e in events:
                score_str = str(e['score']) if e['score'] is not None else "未录入"
                rank_str = str(e['rank_num']) if e['rank_num'] else "-"
                print(f"{e['event_id']:<10} {e['event_name']:<18} {e['category']:<6} {score_str:<10} {rank_str:<6} {e['meet_name']:<15}")
        else:
            print("暂无参赛记录")

    def update_score_ui(self):
        print("\n--- 录入/修改成绩 ---")
        athlete_id = input("请输入运动员编号：").strip()
        event_id = input("请输入项目编号：").strip()

        # 检查参赛记录是否存在
        events = self.db.get_events_by_athlete(athlete_id)
        found = any(e['event_id'] == event_id for e in events)
        if not found:
            print("未找到该参赛记录")
            return

        score_input = input("请输入成绩（数值，如12.5）：").strip()
        score = float(score_input) if score_input else None
        rank_input = input("请输入名次（整数）：").strip()
        rank = int(rank_input) if rank_input else None
        is_record = input("是否破纪录？（y/n）：").strip().lower() == 'y'

        self.db.update_score(athlete_id, event_id, score, rank, is_record)

    def unregister_athlete_ui(self):
        print("\n--- 运动员退赛 ---")
        athlete_id = input("请输入运动员编号：").strip()
        event_id = input("请输入项目编号：").strip()
        confirm = input("确认退赛？请输入 'yes'：").strip()
        if confirm.lower() == 'yes':
            self.db.unregister_athlete(athlete_id, event_id)

    # ==================== 成绩统计 ====================

    def view_event_rankings_ui(self):
        print("\n--- 查看项目成绩排名 ---")
        event_id = input("请输入项目编号：").strip()
        if not self.db.event_exists(event_id):
            print("项目编号不存在")
            return
        rankings = self.db.get_event_rankings(event_id)
        if rankings:
            print(f"\n项目 {event_id} 成绩排名：")
            print(f"{'名次':<6} {'运动员编号':<12} {'姓名':<10} {'学院':<12} {'成绩':<10} {'破纪录':<6}")
            print("-" * 60)
            for i, r in enumerate(rankings, 1):
                record_str = "是" if r['is_record'] else "否"
                print(f"{i:<6} {r['athlete_id']:<12} {r['athlete_name']:<10} {r['college']:<12} {r['score']:<10} {record_str:<6}")
        else:
            print("暂无成绩记录")

    def view_record_breakers_ui(self):
        print("\n--- 查看破纪录情况 ---")
        records = self.db.get_record_breakers()
        if records:
            print(f"{'运动员':<10} {'姓名':<10} {'项目':<15} {'成绩':<10}")
            print("-" * 50)
            for r in records:
                print(f"{r['athlete_id']:<10} {r['athlete_name']:<10} {r['event_name']:<15} {r['score']:<10}")
        else:
            print("暂无破纪录情况")

    def view_athlete_stats_ui(self):
        print("\n--- 运动员参赛统计 ---")
        athlete_id = input("请输入运动员编号：").strip()
        if not self.db.athlete_exists(athlete_id):
            print("运动员编号不存在")
            return
        stats = self.db.get_athlete_stats(athlete_id)
        if stats:
            print(f"\n运动员 {athlete_id} 的参赛统计：")
            print(f"  报名项目数：{stats['total_events']}")
            print(f"  已完成项目：{stats['completed']}")
            print(f"  平均成绩：{round(stats['avg_score'], 2) if stats['avg_score'] else 'N/A'}")
            print(f"  破纪录次数：{stats['records'] or 0}")

    # ==================== 主循环 ====================

    def run(self):
        print("\n" + "=" * 55)
        print("        🏃 欢迎使用运动会管理系统 🏃")
        print("=" * 55)

        if not self.db.connect():
            print("无法启动系统：数据库连接失败")
            return

        self.db.create_tables()

        while True:
            self.show_menu()
            choice = input("请选择操作（输入数字）：").strip()

            handlers = {
                '1': self.add_sports_meet_ui,
                '2': self.view_all_sports_meets,
                '3': self.search_sports_meet_ui,
                '4': self.update_sports_meet_ui,
                '5': self.delete_sports_meet_ui,
                '6': self.add_event_ui,
                '7': self.view_all_events,
                '8': self.search_event_ui,
                '9': self.update_event_ui,
                '10': self.delete_event_ui,
                '11': self.add_referee_ui,
                '12': self.view_all_referees,
                '13': self.search_referee_ui,
                '14': self.update_referee_ui,
                '15': self.delete_referee_ui,
                '16': self.add_athlete_ui,
                '17': self.view_all_athletes,
                '18': self.search_athlete_ui,
                '19': self.update_athlete_ui,
                '20': self.delete_athlete_ui,
                '21': self.manage_athlete_phone_ui,
                '22': self.assign_referee_ui,
                '23': self.view_referees_by_event_ui,
                '24': self.view_events_by_referee_ui,
                '25': self.unassign_referee_ui,
                '26': self.register_athlete_ui,
                '27': self.view_participants_by_event_ui,
                '28': self.view_events_by_athlete_ui,
                '29': self.update_score_ui,
                '30': self.unregister_athlete_ui,
                '31': self.view_event_rankings_ui,
                '32': self.view_record_breakers_ui,
                '33': self.view_athlete_stats_ui,
            }

            if choice == '0':
                print("\n感谢使用运动会管理系统，再见！")
                self.db.close()
                break
            elif choice in handlers:
                handlers[choice]()
            else:
                print("无效选择，请重新输入")

            input("\n按回车键继续...")


if __name__ == "__main__":
    system = SportsMeetSystem(
        host='localhost',
        database='sports_meet_db',
        user='dylan',
        password='P@ssw0rd'
    )
    system.run()
