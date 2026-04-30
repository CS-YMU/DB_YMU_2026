"""运动会管理系统 —— 数据模型"""


class SportsMeet:
    """运动会信息类"""
    def __init__(self, meet_id, name, date, location):
        self.meet_id = meet_id    # 届次编号
        self.name = name          # 名称
        self.date = date          # 举办日期
        self.location = location  # 举办地点

    def __str__(self):
        return f"届次：{self.meet_id} | 名称：{self.name} | 日期：{self.date} | 地点：{self.location}"


class Event:
    """竞赛项目信息类"""
    def __init__(self, event_id, event_name, category, is_team, meet_id):
        self.event_id = event_id      # 项目编号
        self.event_name = event_name  # 项目名称
        self.category = category      # 项目类别（田赛/径赛/团体）
        self.is_team = is_team        # 是否团体项目（True/False）
        self.meet_id = meet_id        # 所属运动会届次编号

    def __str__(self):
        team_str = "是" if self.is_team else "否"
        return f"项目号：{self.event_id} | 名称：{self.event_name} | 类别：{self.category} | 团体：{team_str} | 届次：{self.meet_id}"


class Referee:
    """裁判信息类"""
    def __init__(self, referee_id, name, level):
        self.referee_id = referee_id  # 裁判编号
        self.name = name              # 姓名
        self.level = level            # 裁判等级（国家级/一级/二级）

    def __str__(self):
        return f"裁判编号：{self.referee_id} | 姓名：{self.name} | 等级：{self.level}"


class Athlete:
    """运动员信息类"""
    def __init__(self, athlete_id, name, gender, college):
        self.athlete_id = athlete_id  # 运动员编号
        self.name = name              # 姓名
        self.gender = gender          # 性别
        self.college = college        # 所属学院

    def __str__(self):
        return f"运动员编号：{self.athlete_id} | 姓名：{self.name} | 性别：{self.gender} | 学院：{self.college}"


class RefereeAssignment:
    """裁判执裁关系类（联系实体）"""
    def __init__(self, referee_id, event_id, role):
        self.referee_id = referee_id  # 裁判编号
        self.event_id = event_id      # 项目编号
        self.role = role              # 职务（主裁判/计时裁判等）

    def __str__(self):
        return f"裁判：{self.referee_id} | 项目：{self.event_id} | 职务：{self.role}"


class Participation:
    """参赛关系类（联系实体）"""
    def __init__(self, athlete_id, event_id, score=None, rank=None, is_record=False):
        self.athlete_id = athlete_id  # 运动员编号
        self.event_id = event_id      # 项目编号
        self.score = score            # 参赛成绩
        self.rank = rank              # 名次
        self.is_record = is_record    # 是否破纪录

    def __str__(self):
        score_str = f"{self.score}" if self.score is not None else "未录入"
        rank_str = f"第{self.rank}名" if self.rank else "未排名"
        record_str = "破纪录" if self.is_record else ""
        return f"运动员：{self.athlete_id} | 项目：{self.event_id} | 成绩：{score_str} | {rank_str} {record_str}"
