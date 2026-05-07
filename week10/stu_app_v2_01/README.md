# DB06 数据库应用系统

基于 Flask + MySQL 的数据库教学演示系统，实现了一个完整的学生选课管理 Web 应用。

---

## 环境配置

### 1. 创建 conda 环境

```bash
conda create -n db06 python=3.12
conda activate db06
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

---

## 系统介绍

本系统采用 **三层架构**：

```
┌─────────────────────────────────────────────────────┐
│  表现层 (Flask + HTML模板)                          │
│  routes: /students, /courses, /lab/task1, /lab/task2│
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│  中间件层 (Database 类)                             │
│  封装所有 SQL 操作，统一数据访问接口                 │
│  - get_all_students()                              │
│  - call_fn_get_total_credit()                      │
│  - call_sp_course_stat()                           │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│  数据层 (MySQL - DB06)                             │
│  student / course / student_course 表              │
│  fn_GetTotalCreditBySID 函数                       │
│  sp_CourseStat 存储过程                            │
│  trg_grade_check 触发器                           │
└─────────────────────────────────────────────────────┘
```

### 核心功能模块

| 路由 | 功能 | 演示的知识点 |
|------|------|-------------|
| `/students` | 学生列表 + 总学分统计 | 嵌入式 SQL + 函数调用 |
| `/courses` | 课程列表 + 先修课信息 | LEFT JOIN 自连接 |
| `/course/<id>/stat` | 课程统计（平均分/最高分/及格人数） | 存储过程调用 |
| `/lab/task1` | 任务1在线评测 | 自定义函数 |
| `/lab/task2` | 任务2在线评测 | 存储过程 |

---

## 系统启动

### 步骤1：初始化数据库

```bash
python init_db.py
```

输出示例：
```
============================================================
DB06 数据库应用系统 —— 数据库初始化
============================================================
SQL 文件路径: ../DB06数据库应用系统260504/dbsc.sql
正在创建数据库 DB06...
数据库 DB06 创建成功
正在执行 SQL 文件: ../DB06数据库应用系统260504/dbsc.sql
SQL 文件执行完成
数据库连接成功: localhost/DB06
函数 fn_GetTotalCreditBySID 创建完成
存储过程 sp_CourseStat 创建完成
触发器 trg_grade_check 创建完成
数据库连接已关闭
============================================================
初始化完成！
============================================================
```

### 步骤2：启动 Web 应用

```bash
flask run --debug --port 8080
```

或使用 Python 直接运行：

```bash
python app.py
```

访问 http://localhost:8080 即可使用系统。

---

## 作业任务

### 任务1：编写函数统计学生总学分（50分）

**题目要求**：创建自定义函数 `fn_GetTotalCreditBySID`，统计指定学生已获得的总学分。

**规则**：
- 只统计成绩 >= 60 的课程
- 使用 `SUM` + 多表连接（student_course + course）
- 无记录时返回 0

**参考答案**：

```sql
CREATE FUNCTION fn_GetTotalCreditBySID(p_sid INT)
RETURNS DECIMAL(5,1)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_credit DECIMAL(5,1) DEFAULT 0;
    SELECT IFNULL(SUM(c.Credit), 0) INTO total_credit
    FROM student_course sc
    JOIN course c ON sc.CourseID = c.ID
    WHERE sc.StudentID = p_sid AND sc.Grade >= 60;
    RETURN total_credit;
