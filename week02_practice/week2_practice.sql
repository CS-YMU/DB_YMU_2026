-- =====================================================
-- DB实验02A：SQL查询1 - 完整环境搭建脚本
-- =====================================================

-- 1. 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS db_experiment_week02;
USE db_experiment_week02;

-- 2. 显示当前使用的数据库
SELECT CONCAT('当前使用数据库：', DATABASE()) AS '数据库信息';

-- 3. 删除已存在的表（注意顺序：先删子表，再删父表）
DROP TABLE IF EXISTS SC;
DROP TABLE IF EXISTS Course;
DROP TABLE IF EXISTS Student;

-- 4. 创建学生表
CREATE TABLE Student (
    Sno VARCHAR(10) PRIMARY KEY COMMENT '学号',
    Sname VARCHAR(20) NOT NULL COMMENT '姓名',
    Sage INT COMMENT '年龄',
    Sdept VARCHAR(20) COMMENT '系别'
);

-- 5. 创建课程表（自引用外键）
CREATE TABLE Course (
    Cno VARCHAR(10) PRIMARY KEY COMMENT '课程号',
    Cname VARCHAR(50) NOT NULL COMMENT '课程名',
    Credit INT COMMENT '学分',
    Cpno VARCHAR(10) COMMENT '先修课程号',
    FOREIGN KEY (Cpno) REFERENCES Course(Cno)
);

-- 6. 创建选课表（引用学生表和课程表）
CREATE TABLE SC (
    Sno VARCHAR(10) COMMENT '学号',
    Cno VARCHAR(10) COMMENT '课程号',
    Grade INT COMMENT '成绩',
    PRIMARY KEY (Sno, Cno),
    FOREIGN KEY (Sno) REFERENCES Student(Sno),
    FOREIGN KEY (Cno) REFERENCES Course(Cno)
);

-- 7. 插入学生数据
INSERT INTO Student VALUES 
('2021001', '张三', 20, 'CS'),
('2021002', '李四', 19, 'CS'),
('2021003', '王五', 21, 'MA'),
('2021004', '赵六', 18, 'CS'),
('2021005', '钱七', 22, 'PH');

-- 8. 按依赖顺序插入课程数据
-- 8.1 先插入没有先修课程的
INSERT INTO Course (Cno, Cname, Credit, Cpno) VALUES 
('3', '程序设计基础', 2, NULL),
('2', '数据结构', 3, NULL),
('7', '软件工程', 2, NULL);

-- 8.2 再插入有先修课程的
INSERT INTO Course (Cno, Cname, Credit, Cpno) VALUES 
('1', '数据库系统', 4, '3'),
('5', '计算机网络', 2, '2'),
('4', '操作系统', 3, '1'),
('6', '数据挖掘', 3, '1'),
('8', '数据分析', 4, '6'),
('9', '系统分析与设计', 3, '7'),
('10', '数据库原理_基础%', 2, '1');

-- 9. 插入选课数据
INSERT INTO SC VALUES 
('2021001', '1', 85),
('2021001', '2', 90),
('2021002', '1', 78),
('2021002', '3', 88),
('2021003', '1', 92),
('2021004', '4', 75),
('2021005', '5', 82);

-- -- =====================================================
-- -- 验证数据
-- -- =====================================================

-- SELECT '========================================' AS '';
-- SELECT '数据库环境搭建完成！' AS '状态';
-- SELECT '========================================' AS '';

-- SELECT '--- 学生表数据 ---' AS '';
-- SELECT * FROM Student;

-- SELECT '--- 课程表数据 ---' AS '';
-- SELECT * FROM Course;

-- SELECT '--- 选课表数据 ---' AS '';
-- SELECT * FROM SC;

-- SELECT '--- 选课详细信息（关联查询）---' AS '';
-- SELECT 
--     s.Sno AS 学号,
--     s.Sname AS 姓名,
--     s.Sdept AS 系别,
--     c.Cno AS 课程号,
--     c.Cname AS 课程名,
--     sc.Grade AS 成绩
-- FROM SC sc
-- JOIN Student s ON sc.Sno = s.Sno
-- JOIN Course c ON sc.Cno = c.Cno
-- ORDER BY s.Sno, c.Cno;

