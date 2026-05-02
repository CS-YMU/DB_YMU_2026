# DB05 学生选课管理系统与数据库设计报告指导

本项目用于辅助完成 DB05 课外练习：学生选课管理系统数据库设计。它既提供一个可运行的 Python 命令行系统，也提供一份可参考的数据库设计报告写作思路。

系统以 `../DB05课外练习案例/dbsample.sql` 中的 16 张表为基础，并补充 2 张关系表：

```text
major_course       # 专业开设课程
teacher_guidance   # 教师指导学生
```

补充这 2 张表是为了覆盖作业最开始的完整业务描述：

- 一门课程可以为 0~n 个专业开设，一个专业可以开设 0~n 门课。
- 一个教师可以指导 0~n 个学生，一个学生被 1 个教师指导，并记录指导起止日期。

初始化后业务基础表共 18 张。

## 一、搭建环境

### 1. 环境要求

- Python 3.8+
- MySQL 服务可用
- 本机可执行 `mysql` 命令行客户端
- 当前目录旁边存在 `DB05课外练习案例/`
- `DB05课外练习案例/` 下存在：
  - `dbsample.sql`
  - `生成测试数据.sql`

默认数据库连接配置：

```text
host     = localhost
database = dbsample
user     = dylan
password = P@ssw0rd
charset  = gb18030
```

如需修改数据库连接参数，请同步修改：

- `main.py`
- `init_data.py`
- `init_advanced.py`

### 2. 安装 Python 依赖

进入项目目录：

```bash
cd stu_app_v1_04
```

安装依赖：

```bash
pip install -r requirements.txt
```

也可以使用：

```bash
python -m pip install -r requirements.txt
```

说明：`init_data.py` 主要通过 `mysql` 命令行执行 SQL。即使 Python 依赖未安装，仍可完成建库和导入数据，但最后的 Python 连接验证会跳过。

### 3. 初始化数据库

```bash
python init_data.py
```

脚本会执行：

1. 删除旧的 `dbsample` 数据库。
2. 创建新的 `dbsample` 数据库，字符集为 `gb18030`。
3. 执行 `../DB05课外练习案例/dbsample.sql`。
4. 执行 `../DB05课外练习案例/生成测试数据.sql`。
5. 补充创建 `major_course` 和 `teacher_guidance`。
6. 校验业务基础表数量必须为 18，并打印每张表的数据量。

如果第一步卡住，通常是 Navicat、MySQL Workbench 或正在运行的程序占用了 `dbsample`。当前脚本会自动断开占用 `dbsample` 的其它连接，再重建数据库。

手动检查业务基础表数量：

```bash
mysql -h localhost -u dylan -pP@ssw0rd --default-character-set=gb18030 dbsample \
  -e "SELECT COUNT(*) AS base_table_count
      FROM INFORMATION_SCHEMA.TABLES
      WHERE TABLE_SCHEMA = 'dbsample'
        AND TABLE_TYPE = 'BASE TABLE';"
```

期望结果：

```text
base_table_count
18
```

## 二、怎么使用这个系统

### 1. 启动系统

```bash
python main.py
```

进入系统后，按菜单编号输入操作。

### 2. 推荐使用顺序

1. 先运行 `python init_data.py`，重建数据库并导入测试数据。
2. 运行 `python main.py`，进入命令行菜单。
3. 先查看已有数据：
   - `2` 查看学生
   - `7` 查看课程
   - `12` 查看教师
   - `21` 专业管理
4. 再尝试核心业务操作：
   - `16` 学生选课
   - `20` 录入/修改成绩
   - `22` 先修课程管理
   - `30` 专业开课管理
   - `31` 教师指导管理
5. 需要演示高级数据库对象时，再运行 `python init_advanced.py` 或使用菜单 `25` 到 `29`。

### 3. 功能菜单

```text
【学生管理】
1. 添加学生      2. 查看所有学生   3. 搜索学生
4. 修改学生信息  5. 删除学生

【课程管理】
6. 添加课程      7. 查看所有课程   8. 搜索课程
9. 修改课程信息  10. 删除课程

【教师管理】
11. 添加教师     12. 查看所有教师  13. 搜索教师
14. 修改教师信息 15. 删除教师

【选课管理】
16. 学生选课     17. 查看学生选课  18. 查看所有选课
19. 退课         20. 录入/修改成绩

【专业、先修课程 & 统计】
21. 专业管理     22. 先修课程管理
23. 查询总学分   24. 查询平均成绩

【数据库对象管理】
25. 视图管理     26. 触发器管理    27. 存储过程管理
28. 函数管理     29. 完整性约束管理

【完整业务补充】
30. 专业开课管理 31. 教师指导管理
```