END
```

**测试用例**：

| 学号 | 姓名 | 预期结果 | 说明 |
|------|------|----------|------|
| 200215121 | 李勇 | 10.0 | 3门及格（数据库4.0 + 数学2.0 + 信息系统4.0） |
| 200215122 | 刘晨 | 6.0 | 2门及格（数据库4.0 + 数学2.0） |
| 200215125 | 张立 | 0 | 无选课记录 |
| 999999 | 不存在 | 0 | 不存在的学号 |

**完成方式**：在 http://localhost:8080/lab/task1 页面提交 SQL，系统自动评分。

---

### 任务2：编写存储过程统计课程情况（50分）

**题目要求**：创建存储过程 `sp_CourseStat`，统计指定课程的修读情况。

**规则**：
- 输入参数：课程ID
- 输出5个统计值：平均分、最高分、最低分、及格人数、总人数
- 使用 SELECT ... INTO 语句

**参考答案**：

```sql
CREATE PROCEDURE sp_CourseStat(
    IN  p_cid INT,
    OUT out_avg_grade DECIMAL(5,2),
    OUT out_max_grade DECIMAL(5,2),
    OUT out_min_grade DECIMAL(5,2),
    OUT out_pass_num INT,
    OUT out_total_num INT
)
BEGIN
    SELECT
        IFNULL(AVG(Grade), 0),
        IFNULL(MAX(Grade), 0),
        IFNULL(MIN(Grade), 0),
        IFNULL(SUM(CASE WHEN Grade >= 60 THEN 1 ELSE 0 END), 0),
        COUNT(*)
    INTO
        out_avg_grade, out_max_grade, out_min_grade,
        out_pass_num, out_total_num
    FROM student_course
    WHERE CourseID = p_cid;
END
```

**完成方式**：在 http://localhost:8080/lab/task2 页面提交 SQL，系统自动评分。

---

## 学生完成任务的步骤

### 1. 环境准备

```bash
# 创建并激活环境
conda create -n db06 python=3.12
conda activate db06

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

确认看到以下输出：
```
函数 fn_GetTotalCreditBySID 创建完成
存储过程 sp_CourseStat 创建完成
触发器 trg_grade_check 创建完成
```

### 3. 启动应用

```bash
flask run --debug --port 8080
```

### 4. 访问并验证

打开浏览器访问 http://localhost:8080

- 点击 **学生列表**：查看学生及其总学分（调用了 fn_GetTotalCreditBySID 函数）
- 点击 **课程统计**：查看课程的平均分、最高分等（调用了 sp_CourseStat 存储过程）

### 5. 完成作业评测

1. 访问 http://localhost:8080/lab/task1 （任务1：自定义函数）
2. 访问 http://localhost:8080/lab/task2 （任务2：存储过程）
3. 在编辑器中输入对应的 SQL 语句
4. 点击提交，系统自动判分

### 6. 验证函数/存储过程正确性

也可以在 MySQL 客户端直接验证：

```bash
mysql -u dylan -pP@ssw0rd DB06

# 测试函数
SELECT fn_GetTotalCreditBySID(200215121);  -- 应返回 10.0

# 测试存储过程
CALL sp_CourseStat(1, @avg, @max, @min, @pass, @total);
SELECT @avg, @max, @min, @pass, @total;
```

---

## 数据库表结构

### student（学生表）

| 字段 | 类型 | 说明 |
|------|------|------|
| ID | INT | 学号（主键） |
| Name | VARCHAR | 姓名 |
| Sex | VARCHAR | 性别 |
| Age | INT | 年龄 |
| Dept | VARCHAR | 系别 |
| RID | VARCHAR | 身份证号 |

### course（课程表）

| 字段 | 类型 | 说明 |
|------|------|------|
| ID | INT | 课程号（主键） |
| Name | VARCHAR | 课程名 |
| PID | INT | 先修课ID（自引用） |
| Credit | DECIMAL | 学分 |

### student_course（选课表）

| 字段 | 类型 | 说明 |
|------|------|------|
| StudentID | INT | 学号（外键→student.ID） |
| CourseID | INT | 课程号（外键→course.ID） |
| Grade | DECIMAL | 成绩（0-100） |

---

## 常见问题

### Q: 运行 init_db.py 报错 "FUNCTION does not exist"

A: 确保使用的是 conda 环境中的 Python：
```bash
conda activate db06
/opt/anaconda3/bin/python init_db.py
```

### Q: 启动应用后访问页面报错连接数据库

A: 检查 config.py 中的数据库配置是否正确：
- host: localhost
- user: dylan
- password: P@ssw0rd
- database: DB06

### Q: 任务提交后显示语法错误但 SQL 在客户端可以执行

A: 这是因为 mysql-connector 处理多行 SQL 时的问题。确保提交的 SQL 语句格式正确，或使用单行格式提交。
