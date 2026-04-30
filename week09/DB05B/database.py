import mysql.connector
from mysql.connector import Error


class Database:
    """数据库操作类"""

    def __init__(self, host, database, user, password):
        self.connection_config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        self.connection = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.connection_config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("数据库连接成功")
            return True
        except Error as e:
            print(f"数据库连接失败：{e}")
            return False

    def create_tables(self):
        """创建所有数据表"""
        # 运动会表
        create_sports_meet = """
        CREATE TABLE IF NOT EXISTS sports_meet (
            meet_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            meet_date DATE NOT NULL,
            location VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 竞赛项目表
        create_event = """
        CREATE TABLE IF NOT EXISTS event (
            event_id VARCHAR(20) PRIMARY KEY,
            event_name VARCHAR(100) NOT NULL UNIQUE,
            category ENUM('田赛', '径赛', '团体') NOT NULL,
            is_team BOOLEAN NOT NULL DEFAULT FALSE,
            meet_id VARCHAR(20) NOT NULL,
            CONSTRAINT fk_event_meet FOREIGN KEY (meet_id)
                REFERENCES sports_meet(meet_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 裁判表
        create_referee = """
        CREATE TABLE IF NOT EXISTS referee (
            referee_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            level VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 运动员表
        create_athlete = """
        CREATE TABLE IF NOT EXISTS athlete (
            athlete_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender ENUM('男', '女') NOT NULL,
            college VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 运动员联系电话表（多值属性）
        create_athlete_phone = """
        CREATE TABLE IF NOT EXISTS athlete_phone (
            athlete_id VARCHAR(20) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            PRIMARY KEY (athlete_id, phone),
            CONSTRAINT fk_phone_athlete FOREIGN KEY (athlete_id)
                REFERENCES athlete(athlete_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 执裁关系表（裁判-竞赛项目，M:N，联系属性：职务）
        create_referee_event = """
        CREATE TABLE IF NOT EXISTS referee_event (
            referee_id VARCHAR(20) NOT NULL,
            event_id VARCHAR(20) NOT NULL,
            role VARCHAR(50) NOT NULL,
            PRIMARY KEY (referee_id, event_id),
            CONSTRAINT fk_re_referee FOREIGN KEY (referee_id)
                REFERENCES referee(referee_id) ON DELETE CASCADE,
            CONSTRAINT fk_re_event FOREIGN KEY (event_id)
                REFERENCES event(event_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        # 参赛关系表（运动员-竞赛项目，M:N，联系属性：成绩、名次、是否破纪录）
        create_participation = """
        CREATE TABLE IF NOT EXISTS participation (
            athlete_id VARCHAR(20) NOT NULL,
            event_id VARCHAR(20) NOT NULL,
            score DECIMAL(10,2) DEFAULT NULL,
            rank_num INT DEFAULT NULL,
            is_record BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (athlete_id, event_id),
            CONSTRAINT fk_pa_athlete FOREIGN KEY (athlete_id)
                REFERENCES athlete(athlete_id) ON DELETE CASCADE,
            CONSTRAINT fk_pa_event FOREIGN KEY (event_id)
                REFERENCES event(event_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        try:
            self.cursor.execute(create_sports_meet)
            self.cursor.execute(create_event)
            self.cursor.execute(create_referee)
            self.cursor.execute(create_athlete)
            self.cursor.execute(create_athlete_phone)
            self.cursor.execute(create_referee_event)
            self.cursor.execute(create_participation)
            self.connection.commit()
            print("数据表创建成功")
        except Error as e:
            print(f"创建表失败：{e}")

    # ==================== 运动会操作 ====================

    def add_sports_meet(self, meet):
        query = "INSERT INTO sports_meet (meet_id, name, meet_date, location) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (meet.meet_id, meet.name, meet.date, meet.location))
            self.connection.commit()
            print(f"运动会 {meet.name} 添加成功")
            return True
        except Error as e:
            print(f"添加失败：{e}")
            return False

    def get_all_sports_meets(self):
        query = "SELECT * FROM sports_meet ORDER BY meet_date DESC"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def search_sports_meet(self, keyword):
        query = "SELECT * FROM sports_meet WHERE meet_id LIKE %s OR name LIKE %s ORDER BY meet_date DESC"
        try:
            self.cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            return self.cursor.fetchall()
        except Error as e:
            print(f"搜索失败：{e}")
            return []

    def update_sports_meet(self, meet_id, data):
        query = "UPDATE sports_meet SET name=%s, meet_date=%s, location=%s WHERE meet_id=%s"
        try:
            self.cursor.execute(query, (data['name'], data['date'], data['location'], meet_id))
            self.connection.commit()
            print("运动会信息更新成功")
            return True
        except Error as e:
            print(f"更新失败：{e}")
            return False

    def delete_sports_meet(self, meet_id):
        query = "DELETE FROM sports_meet WHERE meet_id = %s"
        try:
            self.cursor.execute(query, (meet_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("运动会删除成功（级联删除关联项目和参赛记录）")
                return True
            else:
                print("届次编号不存在")
                return False
        except Error as e:
            print(f"删除失败：{e}")
            return False

    def sports_meet_exists(self, meet_id):
        query = "SELECT 1 FROM sports_meet WHERE meet_id = %s"
        try:
            self.cursor.execute(query, (meet_id,))
            return self.cursor.fetchone() is not None
        except Error:
            return False

    # ==================== 竞赛项目操作 ====================

    def add_event(self, event):
        query = "INSERT INTO event (event_id, event_name, category, is_team, meet_id) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (event.event_id, event.event_name, event.category, event.is_team, event.meet_id))
            self.connection.commit()
            print(f"竞赛项目 {event.event_name} 添加成功")
            return True
        except Error as e:
            print(f"添加失败：{e}")
            return False

    def get_all_events(self):
        query = """
        SELECT e.*, sm.name as meet_name
        FROM event e
        JOIN sports_meet sm ON e.meet_id = sm.meet_id
        ORDER BY e.event_id
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def get_events_by_meet(self, meet_id):
        query = "SELECT * FROM event WHERE meet_id = %s ORDER BY event_id"
        try:
            self.cursor.execute(query, (meet_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def search_event(self, keyword):
        query = """
        SELECT e.*, sm.name as meet_name
        FROM event e
        JOIN sports_meet sm ON e.meet_id = sm.meet_id
        WHERE e.event_id LIKE %s OR e.event_name LIKE %s
        ORDER BY e.event_id
        """
        try:
            self.cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            return self.cursor.fetchall()
        except Error as e:
            print(f"搜索失败：{e}")
            return []

    def update_event(self, event_id, data):
        query = "UPDATE event SET event_name=%s, category=%s, is_team=%s, meet_id=%s WHERE event_id=%s"
        try:
            self.cursor.execute(query, (data['event_name'], data['category'], data['is_team'], data['meet_id'], event_id))
            self.connection.commit()
            print("竞赛项目信息更新成功")
            return True
        except Error as e:
            print(f"更新失败：{e}")
            return False

    def delete_event(self, event_id):
        query = "DELETE FROM event WHERE event_id = %s"
        try:
            self.cursor.execute(query, (event_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("竞赛项目删除成功")
                return True
            else:
                print("项目编号不存在")
                return False
        except Error as e:
            print(f"删除失败：{e}")
            return False

    def event_exists(self, event_id):
        query = "SELECT 1 FROM event WHERE event_id = %s"
        try:
            self.cursor.execute(query, (event_id,))
            return self.cursor.fetchone() is not None
        except Error:
            return False

    # ==================== 裁判操作 ====================

    def add_referee(self, referee):
        query = "INSERT INTO referee (referee_id, name, level) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (referee.referee_id, referee.name, referee.level))
            self.connection.commit()
            print(f"裁判 {referee.name} 添加成功")
            return True
        except Error as e:
            print(f"添加失败：{e}")
            return False

    def get_all_referees(self):
        query = "SELECT * FROM referee ORDER BY referee_id"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def search_referee(self, keyword):
        query = "SELECT * FROM referee WHERE referee_id LIKE %s OR name LIKE %s ORDER BY referee_id"
        try:
            self.cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            return self.cursor.fetchall()
        except Error as e:
            print(f"搜索失败：{e}")
            return []

    def update_referee(self, referee_id, data):
        query = "UPDATE referee SET name=%s, level=%s WHERE referee_id=%s"
        try:
            self.cursor.execute(query, (data['name'], data['level'], referee_id))
            self.connection.commit()
            print("裁判信息更新成功")
            return True
        except Error as e:
            print(f"更新失败：{e}")
            return False

    def delete_referee(self, referee_id):
        query = "DELETE FROM referee WHERE referee_id = %s"
        try:
            self.cursor.execute(query, (referee_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("裁判删除成功")
                return True
            else:
                print("裁判编号不存在")
                return False
        except Error as e:
            print(f"删除失败：{e}")
            return False

    def referee_exists(self, referee_id):
        query = "SELECT 1 FROM referee WHERE referee_id = %s"
        try:
            self.cursor.execute(query, (referee_id,))
            return self.cursor.fetchone() is not None
        except Error:
            return False

    # ==================== 运动员操作 ====================

    def add_athlete(self, athlete):
        query = "INSERT INTO athlete (athlete_id, name, gender, college) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (athlete.athlete_id, athlete.name, athlete.gender, athlete.college))
            self.connection.commit()
            print(f"运动员 {athlete.name} 添加成功")
            return True
        except Error as e:
            print(f"添加失败：{e}")
            return False

    def get_all_athletes(self):
        query = "SELECT * FROM athlete ORDER BY athlete_id"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def search_athlete(self, keyword):
        query = "SELECT * FROM athlete WHERE athlete_id LIKE %s OR name LIKE %s ORDER BY athlete_id"
        try:
            self.cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            return self.cursor.fetchall()
        except Error as e:
            print(f"搜索失败：{e}")
            return []

    def update_athlete(self, athlete_id, data):
        query = "UPDATE athlete SET name=%s, gender=%s, college=%s WHERE athlete_id=%s"
        try:
            self.cursor.execute(query, (data['name'], data['gender'], data['college'], athlete_id))
            self.connection.commit()
            print("运动员信息更新成功")
            return True
        except Error as e:
            print(f"更新失败：{e}")
            return False

    def delete_athlete(self, athlete_id):
        query = "DELETE FROM athlete WHERE athlete_id = %s"
        try:
            self.cursor.execute(query, (athlete_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("运动员删除成功")
                return True
            else:
                print("运动员编号不存在")
                return False
        except Error as e:
            print(f"删除失败：{e}")
            return False

    def athlete_exists(self, athlete_id):
        query = "SELECT 1 FROM athlete WHERE athlete_id = %s"
        try:
            self.cursor.execute(query, (athlete_id,))
            return self.cursor.fetchone() is not None
        except Error:
            return False

    # ==================== 运动员联系电话操作（多值属性）====================

    def add_athlete_phone(self, athlete_id, phone):
        query = "INSERT INTO athlete_phone (athlete_id, phone) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (athlete_id, phone))
            self.connection.commit()
            print(f"联系电话 {phone} 添加成功")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                print("该电话已存在")
            else:
                print(f"添加失败：{e}")
            return False

    def get_athlete_phones(self, athlete_id):
        query = "SELECT phone FROM athlete_phone WHERE athlete_id = %s"
        try:
            self.cursor.execute(query, (athlete_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def delete_athlete_phone(self, athlete_id, phone):
        query = "DELETE FROM athlete_phone WHERE athlete_id = %s AND phone = %s"
        try:
            self.cursor.execute(query, (athlete_id, phone))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("联系电话删除成功")
                return True
            else:
                print("电话不存在")
                return False
        except Error as e:
            print(f"删除失败：{e}")
            return False

    # ==================== 执裁关系操作（裁判-项目 M:N）====================

    def assign_referee(self, assignment):
        query = "INSERT INTO referee_event (referee_id, event_id, role) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (assignment.referee_id, assignment.event_id, assignment.role))
            self.connection.commit()
            print(f"执裁分配成功：裁判 {assignment.referee_id} -> 项目 {assignment.event_id}")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                print("该裁判已分配到此项目")
            else:
                print(f"分配失败：{e}")
            return False

    def get_referees_by_event(self, event_id):
        query = """
        SELECT re.*, r.name as referee_name, r.level
        FROM referee_event re
        JOIN referee r ON re.referee_id = r.referee_id
        WHERE re.event_id = %s
        """
        try:
            self.cursor.execute(query, (event_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def get_events_by_referee(self, referee_id):
        query = """
        SELECT re.*, e.event_name, e.category, sm.name as meet_name
        FROM referee_event re
        JOIN event e ON re.event_id = e.event_id
        JOIN sports_meet sm ON e.meet_id = sm.meet_id
        WHERE re.referee_id = %s
        """
        try:
            self.cursor.execute(query, (referee_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def unassign_referee(self, referee_id, event_id):
        query = "DELETE FROM referee_event WHERE referee_id = %s AND event_id = %s"
        try:
            self.cursor.execute(query, (referee_id, event_id))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("执裁关系解除成功")
                return True
            else:
                print("执裁关系不存在")
                return False
        except Error as e:
            print(f"解除失败：{e}")
            return False

    # ==================== 参赛关系操作（运动员-项目 M:N）====================

    def register_athlete(self, participation):
        query = "INSERT INTO participation (athlete_id, event_id) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (participation.athlete_id, participation.event_id))
            self.connection.commit()
            print(f"报名成功：运动员 {participation.athlete_id} -> 项目 {participation.event_id}")
            return True
        except Error as e:
            if "Duplicate entry" in str(e):
                print("该运动员已报名此项目")
            else:
                print(f"报名失败：{e}")
            return False

    def get_participants_by_event(self, event_id):
        query = """
        SELECT p.*, a.name as athlete_name, a.gender, a.college
        FROM participation p
        JOIN athlete a ON p.athlete_id = a.athlete_id
        WHERE p.event_id = %s
        ORDER BY p.rank_num, p.score
        """
        try:
            self.cursor.execute(query, (event_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def get_events_by_athlete(self, athlete_id):
        query = """
        SELECT p.*, e.event_name, e.category, sm.name as meet_name
        FROM participation p
        JOIN event e ON p.event_id = e.event_id
        JOIN sports_meet sm ON e.meet_id = sm.meet_id
        WHERE p.athlete_id = %s
        """
        try:
            self.cursor.execute(query, (athlete_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def update_score(self, athlete_id, event_id, score, rank, is_record):
        query = "UPDATE participation SET score=%s, rank_num=%s, is_record=%s WHERE athlete_id=%s AND event_id=%s"
        try:
            self.cursor.execute(query, (score, rank, is_record, athlete_id, event_id))
            self.connection.commit()
            print("成绩录入/更新成功")
            return True
        except Error as e:
            print(f"更新失败：{e}")
            return False

    def unregister_athlete(self, athlete_id, event_id):
        query = "DELETE FROM participation WHERE athlete_id = %s AND event_id = %s"
        try:
            self.cursor.execute(query, (athlete_id, event_id))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print("退赛成功")
                return True
            else:
                print("参赛记录不存在")
                return False
        except Error as e:
            print(f"退赛失败：{e}")
            return False

    # ==================== 统计查询 ====================

    def get_event_rankings(self, event_id):
        query = """
        SELECT p.*, a.name as athlete_name, a.college
        FROM participation p
        JOIN athlete a ON p.athlete_id = a.athlete_id
        WHERE p.event_id = %s AND p.score IS NOT NULL
        ORDER BY p.score
        """
        try:
            self.cursor.execute(query, (event_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def get_record_breakers(self):
        query = """
        SELECT p.*, a.name as athlete_name, e.event_name
        FROM participation p
        JOIN athlete a ON p.athlete_id = a.athlete_id
        JOIN event e ON p.event_id = e.event_id
        WHERE p.is_record = TRUE
        ORDER BY e.event_name
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查询失败：{e}")
            return []

    def get_athlete_stats(self, athlete_id):
        query = """
        SELECT COUNT(*) as total_events, COUNT(score) as completed,
               AVG(score) as avg_score, SUM(is_record) as records
        FROM participation WHERE athlete_id = %s
        """
        try:
            self.cursor.execute(query, (athlete_id,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"查询失败：{e}")
            return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
