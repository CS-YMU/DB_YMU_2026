# 学生选课管理系统 —— 高级数据库对象教学说明

> 本文档配合 `week07/stu_app_v1` 使用，面向课堂教学场景，系统讲解如何在真实 CLI 项目中引入**视图（View）、触发器（Trigger）、存储过程（Stored Procedure）、函数（Function）以及完整性约束（Integrity Constraint）**等数据库对象。

---

## 一、项目结构与文件说明

```
week07/stu_app_v1/
├── main.py               # CLI 主程序（已扩展数据库对象管理菜单）
├── database.py           # 数据库操作类（新增视图/触发器/过程/函数/约束管理）
├── models.py             # 数据模型（Student、Course、SC）
├── init_data.py          # 基础数据初始化脚本
├── init_advanced.py      # 【新增】高级数据库对象一键初始化与演示
├── requirements.txt      # 依赖（mysql-connector-python）
└── DATABASE_OBJECTS.md   # 【新增】本文档
```

---

## 二、设计原则

1. **简单直观**：每种数据库对象只提供 1~2 个最经典的教学案例，避免过度设计。
2. **中文注释**：所有新增代码均带有详细中文注释，便于逐行讲解。
3. **交互式管理**：主菜单新增“数据库对象管理”模块，支持在 CLI 中创建、查看、调用、删除各类对象。
4. **一键演示**：`init_advanced.py` 可一键创建所有对象并输出演示结果，适合教师在课堂上快速搭建环境。

---

## 三、视图（View）

### 3.1 教学概念

视图是**虚拟表**，本身不存储数据，而是基于一条 `SELECT` 语句的动态结果集。它常用于：
- 简化复杂的联表查询；
- 为不同用户暴露不同的数据子集（安全隔离）；
- 将统计逻辑封装为“表”的形式。

### 3.2 本案例中的视图

| 视图名 | 作用 |
|--------|------|
| `v_student_scores` | 将 `students`、`course`、`sc` 三表关联，展示学生成绩明细 |
| `v_course_stats` | 聚合每门课程的选课人数、平均分、最高分、最低分 |

### 3.3 核心 SQL 语法示例

```sql
CREATE OR REPLACE VIEW v_student_scores AS
SELECT
    s.student_id,
    s.name AS student_name,
    s.major,
    c.course_id,
    c.course_name,
    c.credit,
    sc.semester,
    sc.score
FROM sc
JOIN students s ON sc.student_id = s.student_id
JOIN course c ON sc.course_id = c.course_id;
```

### 3.4 CLI 操作路径

```
主菜单 → 18. 视图管理 →
  1. 创建学生成绩视图
  2. 创建课程统计视图
  3. 查看所有视图
  4. 查询视图内容
  5. 删除视图
```

### 3.5 课堂讲解要点
- 强调 `CREATE OR REPLACE` 的幂等性：重复执行不会报错。
- 对比“直接查基表”与“查视图”在应用层代码上的差异。
- 提问：如果基表数据改了，视图中的数据会变吗？（答案是：会，因为视图不存数据）

---

## 四、触发器（Trigger）

### 4.1 教学概念

触发器是一种**自动执行的存储程序**，在 `INSERT`、`UPDATE`、`DELETE` 事件发生前（`BEFORE`）或后（`AFTER`）自动触发。它常用于：
- 自动化业务规则检查；
- 审计日志（Audit Log）；
- 级联更新或数据同步。

### 4.2 本案例中的触发器

| 触发器名 | 触发时机 | 作用 |
|----------|----------|------|
| `trg_before_sc_score_check` | `BEFORE INSERT` | 检查成绩是否在 `0~100` 之间，否则抛出错误 |
| `trg_before_sc_score_update_check` | `BEFORE UPDATE` | 同上，针对更新操作 |
| `trg_after_student_delete_log` | `AFTER DELETE` | 学生被删除后，自动将删除信息写入日志表 |

### 4.3 核心 SQL 语法示例（成绩检查触发器）

