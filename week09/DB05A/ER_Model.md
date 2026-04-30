# 运动会管理系统 —— 概念建模（ER 建模）

---

## 一、实体联系简图（Crow's Foot 符号）

```
        ┌──────────────┐
        │   运动会      │
        │ SportsMeet   │
        └──────┬───────┘
               │
               │ 包含 (1 : N)
               │
        ┌──────▼───────┐        执裁 (M : N)        ┌──────────────┐
        │  竞赛项目     │◄──────────────────────────►│    裁判      │
        │    Event     │         属性: 职务          │   Referee   │
        └──────┬───────┘                            └──────────────┘
               ▲
               │ 参加 (M : N)
               │ 属性: 成绩, 名次, 是否破纪录
               │
        ┌──────┴───────┐
        │   运动员      │
        │   Athlete    │
        └──────────────┘
```

### ER 简图说明

| 关系 | 基数 | 语义 |
|------|------|------|
| 运动会 —— 竞赛项目 | 1 : N | 每届运动会包含多个竞赛项目，每个竞赛项目属于一届运动会 |
| 裁判 —— 竞赛项目 | M : N | 一名裁判可执裁多个项目，一个项目可由多名裁判共同执裁 |
| 运动员 —— 竞赛项目 | M : N | 一名运动员可参加多个项目，一个项目有多名运动员参加 |

---

## 二、实体及属性详细建模

### 2.1 运动会（SportsMeet）

| 属性 | 英文名 | 数据类型 | 约束 | 说明 |
|------|--------|----------|------|------|
| 届次编号 | meet_id | VARCHAR(20) | PRIMARY KEY | 唯一标识每届运动会 |
| 名称 | name | VARCHAR(100) | UNIQUE, NOT NULL | 如"第46届田径运动会" |
| 举办日期 | date | DATE | NOT NULL | 运动会举办日期 |
| 举办地点 | location | VARCHAR(200) | - | 运动会举办地点 |

---

### 2.2 竞赛项目（Event）

| 属性 | 英文名 | 数据类型 | 约束 | 说明 |
|------|--------|----------|------|------|
| 项目编号 | event_id | VARCHAR(20) | PRIMARY KEY | 唯一标识竞赛项目 |
| 项目名称 | event_name | VARCHAR(100) | UNIQUE, NOT NULL | 如"男子100米" |
| 项目类别 | category | VARCHAR(20) | NOT NULL | 枚举：田赛/径赛/团体 |
| 是否团体项目 | is_team | BOOLEAN | NOT NULL, DEFAULT FALSE | 是/否 |
| 届次编号 | meet_id | VARCHAR(20) | FOREIGN KEY → 运动会 | 所属运动会 |

> **说明**：竞赛项目依赖于运动会，每个竞赛项目必须属于某一届运动会（1:N 关系）。

---

### 2.3 裁判（Referee）

| 属性 | 英文名 | 数据类型 | 约束 | 说明 |
|------|--------|----------|------|------|
| 裁判编号 | referee_id | VARCHAR(20) | PRIMARY KEY | 唯一标识每位裁判 |
| 姓名 | name | VARCHAR(50) | NOT NULL | 裁判姓名 |
| 裁判等级 | level | VARCHAR(20) | NOT NULL | 如：国家级/一级/二级 |

---

### 2.4 运动员（Athlete）

| 属性 | 英文名 | 数据类型 | 约束 | 说明 |
|------|--------|----------|------|------|
| 运动员编号 | athlete_id | VARCHAR(20) | PRIMARY KEY | 唯一标识每位运动员 |
| 姓名 | name | VARCHAR(50) | NOT NULL | 运动员姓名 |
| 性别 | gender | ENUM('男','女') | NOT NULL | 运动员性别 |
| 所属学院 | college | VARCHAR(100) | NOT NULL | 如"计算机学院" |

> **多值属性**：运动员的**联系电话**为多值属性，需单独建表处理（见下方）。

#### 运动员联系电话（AthletePhone）

| 属性 | 英文名 | 数据类型 | 约束 | 说明 |
|------|--------|----------|------|------|
| 运动员编号 | athlete_id | VARCHAR(20) | FOREIGN KEY → 运动员 | 联合主键之一 |
| 联系电话 | phone | VARCHAR(20) | NOT NULL | 一个运动员可有多个电话 |

> 主键：(athlete_id, phone)

---

## 三、关系及关系属性详细建模

### 3.1 包含（SportsMeet —— Event）