### 4. 系统功能与数据库表对应关系

| 功能模块 | 对应表 |
|---|---|
| 学生管理 | `student`, `student_major1`, `student_major2`, `student_phone` |
| 课程管理 | `course`, `teacher_course`, `course_leader` |
| 教师管理 | `teacher`, `teacher_major`, `dd_professional_title` |
| 专业管理 | `major`, `major_leader` |
| 选课管理 | `student_course`, `course`, `student` |
| 先修课程管理 | `course_prerequisite` |
| 专业开课管理 | `major_course` |
| 教师指导管理 | `teacher_guidance` |
| 数据字典查询 | `dd_sex`, `dd_professional_title`, `dd_administrative_divisions` |

## 三、数据库概念结构设计阶段怎么做

数据库概念结构设计的目标是：不考虑具体数据库软件，先把业务中的实体、关系和约束表达清楚。

### 1. 阅读业务需求

从作业描述中提取对象和规则：

- 专业：专业代码、名称、学制。
- 学生：注册序号、学号、姓名、性别、生日、入学年份、家庭地址、电话。
- 课程：课程代码、课程名、学分、学时。
- 教师：教师序号、工号、姓名、职称。
- 学生主修/辅修专业。
- 专业开设课程。
- 教师属于专业。
- 专业负责人。
- 课程先修关系。
- 教师讲授课程。
- 课程负责人。
- 学生选课。
- 教师指导学生。

### 2. 识别实体

建议把以下对象作为核心实体：

```text
学生
专业
课程
教师
```

数据字典也可以作为独立实体/字典表处理：

```text
性别编码
职称编码
行政区划编码
```

### 3. 识别关系

需要重点分析这些关系：

| 关系 | 类型 | 说明 |
|---|---|---|
| 学生-课程：选修 | m:n | 关系有属性：选课日期、学年、学期、成绩、是否通过、主修/辅修。 |
| 学生-专业：主修 | n:1 | 学生必须且只能主修一个专业。 |
| 学生-专业：辅修 | n:1 | 学生最多辅修一个专业。 |
| 专业-课程：开设 | m:n | 一个专业可开多门课，一门课可面向多个专业。 |
| 课程-课程：先修 | m:n 自关联 | 一门课程可有多门先修课。 |
| 教师-专业：属于 | n:1 | 一个教师属于一个专业。 |
| 专业-教师：负责人 | 1:1 | 一个专业有一个负责人，一个教师最多负责一个专业。 |
| 教师-课程：讲授 | 1:n | 一个教师可讲授多门课，每门课由一个教师讲授。 |
| 课程-教师：负责人 | 1:1 | 每门课有一个课程负责人。 |
| 教师-学生：指导 | 1:n | 一个教师指导多个学生，一个学生有一个指导教师。 |

### 4. 绘制 ER 简图

ER 图建议使用 Crow’s Foot 符号。注意：

- ER 简图只画实体和关系，不写字段。
- 要标出关系基数，例如 1:1、1:n、m:n。
- 要标出是否必须参与，例如学生必须主修专业。
- 关系有属性时，后续逻辑设计阶段要单独转换为关系表。

### 5. 编写关系语义

示例：

- 1 个学生选修 0~n 门课程；1 门课程被 0~n 个学生选修。
- 1 个学生主修 1 个专业；1 个专业是 0~n 个学生的主修专业。
- 1 门课程有 0~n 门先修课程；1 门课程可以作为 0~n 门课程的先修课程。
- 1 个教师指导 0~n 个学生；1 个学生被 1 个教师指导。

### 6. 分析属性

每个实体和关系都要分析属性特性：

| 属性特性 | 含义 | 示例 |
|---|---|---|
| 标识属性 | 能唯一识别对象 | 学号、课程代码、工号 |
| 强制属性 | 不能为空 | 姓名、入学年份 |
| 派生属性 | 可由其它属性计算 | 是否通过由成绩计算 |
| 多值属性 | 一个对象可有多个值 | 学生电话 |
| 复合属性 | 可拆分为多个部分 | 家庭地址 |
| 枚举属性 | 取值范围固定 | 性别、学期、电话类型 |

## 四、数据库逻辑结构设计

逻辑结构设计的目标是：把 ER 模型转换为关系模式，也就是“表结构草案”。

### 1. 转换规则

- 一个实体集通常转换为一个表。
- 一个 m:n 关系必须转换为一个关系表。
- 一个 1:n 关系通常在 n 方加入外键。
- 一个 1:1 关系可以转换为关系表，也可以在一方加入外键。
- 关系本身有属性时，建议转换为独立关系表。