```sql
CREATE TRIGGER trg_before_sc_score_check
BEFORE INSERT ON sc
FOR EACH ROW
BEGIN
    IF NEW.score IS NOT NULL AND (NEW.score < 0 OR NEW.score > 100) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '成绩必须在 0~100 之间';
    END IF;
END
```

> `NEW` 关键字表示即将插入的新记录；`SIGNAL SQLSTATE '45000'` 用于抛出自定义错误。

### 4.4 核心 SQL 语法示例（删除日志触发器）

```sql
CREATE TRIGGER trg_after_student_delete_log
AFTER DELETE ON students
FOR EACH ROW
BEGIN
    INSERT INTO student_delete_log (student_id, name, major)
    VALUES (OLD.student_id, OLD.name, OLD.major);
END
```

> `OLD` 关键字表示被删除的旧记录。

### 4.5 CLI 操作路径

```
主菜单 → 19. 触发器管理 →
  1. 创建成绩范围检查触发器
  2. 创建学生删除日志触发器
  3. 查看所有触发器
  4. 查看删除日志
  5. 删除触发器
```

### 4.6 课堂演示建议
1. 先创建 `trg_before_sc_score_check`；
2. 在 CLI 中尝试录入成绩 `150`，观察报错；
3. 再创建 `trg_after_student_delete_log`；
4. 删除一名学生，然后查看 `student_delete_log` 表，验证日志是否自动产生。

---

## 五、存储过程（Stored Procedure）

### 5.1 教学概念

存储过程是**预编译的 SQL 程序**，保存在数据库服务器端，可接收输入参数（`IN`）、输出参数（`OUT`），并执行复杂的控制流逻辑。优点：
- 减少客户端与服务端之间的网络交互；
- 将业务逻辑下沉到数据库层，统一维护；
- 提升安全性（可避免直接暴露表结构）。

### 5.2 本案例中的存储过程

| 过程名 | 功能 |
|--------|------|
| `sp_student_rank` | 输入学号，输出该学生在全部学生中的平均成绩排名 |
| `sp_course_pass_rate` | 输入课程号，输出该课程的及格率（百分比） |

### 5.3 核心 SQL 语法示例（学生排名）

```sql
CREATE PROCEDURE sp_student_rank(IN p_student_id VARCHAR(20), OUT p_rank INT)
BEGIN
    SELECT student_rank INTO p_rank
    FROM (
        SELECT
            student_id,
            RANK() OVER (ORDER BY AVG(score) DESC) AS student_rank
        FROM sc
        WHERE score IS NOT NULL
        GROUP BY student_id
    ) ranked
    WHERE student_id = p_student_id;
END
```

### 5.4 核心 SQL 语法示例（课程及格率）

```sql
CREATE PROCEDURE sp_course_pass_rate(
    IN p_course_id VARCHAR(20),
    OUT p_pass_rate DECIMAL(5,2)
)
BEGIN
    DECLARE total_count INT DEFAULT 0;
    DECLARE pass_count INT DEFAULT 0;

    SELECT COUNT(*) INTO total_count
    FROM sc WHERE course_id = p_course_id AND score IS NOT NULL;

    SELECT COUNT(*) INTO pass_count
    FROM sc WHERE course_id = p_course_id AND score >= 60;

    IF total_count > 0 THEN
        SET p_pass_rate = (pass_count / total_count) * 100;
    ELSE
        SET p_pass_rate = 0;
    END IF;
END
```

### 5.5 CLI 操作路径

```
主菜单 → 20. 存储过程管理 →
  1. 创建学生排名存储过程
  2. 创建课程及格率存储过程
  3. 调用学生排名存储过程
  4. 调用课程及格率存储过程
  5. 查看所有存储过程
  6. 删除存储过程
```

### 5.6 课堂讲解要点
- `IN` vs `OUT`：输入参数 vs 输出参数；
- `DECLARE` 局部变量与 `SET` 赋值；
- `RANK() OVER (...)` 窗口函数的应用场景；
- 对比“在 Python 中计算排名” vs “在存储过程中计算排名”的优劣。