| 关系名 | 包含 | Contains |
|--------|------|----------|
| 参与实体 | 运动会(1端) / 竞赛项目(N端) | |
| 语义 | 每届运动会包含多个竞赛项目，每个竞赛项目属于且仅属于一届运动会 | |
| 关系属性 | 无（可通过在 Event 实体中增加 meet_id 外键实现） | |
| 实现方式 | 在 Event 表中添加 meet_id 外键字段 | |

---

### 3.2 执裁（Referee —— Event）

| 关系名 | 执裁 | Referee_Event |
|--------|------|---------------|
| 参与实体 | 裁判(M端) / 竞赛项目(N端) | |
| 语义 | 一名裁判可执裁多个竞赛项目，一个竞赛项目可由多名裁判共同执裁 | |
| 关系属性 | 职务（如"主裁判"、"计时裁判"等） | |

#### 执裁关系属性表

| 属性 | 英文名 | 数据类型 | 约束 | 说明 |
|------|--------|----------|------|------|
| 裁判编号 | referee_id | VARCHAR(20) | FOREIGN KEY → 裁判, PRIMARY KEY | 联合主键之一 |
| 项目编号 | event_id | VARCHAR(20) | FOREIGN KEY → 竞赛项目, PRIMARY KEY | 联合主键之一 |
| 职务 | role | VARCHAR(50) | NOT NULL | 如：主裁判、计时裁判、发令裁判 |

> 主键：(referee_id, event_id)

---

### 3.3 参加（Athlete —— Event）

| 关系名 | 参加 | Participate |
|--------|------|-------------|
| 参与实体 | 运动员(M端) / 竞赛项目(N端) | |
| 语义 | 一名运动员可报名参加多个竞赛项目，一个竞赛项目有多名运动员参加 | |
| 关系属性 | 成绩、名次、是否破纪录 | |

#### 参加关系属性表

| 属性 | 英文名 | 数据类型 | 约束 | 说明 |
|------|--------|----------|------|------|
| 运动员编号 | athlete_id | VARCHAR(20) | FOREIGN KEY → 运动员, PRIMARY KEY | 联合主键之一 |
| 项目编号 | event_id | VARCHAR(20) | FOREIGN KEY → 竞赛项目, PRIMARY KEY | 联合主键之一 |
| 参赛成绩 | score | DECIMAL(10,2) | - | 数值表示，如12.5（秒）、5.68（米） |
| 名次 | rank | INT | - | 1, 2, 3, ... |
| 是否破纪录 | is_record | BOOLEAN | DEFAULT FALSE | 是否打破纪录 |

> 主键：(athlete_id, event_id)

---

## 四、完整关系语义描述

| 关系 | 实体1 | 实体2 | 基数 | 语义 |
|------|-------|-------|------|------|
| 包含 | 运动会 | 竞赛项目 | 1 : N | 每届运动会包含多个竞赛项目；每个竞赛项目只属于一届运动会 |
| 执裁 | 裁判 | 竞赛项目 | M : N | 一名裁判可执裁多个竞赛项目；一个竞赛项目可由多名裁判共同执裁。需记录裁判在该项目中的具体职务 |
| 参加 | 运动员 | 竞赛项目 | M : N | 一名运动员可参加多个竞赛项目；一个竞赛项目有多名运动员参加。需记录参赛成绩、名次和是否破纪录 |

---

## 五、常见错误提示（对照自查）

| 易错点 | 正确做法 |
|--------|----------|
| ❌ 将"成绩"作为运动员或项目的属性 | ✅ 成绩是"参加"联系的属性，依赖于(运动员, 项目)组合 |
| ❌ 将"职务"作为裁判的属性 | ✅ 职务是"执裁"联系的属性，依赖于(裁判, 项目)组合 |
| ❌ 将"联系电话"作为运动员的单值属性 | ✅ 联系电话是多值属性，需单独建表或建模为多值属性 |
| ❌ 单独为"竞赛成绩"创建实体 | ✅ 竞赛成绩是联系属性，不需要单独实体 |
| ❌ 裁判与运动员建立直接联系 | ✅ 题目明确说明裁判与运动员没有直接联系 |

---

## 六、逻辑设计（可选 —— 关系模式）

若从 ER 图转换到关系模式：

```
SportsMeet(meet_id, name, date, location)
Event(event_id, event_name, category, is_team, meet_id)
    -- meet_id → SportsMeet(meet_id)
Referee(referee_id, name, level)
Athlete(athlete_id, name, gender, college)
AthletePhone(athlete_id, phone)
    -- athlete_id → Athlete(athlete_id)
Referee_Event(referee_id, event_id, role)
    -- referee_id → Referee(referee_id)
    -- event_id → Event(event_id)
Participation(athlete_id, event_id, score, rank, is_record)
    -- athlete_id → Athlete(athlete_id)
    -- event_id → Event(event_id)
```
