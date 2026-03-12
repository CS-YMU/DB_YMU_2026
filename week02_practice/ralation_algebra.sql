
-- 1. 创建学生信息库（数据库）
CREATE DATABASE IF NOT EXISTS student_info_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 2. 使用该数据库
USE student_info_db;

-- 3. 创建 Student 表
CREATE TABLE Student (
    ID VARCHAR(20) NOT NULL COMMENT '学号',
    Name VARCHAR(50) NOT NULL COMMENT '姓名',
    Sex ENUM('男', '女') NOT NULL COMMENT '性别',
    Age INT COMMENT '年龄',
    Dept VARCHAR(50) NOT NULL COMMENT '系别',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

-- 4. 插入图片中的数据
INSERT INTO Student (ID, Name, Sex, Age, Dept) VALUES
('200215121', '李勇', '男', 20, 'CS'),
('200215122', '刘晨', '女', 19, 'CS'),
('200215123', '王敏', '女', 18, 'MA'),
('200215125', '张立', '男', 19, 'IS');

-- 5. 验证数据
SELECT * FROM Student;

-- 6. 创建 Course 表
CREATE TABLE IF NOT EXISTS Course (
    ID VARCHAR(10) NOT NULL COMMENT '课程编号',
    Name VARCHAR(100) NOT NULL COMMENT '课程名称',
    Credit INT COMMENT '学分',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- 7. 插入一些示例数据（包含学分=3的课程）
INSERT INTO Course (ID, Name, Credit) VALUES
('C001', '数据库系统概论', 4),
('C002', '数据结构', 3),
('C003', '高等数学', 5),
('C004', '计算机网络', 3),
('C005', '操作系统', 4),
('C006', '软件工程', 3);

-- 8. 查看所有课程
SELECT * FROM Course;

SELECT * FROM student_info_db.Student;

INSERT INTO Student (ID, Name, Sex, Age, Dept) VALUES
('200215121', '李勇', '男', 20, 'CS'),
('200215122', '刘晨', '女', 19, 'CS'),
('200215123', '王敏', '女', 18, 'MA'),
('200215125', '张立', '男', 19, 'IS');

SELECT Name, Dept FROM Student where Dept='CS' and Age>18 or age>20;
-- 查询 Name 和 Age，只返回前 3 条记录
SELECT Name, Age FROM Student LIMIT 3;