---

## 六、函数（Function）

### 6.1 教学概念

自定义函数（User-Defined Function, UDF）与存储过程的区别在于：
- **函数**必须返回一个值，且可在 `SELECT`、`WHERE`、`ORDER BY` 等 SQL 语句中直接调用；
- **存储过程**通过 `CALL` 调用，可返回多个结果集或 `OUT` 参数，但**不能**嵌入到普通 SQL 表达式中。

### 6.2 本案例中的函数

| 函数名 | 功能 |
|--------|------|
| `fn_grade_level(score)` | 根据成绩返回等级：优 / 良 / 中 / 及格 / 不及格 / 未录入 |

### 6.3 核心 SQL 语法示例

```sql
CREATE FUNCTION fn_grade_level(score DECIMAL(5,2))
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
    IF score IS NULL THEN
        RETURN '未录入';
    ELSEIF score >= 90 THEN
        RETURN '优';
    ELSEIF score >= 80 THEN
        RETURN '良';
    ELSEIF score >= 70 THEN
        RETURN '中';
    ELSEIF score >= 60 THEN
        RETURN '及格';
    ELSE
        RETURN '不及格';
    END IF;
END
```

> `DETERMINISTIC` 声明：给定相同的输入，函数总是返回相同的结果。这是 MySQL 开启二进制日志时对函数创建的常见要求。

### 6.4 在 SELECT 中调用函数

```sql
SELECT
    s.student_id,
    s.name,
    c.course_name,
    sc.score,
    fn_grade_level(sc.score) AS grade_level
FROM sc
JOIN students s ON sc.student_id = s.student_id
JOIN course c ON sc.course_id = c.course_id;
```

### 6.5 CLI 操作路径

```
主菜单 → 21. 函数管理 →
  1. 创建成绩等级函数
  2. 调用函数测试
  3. 在查询中演示函数
  4. 查看所有函数
  5. 删除函数
```

### 6.6 课堂讲解要点
- 函数 vs 存储过程：使用场景、调用方式、返回值差异；
- `DETERMINISTIC`、`NO SQL`、`READS SQL DATA` 等特性声明的意义；
- 提问：为什么成绩等级适合用函数，而排名计算更适合用存储过程？

---

## 七、完整性约束（Integrity Constraint）

### 7.1 教学概念

完整性约束是保证数据库中数据正确性、一致性的规则。常见类型：
- `PRIMARY KEY`：实体完整性；
- `FOREIGN KEY`：参照完整性；
- `UNIQUE`：唯一性约束；
- `CHECK`：域完整性，限制列的取值范围；
- `NOT NULL`：非空约束。

### 7.2 本案例中的约束示例

基础表创建时已经内建了以下约束（见 `database.py` 的 `create_tables`）：
- `students` 表：`PRIMARY KEY (student_id)`、`CHECK (age > 0 AND age < 150)`
- `course` 表：`PRIMARY KEY (course_id)`
- `sc` 表：
  - `FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE`
  - `FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE RESTRICT`
  - `UNIQUE (student_id, course_id, semester)`

新增功能支持**动态添加/删除**约束：
- `ALTER TABLE ... ADD CONSTRAINT ... CHECK (...)`
- `ALTER TABLE ... DROP CONSTRAINT ...`

### 7.3 CLI 操作路径

```
主菜单 → 22. 完整性约束管理 →
  1. 查看指定表的所有约束
  2. 添加 CHECK 约束
  3. 删除指定约束
```

### 7.4 课堂演示建议
1. 先查看 `sc` 表的外键约束名称；
2. 尝试删除某个外键约束，观察删除后是否能插入非法的 `student_id`；
3. 重新添加外键约束，恢复数据完整性；
4. 在 `course` 表上动态添加 `CHECK (credit > 0)`，然后尝试插入学分为 `-1` 的课程，观察报错。