### 2. 属性处理

| 问题 | 处理方式 |
|---|---|
| 多值属性 | 拆为独立表，例如 `student_phone`。 |
| 复合属性 | 拆为多个字段，例如行政区划编码 + 详细地址。 |
| 派生属性 | 保存计算规则，例如 `HasPassed = Score >= 60`。 |
| 枚举属性 | 使用数据字典表或 ENUM 类型。 |
| 候选码 | 在物理设计中使用唯一索引实现。 |

### 3. 建议关系模式清单

DB05 示例 SQL 原有 16 张表：

```text
dd_sex
dd_professional_title
dd_administrative_divisions
major
student
student_phone
course
teacher
student_course
student_major1
student_major2
course_prerequisite
major_leader
teacher_major
course_leader
teacher_course
```

为覆盖完整业务描述，本系统补充：

```text
major_course
teacher_guidance
```

### 4. 关键关系表说明

| 表名 | 设计意义 |
|---|---|
| `student_course` | 学生选课 m:n 关系，同时保存选课日期、学年、学期、成绩等关系属性。 |
| `student_major1` | 学生主修专业。 |
| `student_major2` | 学生辅修专业。 |
| `student_phone` | 学生电话，多值属性拆表。 |
| `course_prerequisite` | 课程先修，自关联 m:n。 |
| `major_leader` | 专业负责人 1:1。 |
| `teacher_major` | 教师所属专业。 |
| `course_leader` | 课程负责人 1:1。 |
| `teacher_course` | 教师讲授课程。 |
| `major_course` | 专业开设课程，补充完整业务需求。 |
| `teacher_guidance` | 教师指导学生，补充完整业务需求。 |

## 五、数据库物理结构设计（MySQL 中实现数据库的要求）

物理结构设计的目标是：把逻辑表结构落实到 MySQL 的字段类型、索引、约束和存储实现。

### 1. 基本约定

```text
数据库名称：dbsample
数据库管理系统：MySQL
字符编码：gb18030
```

### 2. 主键设计

建议使用 AID 作为代理主键：

- `student.AID`
- `course.AID`
- `teacher.AID`
- `major.AID`

业务编号作为唯一索引：

- `student.Code`
- `course.Code`
- `teacher.Code`
- `major.Code`

### 3. 数据字典设计

使用数据字典表保存标准枚举数据：

- `dd_sex`：性别。
- `dd_professional_title`：职称。
- `dd_administrative_divisions`：行政区划。

学生表、教师表通过外键引用这些字典表。

### 4. 外键设计

DB05 示例 SQL 的外键策略：

```text
ON DELETE RESTRICT
ON UPDATE CASCADE
```

含义：

- 被引用数据正在使用时，不允许直接删除。
- 被引用主键更新时，引用方级联更新。

### 5. 约束设计

需要关注：

- 主键约束。
- 唯一索引。
- 外键约束。
- CHECK 约束，例如：
  - `course.Hours >= 0`
  - `course.Credit >= 0`
  - `student.YearInroll > 0`
- 虚拟列，例如：
  - `student_course.HasPassed` 由 `Score >= 60` 自动计算。

### 6. 补充表物理设计

`major_course`：

```text
MajorAID  -> major.AID
CourseAID -> course.AID
主键：(MajorAID, CourseAID)
```

`teacher_guidance`：

```text
StudentAID -> student.AID
TeacherAID -> teacher.AID
StartDate  指导开始日期
EndDate    指导结束日期，可为空
主键：StudentAID
```

`teacher_guidance.StudentAID` 作为主键，表示一个学生最多只有一个当前指导关系。

## 六、数据库实现（实施）

数据库实现阶段的目标是：真正创建数据库、运行 SQL、导入数据并核查结果。

### 1. 使用脚本初始化

```bash
cd stu_app_v1_04
python init_data.py
```

该脚本会：

- 删除并重建 `dbsample`。
- 执行 DB05 示例建表 SQL。
- 执行 DB05 测试数据 SQL。
- 补充创建 `major_course`、`teacher_guidance`。
- 生成补充关系测试数据。
- 检查业务基础表数量是否为 18。

### 2. 检查表数量

```bash
mysql -h localhost -u dylan -pP@ssw0rd --default-character-set=gb18030 dbsample \
  -e "SELECT COUNT(*) AS base_table_count
      FROM INFORMATION_SCHEMA.TABLES
      WHERE TABLE_SCHEMA = 'dbsample'
        AND TABLE_TYPE = 'BASE TABLE';"
```

应得到：

```text
base_table_count
18
```

### 3. 核查字段和约束

建议核查：

