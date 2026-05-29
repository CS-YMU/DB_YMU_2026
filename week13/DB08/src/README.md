# DB08: 数据库存储技术与索引优化

基于 MySQL `employees` 示例数据库的 Streamlit 交互式教学演示程序。

---

## 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
  - [1. 创建 Conda 环境](#1-创建-conda-环境)
  - [2. 安装依赖](#2-安装依赖)
  - [3. 配置数据库连接](#3-配置数据库连接)
  - [4. 导入示例数据库](#4-导入示例数据库)
  - [5. 启动应用](#5-启动应用)
- [项目结构](#项目结构)
- [功能说明](#功能说明)
- [课程对应](#课程对应)

---

## 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.10+ |
| MySQL | 5.7+ / 8.0+ |
| Conda | 最新版（推荐） |

---

## 快速开始

### 1. 创建 Conda 环境

```bash
conda create -n db08 python=3.12 -y
conda activate db08
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

`requirements.txt` 内容：

```text
streamlit>=1.28.0
pymysql>=1.1.0
cryptography>=41.0.0
pandas>=2.0.0
matplotlib>=3.7.0
graphviz>=0.20.0
```

### 3. 配置数据库连接

编辑 `config.py`，填入你的 MySQL 账号密码：

```python
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'dylan'),              # ← 改成你的用户名
    'password': os.getenv('DB_PASSWORD', ''),   # ← 改成你的密码
    'database': os.getenv('DB_DATABASE', 'DB08'),       # ← 数据库名
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'use_unicode': True,
}
```

> **提示**：支持通过环境变量覆盖配置，例如：
> ```bash
> export DB_USER=root
> export DB_PASSWORD='你的密码'
> streamlit run app.py
> ```

### 4. 导入示例数据库

确保 MySQL 服务已启动，在 `src/` 目录下执行：

```bash
# 替换数据库名为 DB08 后导入
sed 's/`employees`/`DB08`/g' employees.sql > db08.sql
mysql -u dylan -p < db08.sql
```

> 如果你已经有 `db08.sql`，直接执行：
> ```bash
> mysql -u dylan -p < db08.sql
> ```

导入成功后，MySQL 中会出现 `DB08` 数据库，包含 6 张表：

| 表名 | 说明 | 记录数 |
|------|------|--------|
| `employees` | 员工基本信息 | ~30万 |
| `departments` | 部门信息 | 9 |
| `dept_emp` | 员工-部门关系 | ~33万 |
| `dept_manager` | 部门经理 | 24 |
| `salaries` | 薪资记录 | ~284万 |
| `titles` | 职位记录 | ~44万 |

### 5. 启动应用

```bash
streamlit run app.py
```

默认在浏览器打开：`http://localhost:8501`

启动后，点击侧边栏「测试连接」验证数据库是否连通。

---

## 项目结构

```
DB08/src/
├── app.py                          # 主入口（页面导航 + 连接测试）
├── config.py                       # 数据库连接配置
├── db_config.py                    # 数据库操作封装（查询/EXPLAIN/DDL）
├── requirements.txt                # Python 依赖清单
├── README.md                       # 本文件
└── pages/                          # 子页面目录
    ├── 01_数据库概览.py             # 表结构、索引、数据统计
    ├── 02_EXPLAIN分析工具.py        # 自由输入 SQL 分析执行计划
    ├── 03_任务1_索引性能对比.py      # 有无索引性能差异实验
    ├── 04_任务2_最左前缀法则.py      # 联合索引验证与失效场景
    ├── 05_任务3_SQL写法对比.py      # 子查询/窗口函数/LIMIT 对比
    ├── 06_课件通俗讲解.py            # 按 DB08_MD_课件.md 15 节通俗讲解
    ├── 07_索引结构互动演示.py        # 稠密/稀疏/辅助/B+树/哈希/位图索引演示
    ├── 08_作业与实验训练.py          # 作业题拆解、记录长度、索引维护模拟
    └── 09_p5动画案例.py              # p5.js 动画演示块读取、B+树、哈希、位图
```

---

## 功能说明

| 页面 | 功能描述 | 对应实验 |
|------|----------|----------|
| **数据库概览** | 查看 6 张表的字段结构、索引列表、数据量与存储空间统计 | 实验准备 |
| **EXPLAIN 分析工具** | 输入任意 SELECT 语句，查看并解读 MySQL 执行计划 | 实验准备二 |
| **任务1: 索引性能对比** | 对 `last_name` 创建/删除索引，对比等值查询、范围查询、覆盖索引的执行计划差异 | 任务1 (40分) |
| **任务2: 最左前缀法则** | 验证联合索引最左前缀法则（完整匹配、最左列、跳过列、顺序调整），演示索引失效场景（范围查询后列失效、隐式类型转换、LIKE 前导%、OR 条件） | 任务2 (30分) |
| **任务3: SQL 写法对比** | 用子查询、窗口函数 `RANK()`、`ORDER BY + LIMIT` 三种方式查询最高薪员工，对比执行计划 | 任务3 (30分) |
| **课件通俗讲解** | 严格按 `DB08_MD_课件.md`：为什么需要存储技术、逻辑/物理、MySQL 存储方式、数据块、记录、块组织、表组织、索引、高频题、总结 | 课件理论 |
| **索引结构互动演示** | 用学生表案例演示稠密索引、稀疏索引、多级索引、辅助索引、B+树、哈希索引、位图索引 | 课件理论 |
| **作业与实验训练** | 拆解作业 08 的文件策略、记录长度计算、索引查询模拟、索引维护模拟 | 作业08 |
| **p5动画案例** | 使用 p5.js 动画演示按块读取、定长/变长记录、B+树范围查询、哈希冲突、位图 AND | 课堂演示 |

---

## 课程对应

- **课件**：第8讲 — 关系数据库存储技术
- **作业**：DB作业08 — 数据库存储技术
- **实验**：DB实验08 — 索引（MySQL数据库性能优化）