---

## 八、快速启动指南

### 8.1 环境准备

确保已安装依赖并配置好本地 MySQL：

```bash
cd week07/stu_app_v1
pip install -r requirements.txt
```

> 默认数据库配置为 `host=localhost, database=student_db, user=dylan, password=P@ssw0rd`。如需修改，请编辑 `main.py` 和 `init_advanced.py` 顶部的配置。

### 8.2 启动基础数据

```bash
python init_data.py
```

该脚本会重建 `students`、`course`、`sc` 三张基表，并插入 4 名学生、6 门课程、14 条选课记录及对应成绩。

### 8.3 启动高级对象演示

```bash
python init_advanced.py
```

该脚本会自动创建所有视图、触发器、存储过程、函数，并输出调用演示结果。

### 8.4 进入交互式 CLI

```bash
python main.py
```

在菜单中选择 **18~22** 即可交互式管理各类数据库对象。

---

## 九、课堂授课建议

### 9.1 授课顺序（推荐 45 分钟课时分配）

| 阶段 | 内容 | 时长 |
|------|------|------|
| 1 | 回顾基表与基础 CRUD（快速带过） | 5 min |
| 2 | **视图**：创建 + 查询演示，强调“虚拟表”概念 | 8 min |
| 3 | **触发器**：BEFORE 检查 + AFTER 日志，现场删学生看日志 | 10 min |
| 4 | **存储过程**：讲解 IN/OUT，调用 `sp_student_rank` | 10 min |
| 5 | **函数**：对比过程，现场在 SELECT 中调用 `fn_grade_level` | 7 min |
| 6 | **完整性约束**：查看已有约束 + 动态添加 CHECK 约束 | 5 min |

### 9.2 常见学生问题与解答

**Q1：视图会占用大量存储空间吗？**
> 不会。视图只保存定义（即那条 SELECT 语句），不保存数据本身。查询视图时，数据库会实时执行该 SELECT。

**Q2：触发器和 CHECK 约束有什么区别？**
> `CHECK` 约束是声明式的、静态的，只能写简单条件；触发器是过程式的，可以执行更复杂的逻辑（如跨表操作、写日志、发信号等）。

**Q3：存储过程和函数到底用哪个？**
> 如果需要“在 SQL 语句中像 `COUNT()` 一样被调用”，用函数；如果需要“执行一段独立逻辑、返回多个值或结果集”，用存储过程。

**Q4：MySQL 创建函数报错 `This function has none of DETERMINISTIC...`**
> 因为 MySQL 开启了二进制日志（binlog），要求函数必须声明是 `DETERMINISTIC`、`NO SQL` 或 `READS SQL DATA`。本案例已在函数定义中加入 `DETERMINISTIC`。

---

## 十、课后作业

> 以下五个课后作业分别对应 **视图、触发器、存储过程、函数、完整性约束**。每个作业均已在 `database.py` 和 `main.py` 中预留了带 `TODO` 注释的代码框架，学生只需在指定位置补全核心 SQL 或 Python 逻辑，即可在 CLI 菜单中直接运行验证。

---

### 作业 1：视图 —— 学生学分与平均成绩统计视图

#### 目标
在 `database.py` 中补全 `create_view_student_credits` 方法，创建一个名为 `v_student_credits` 的视图。该视图需展示每位学生的：
- 学号 (`student_id`)
- 姓名 (`name`)
- 总学分 (`total_credits`，使用 `SUM`)
- 平均成绩 (`avg_score`，使用 `AVG`)

#### 涉及知识点
- 多表关联（`LEFT JOIN`）
- 聚合函数（`SUM`、`AVG`）与 `GROUP BY`
- 视图的创建语法 `CREATE OR REPLACE VIEW ... AS`