- 表是否完整。
- 字段是否完整。
- 主键是否正确。
- 唯一索引是否正确。
- 外键是否正确。
- CHECK 约束是否存在。
- 虚拟列是否存在。

可使用：

```sql
SHOW CREATE TABLE student_course;
SHOW CREATE TABLE teacher_guidance;
SHOW CREATE TABLE major_course;
```

### 4. 生成数据关系图

建议使用 Navicat 或 MySQL Workbench 生成数据库关系图。不要只生成一张大图，建议按主题拆分：

- 数据字典图。
- 学生相关图。
- 课程相关图。
- 教师相关图。
- 专业相关图。
- 选课相关图。
- 完整业务补充图：`major_course`、`teacher_guidance`。

### 5. 生成元数据报告

可使用 Navicat 的数据字典功能生成元数据报告。报告中应体现：

- 表名。
- 字段名。
- 字段类型。
- 是否允许为空。
- 主键、索引、外键。
- 默认值和约束。

## 七、数据库应用设计（应用程序与数据库外模式设计）

应用设计阶段的目标是：说明普通用户如何通过程序访问数据库，以及程序中的功能如何映射到数据库表。

### 1. 应用程序运行

```bash
cd stu_app_v1_04
python main.py
```

### 2. 外模式理解

外模式可以理解为“用户看到和使用的数据视图”。例如：

- 用户看到“学生姓名、专业、课程、成绩”，程序背后需要连接 `student`、`student_major1`、`major`、`student_course`、`course`。
- 用户执行“学生选课”，程序背后向 `student_course` 插入记录。
- 用户执行“设置教师指导学生”，程序背后向 `teacher_guidance` 插入或更新记录。

### 3. 应用功能与表映射

| 应用功能 | 数据库表 |
|---|---|
| 添加学生 | `student`, `student_major1`, `student_major2`, `student_phone` |
| 查看学生 | `student`, `dd_sex`, `major`, `dd_administrative_divisions` |
| 添加课程 | `course`, `teacher_course`, `course_leader` |
| 添加教师 | `teacher`, `teacher_major` |
| 学生选课 | `student_course` |
| 录入成绩 | `student_course.Score` |
| 查询是否通过 | `student_course.HasPassed` |
| 维护先修课程 | `course_prerequisite` |
| 设置专业负责人 | `major_leader` |
| 设置课程负责人 | `course_leader` |
| 设置专业开课 | `major_course` |
| 设置教师指导学生 | `teacher_guidance` |

### 4. 可写入报告的应用设计说明

报告中可以这样描述：

> 本系统采用 Python 命令行方式作为数据库应用程序。用户通过菜单完成学生、课程、教师、专业等基础数据的维护，并完成选课、成绩录入、先修课程、专业开课、教师指导等业务操作。程序通过 `database.py` 将用户操作转换为 SQL，对 MySQL 数据库 `dbsample` 中的表进行增删改查。系统中的查询功能体现了数据库外模式设计，例如学生成绩查询、课程统计、学生总学分和平均成绩查询等。

### 5. 高级对象说明

本项目还提供高级对象演示：

```bash
python init_advanced.py
```

包括：

- 视图：`v_student_scores`、`v_course_stats`、`v_student_credits`
- 触发器：成绩范围检查
- 存储过程：学生排名、课程及格率、成绩加分
- 函数：成绩等级、GPA

这些内容可作为扩展学习，不是 DB05 示例 SQL 原本 16 张表的一部分。

## 八、建议报告目录

学生写数据库设计报告时，可按以下结构组织：

```text
1. 数据库概念结构设计
   1.1 业务需求分析
   1.2 实体与关系识别
   1.3 ER 简图
   1.4 关系语义说明
   1.5 实体和关系属性分析

2. 数据库逻辑结构设计
   2.1 ER 模型转换为关系模式
   2.2 多值属性处理
   2.3 复合属性处理
   2.4 派生属性处理
   2.5 枚举属性和数据字典处理
   2.6 最终关系模式清单

3. 数据库物理结构设计
   3.1 MySQL 实现约定
   3.2 表结构设计
   3.3 主键、唯一索引、外键设计
   3.4 CHECK 约束和虚拟列设计

4. 数据库实现
   4.1 建库建表 SQL
   4.2 测试数据生成
   4.3 数据库关系图
   4.4 元数据报告
   4.5 实现核查

5. 数据库应用设计
   5.1 应用程序功能
   5.2 外模式设计
   5.3 主要查询和数据处理流程
   5.4 系统运行截图或说明
```

## 九、常用命令汇总

```bash
cd stu_app_v1_04
pip install -r requirements.txt
python init_data.py
python main.py
```

可选：

```bash
python init_advanced.py
```