-- -- =====================================================
-- -- 实验2.1 - 2.16 查询语句
-- -- =====================================================

-- SELECT '========================================' AS '';
-- SELECT '开始执行实验查询...' AS '';
-- SELECT '========================================' AS '';

-- -- 2.1 查询所有课程
-- SELECT '2.1 查询所有课程：' AS '';
-- SELECT * FROM Course;

-- -- 2.2 查询所有课程，结果集的列为(ID, Name)
-- SELECT '2.2 查询所有课程(ID, Name)：' AS '';
-- SELECT Cno AS ID, Cname AS Name FROM Course;

-- -- 2.3 查询学生信息，结果集的列为(学号,姓名,年龄,年龄+1)
-- SELECT '2.3 查询学生信息(学号,姓名,年龄,年龄+1)：' AS '';
-- SELECT Sno AS 学号, Sname AS 姓名, Sage AS 年龄, Sage+1 AS 年龄加1 FROM Student;

-- -- 2.4 查询学分大于3的课程
-- SELECT '2.4 查询学分大于3的课程：' AS '';
-- SELECT * FROM Course WHERE Credit > 3;

-- -- 2.5 查询年龄大于18、CS系的男生
-- SELECT '2.5 查询年龄大于18、CS系的学生：' AS '';
-- SELECT * FROM Student WHERE Sage > 18 AND Sdept = 'CS';

-- -- 2.6 查询学分在[2,4]范围的课程信息
-- SELECT '2.6 查询学分在[2,4]范围的课程：' AS '';
-- SELECT * FROM Course WHERE Credit BETWEEN 2 AND 4;

-- -- 2.7 查询学分不在[2,4]范围的课程信息
-- SELECT '2.7 查询学分不在[2,4]范围的课程：' AS '';
-- SELECT * FROM Course WHERE Credit NOT BETWEEN 2 AND 4;

-- -- 2.8 查询课程名称以“数据”开始的课程
-- SELECT '2.8 查询课程名称以"数据"开始的课程：' AS '';
-- SELECT * FROM Course WHERE Cname LIKE '数据%';

-- -- 2.9 查询课程名中有“系统”的课程
-- SELECT '2.9 查询课程名中有"系统"的课程：' AS '';
-- SELECT * FROM Course WHERE Cname LIKE '%系统%';

-- -- 2.10 查询至少有3个字符的课程
-- SELECT '2.10 查询至少有3个字符的课程：' AS '';
-- SELECT * FROM Course WHERE CHAR_LENGTH(Cname) >= 3;

-- -- 2.11 查询课程名称第2个字符是“程”的课程
-- SELECT '2.11 查询课程名称第2个字符是"程"的课程：' AS '';
-- SELECT * FROM Course WHERE Cname LIKE '_程%';

-- -- 2.12 查询课程名称中有“%”、“_”或“\”字符的课程
-- SELECT '2.12 查询课程名称中有特殊字符的课程：' AS '';
-- SELECT * FROM Course WHERE Cname LIKE '%\%%' OR Cname LIKE '%\_%';

-- -- 2.13 查询课程代号为1、3、4或7的选修情况
-- SELECT '2.13 查询课程代号为1、3、4或7的选修情况：' AS '';
-- SELECT * FROM SC WHERE Cno IN ('1', '3', '4', '7');

-- -- 2.14 查询没有被选修的课程
-- SELECT '2.14 查询没有被选修的课程：' AS '';
-- SELECT Cno, Cname FROM Course WHERE Cno NOT IN (SELECT DISTINCT Cno FROM SC);

-- -- 2.15 查询没有先修课程的课程
-- SELECT '2.15 查询没有先修课程的课程：' AS '';
-- SELECT * FROM Course WHERE Cpno IS NULL;

-- -- 2.16 查询有先修课程、学分大于2的课程
-- SELECT '2.16 查询有先修课程、学分大于2的课程：' AS '';
-- SELECT * FROM Course WHERE Cpno IS NOT NULL AND Credit > 2;

-- SELECT '========================================' AS '';
-- SELECT '所有实验查询执行完成！' AS '';
-- SELECT '========================================' AS '';