#### 详细步骤引导
1. 打开 `database.py`，定位到 `create_view_student_credits` 方法（在“课后作业 1”注释下方）。
2. 将 `query` 变量中的 `-- TODO` 注释替换为完整的 `CREATE OR REPLACE VIEW` 语句。
3. 关联三张表：`students`（学生信息）、`sc`（选课记录）、`course`（课程学分）。
4. **注意**：只统计已录入成绩的课程（`sc.score IS NOT NULL`），否则 `AVG` 和 `SUM` 会计算未出成绩的课程。
5. 保存文件后，运行 `python main.py` → 选择 **18. 视图管理** → 选择 **6. 【课后作业】创建学生学分统计视图**，验证是否创建成功。
6. 在视图管理菜单中选择 **4. 查询视图内容**，输入视图名 `v_student_credits`，查看结果。

#### 代码占位位置
- `database.py`：搜索 `课后作业 1：视图扩展`
- `main.py`：视图管理子菜单已预留选项 **6**

---

### 作业 2：触发器 —— 学生专业变更日志

#### 目标
在 `database.py` 中补全 `create_trigger_major_change_log` 方法，实现一个 `AFTER UPDATE` 触发器：
- 当 `students` 表的 `major`（专业）字段被修改时，自动在 `major_change_log` 日志表中记录旧专业和新专业。

#### 涉及知识点
- `AFTER UPDATE` 触发器的语法
- `OLD` 与 `NEW` 伪记录的使用
- 条件判断（`IF ... THEN ... END IF`）

#### 详细步骤引导
1. 打开 `database.py`，定位到 `create_trigger_major_change_log` 方法（在“课后作业 2”注释下方）。
2. **第一步**：补全 `create_log_table` 中的 SQL，创建日志表 `major_change_log`。建议包含以下字段：
   - `log_id`：自增主键
   - `student_id`：学号
   - `old_major`：修改前的专业
   - `new_major`：修改后的专业
   - `changed_at`：修改时间（默认当前时间）
3. **第二步**：补全 `query` 中的触发器定义：
   - 触发器名：`trg_after_student_major_change_log`
   - 触发时机：`AFTER UPDATE ON students`
   - 触发器体中使用 `OLD.major` 和 `NEW.major`
   - 建议加上 `IF OLD.major <> NEW.major THEN ... END IF;`，避免无意义记录
4. 保存文件后，运行 `python main.py` → 选择 **19. 触发器管理** → 选择 **6. 【课后作业】创建专业变更日志触发器**。
5. 验证：在主菜单选择 **4. 修改学生信息**，将某位学生的专业改为其他值，然后回到触发器管理菜单选择 **7. 【课后作业】查看专业变更日志**，观察是否生成了日志记录。

#### 代码占位位置
- `database.py`：搜索 `课后作业 2：触发器扩展`
- `main.py`：触发器管理子菜单已预留选项 **6**（创建）和 **7**（查看日志）

---

### 作业 3：存储过程 —— 课程成绩统一加分

#### 目标
在 `database.py` 中补全 `create_proc_score_bonus` 和 `call_proc_score_bonus` 方法，创建一个存储过程 `sp_score_bonus`：
- 输入：课程号 (`course_id`) 和 加分值 (`bonus`)
- 功能：为该课程所有已录入成绩的学生统一加分，但**上限不超过 100 分**

#### 涉及知识点
- `IN` 参数的定义与使用
- `UPDATE` 语句结合条件控制
- MySQL 内置函数 `LEAST(a, b)` 的用法

#### 详细步骤引导
1. 打开 `database.py`，定位到 `create_proc_score_bonus` 方法（在“课后作业 3”注释下方）。
2. 将 `query` 中的 `-- TODO` 替换为完整的 `CREATE PROCEDURE` 语句：
   - 过程名：`sp_score_bonus`
   - 参数：`IN p_course_id VARCHAR(20), IN p_bonus DECIMAL(5,2)`
   - 核心逻辑：`UPDATE sc SET score = LEAST(score + p_bonus, 100) WHERE course_id = p_course_id AND score IS NOT NULL;`
