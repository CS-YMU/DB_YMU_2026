# 学生选课管理系统 —— DB05 数据库对象说明

本文档对应 `DB05课外练习案例/` 中的 `dbsample.sql` 和 `生成测试数据.sql`。

## 基础表

系统以 DB05 示例 SQL 的 16 张表为基础：

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

为覆盖原始业务描述，完整业务版补充 2 张关系表：

```text
major_course
teacher_guidance
```

## 高级对象

`init_advanced.py` 和主菜单 25-29 提供教学演示用对象，均基于 DB05 的真实表名：

| 类型 | 名称 | 作用 |
|------|------|------|
| 视图 | `v_student_scores` | 学生、主修专业、课程、成绩明细 |
| 视图 | `v_course_stats` | 每门课选课人数、平均分、最高分、最低分 |
| 视图 | `v_student_credits` | 每个学生已录入成绩课程的学分与平均分 |
| 触发器 | `trg_before_sc_score_check` | 插入选课成绩前检查 0-100 |
| 触发器 | `trg_before_sc_score_update_check` | 更新成绩前检查 0-100 |
| 存储过程 | `sp_student_rank` | 按平均成绩计算学生排名 |
| 存储过程 | `sp_course_pass_rate` | 计算课程及格率 |
| 存储过程 | `sp_score_bonus` | 对某课程成绩统一加分，上限 100 |
| 函数 | `fn_grade_level(score)` | 百分制成绩转等级 |
| 函数 | `fn_gpa(score)` | 百分制成绩转 GPA |

## 约束口径

案例 SQL 的外键删除策略是 `ON DELETE RESTRICT`，更新策略是 `ON UPDATE CASCADE`。应用层删除学生时会先清理 `student_course`、`student_phone`、`student_major1`、`student_major2` 中的依赖记录；其他实体若仍被引用，则保持由 MySQL 拒绝删除。

高级对象只创建视图、触发器、存储过程和函数，不创建额外业务基础表。动态添加/删除对象的菜单会校验表名、视图名、触发器名、过程名和函数名，避免把任意输入拼接到对象名位置。