3. 补全 `call_proc_score_bonus` 方法中的 `self.cursor.execute(...)` 调用语句，执行 `CALL sp_score_bonus(%s, %s)`。
4. 保存文件后，运行 `python main.py` → 选择 **20. 存储过程管理** → 选择 **7. 【课后作业】创建并调用成绩加分存储过程**。
5. 验证：选择课程号和加分值后，回到主菜单选择 **13. 查看所有选课记录**，观察该课程的成绩是否正确变化（且不超过 100）。

#### 代码占位位置
- `database.py`：搜索 `课后作业 3：存储过程扩展`
- `main.py`：存储过程管理子菜单已预留选项 **7**

---

### 作业 4：函数 —— 百分制转 4.0 制 GPA

#### 目标
在 `database.py` 中补全 `create_func_gpa`、`call_func_gpa` 和 `demo_func_gpa_in_query` 方法，创建一个自定义函数 `fn_gpa(score)`：
- 将百分制成绩转换为 4.0 制 GPA。

#### 转换规则建议
| 成绩范围 | GPA |
|---------|-----|
| `score >= 90` | 4.0 |
| `score >= 85` | 3.7 |
| `score >= 82` | 3.3 |
| `score >= 78` | 3.0 |
| `score >= 75` | 2.7 |
| `score >= 72` | 2.3 |
| `score >= 68` | 2.0 |
| `score >= 64` | 1.5 |
| `score >= 60` | 1.0 |
| `score < 60`  | 0.0 |
| `NULL`        | `NULL` |

#### 涉及知识点
- 自定义标量函数的创建（`CREATE FUNCTION ... RETURNS ... DETERMINISTIC`）
- 多分支 `IF ... ELSEIF ... ELSE ... END IF`
- 在 `SELECT` 查询中调用自定义函数

#### 详细步骤引导
1. 打开 `database.py`，定位到 `create_func_gpa` 方法（在“课后作业 4”注释下方）。
2. 将 `query` 中的 `-- TODO` 替换为完整的 `CREATE FUNCTION` 语句，参照上表实现分支逻辑。
3. `call_func_gpa` 和 `demo_func_gpa_in_query` 已经给出完整 Python 框架，无需修改 SQL 调用部分，只需要确保 `create_func_gpa` 中的函数名与 SQL 一致即可。
4. 保存文件后，运行 `python main.py` → 选择 **21. 函数管理** → 选择 **6. 【课后作业】创建 GPA 转换函数**。
5. 验证：选择 **7. 【课后作业】调用 GPA 函数测试**，输入成绩查看转换结果；再选择 **8. 【课后作业】在查询中演示 GPA 函数**，查看所有学生的成绩与对应 GPA。

#### 代码占位位置
- `database.py`：搜索 `课后作业 4：函数扩展`
- `main.py`：函数管理子菜单已预留选项 **6、7、8**

---

### 作业 5：完整性约束 —— 手机号格式检查

#### 目标
在 `database.py` 中补全 `add_demo_phone_constraint` 方法，为 `students` 表的 `phone` 列动态添加一个 `CHECK` 约束：
- 要求 `phone` 必须是 **11 位数字**。
- 允许 `phone` 为空（即允许不填手机号）。

#### 涉及知识点
- `ALTER TABLE ... ADD CONSTRAINT ... CHECK (...)`
- MySQL 正则表达式（`REGEXP`）在 `CHECK` 约束中的应用（MySQL 8.0.16+）
- 逻辑或 `OR` 的使用：允许为空或符合格式

#### 详细步骤引导
1. 打开 `database.py`，定位到 `add_demo_phone_constraint` 方法（在“课后作业 5”注释下方）。
2. 将 `pass` 替换为对 `self.add_check_constraint(...)` 的调用：
   - 约束名：`'chk_phone_format'`
   - 表名：`'students'`
   - 条件：`"phone IS NULL OR phone REGEXP '^[0-9]{11}$'"`
3. 保存文件后，运行 `python main.py` → 选择 **22. 完整性约束管理** → 选择 **4. 【课后作业】添加手机号格式 CHECK 约束**。
4. 验证：尝试在主菜单 **1. 添加学生** 或 **4. 修改学生信息** 中输入非 11 位的手机号（如 `138001` 或 `138-0013-8001`），观察数据库是否抛出 `CHECK constraint violation` 错误。

#### 代码占位位置
- `database.py`：搜索 `课后作业 5：完整性约束扩展`
- `main.py`：完整性约束管理子菜单已预留选项 **4**

---

## 十一、参考答案与代码补全提示

以下给出五个课后作业的关键代码参考，供学生自查或教师课堂讲解使用。

### 作业1 参考答案：`create_view_student_credits`

```sql
CREATE OR REPLACE VIEW v_student_credits AS
SELECT
    s.student_id,
    s.name,
    SUM(c.credit) AS total_credits,
    AVG(sc.score) AS avg_score
FROM students s
LEFT JOIN sc ON s.student_id = sc.student_id AND sc.score IS NOT NULL
LEFT JOIN course c ON sc.course_id = c.course_id
GROUP BY s.student_id, s.name;
```

### 作业2 参考答案：`create_trigger_major_change_log`

```sql
-- 日志表
CREATE TABLE IF NOT EXISTS major_change_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    old_major VARCHAR(100),
    new_major VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 触发器
CREATE TRIGGER trg_after_student_major_change_log
AFTER UPDATE ON students
FOR EACH ROW
BEGIN
    IF OLD.major <> NEW.major THEN
        INSERT INTO major_change_log (student_id, old_major, new_major)
        VALUES (OLD.student_id, OLD.major, NEW.major);
    END IF;
END
```

### 作业3 参考答案：`sp_score_bonus`

```sql
CREATE PROCEDURE sp_score_bonus(IN p_course_id VARCHAR(20), IN p_bonus DECIMAL(5,2))
BEGIN
    UPDATE sc
    SET score = LEAST(score + p_bonus, 100)
    WHERE course_id = p_course_id AND score IS NOT NULL;
END
```

### 作业4 参考答案：`fn_gpa`

```sql
CREATE FUNCTION fn_gpa(score DECIMAL(5,2))
RETURNS DECIMAL(2,1)
DETERMINISTIC
BEGIN
    IF score IS NULL THEN RETURN NULL;
    ELSEIF score >= 90 THEN RETURN 4.0;
    ELSEIF score >= 85 THEN RETURN 3.7;
    ELSEIF score >= 82 THEN RETURN 3.3;
    ELSEIF score >= 78 THEN RETURN 3.0;
    ELSEIF score >= 75 THEN RETURN 2.7;
    ELSEIF score >= 72 THEN RETURN 2.3;
    ELSEIF score >= 68 THEN RETURN 2.0;
    ELSEIF score >= 64 THEN RETURN 1.5;
    ELSEIF score >= 60 THEN RETURN 1.0;
    ELSE RETURN 0.0;
    END IF;
END
```

### 作业5 参考答案：`add_demo_phone_constraint`

```python
def add_demo_phone_constraint(self):
    return self.add_check_constraint(
        'chk_phone_format',
        'students',
        "phone IS NULL OR phone REGEXP '^[0-9]{11}$'"
    )
```

---

## 十二、总结

本次扩展在保持学生选课管理系统**简洁易懂**的前提下，完整引入了五大类高级数据库对象的管理能力：

- **视图**：简化查询、封装统计逻辑；
- **触发器**：自动化规则检查与审计日志；
- **存储过程**：服务端复杂计算与排名/统计；
- **函数**：可复用的标量计算，直接在 SQL 中调用；
- **完整性约束**：动态维护数据的正确性与一致性。

所有新增功能均通过**中文注释**和**CLI 交互菜单**呈现，配合 `init_advanced.py` 一键初始化脚本，非常适合在课堂上进行**边讲边练**的沉浸式数据库教学。
