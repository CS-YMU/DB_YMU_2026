-- =====================================================
-- Week04 Theory: 数据库完整性实验库
-- 适用于 MySQL 8
-- =====================================================

-- 1. 创建数据库
DROP DATABASE IF EXISTS week04_theory;
CREATE DATABASE week04_theory
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 2. 使用数据库
USE week04_theory;

-- =====================================================
-- 3. 学生表 Student
-- 演示：
-- PRIMARY KEY / NOT NULL / CHECK / DEFAULT
-- =====================================================
CREATE TABLE Student (
    ID VARCHAR(20) NOT NULL COMMENT '学号',
    Name VARCHAR(50) NOT NULL COMMENT '姓名',
    Sex ENUM('男', '女') NOT NULL COMMENT '性别',
    Age INT DEFAULT 18 COMMENT '年龄',
    Dept VARCHAR(50) NOT NULL COMMENT '院系',
    PRIMARY KEY (ID),
    CHECK (Age >= 15 AND Age <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

-- =====================================================
-- 4. 课程表 Course
-- 演示：
-- PRIMARY KEY / UNIQUE / CHECK
-- =====================================================
CREATE TABLE Course (
    CourseID VARCHAR(10) NOT NULL COMMENT '课程号',
    CourseName VARCHAR(100) NOT NULL COMMENT '课程名',
    Credit INT NOT NULL DEFAULT 2 COMMENT '学分',
    Teacher VARCHAR(50) COMMENT '任课教师',
    PRIMARY KEY (CourseID),
    UNIQUE (CourseName),
    CHECK (Credit >= 1 AND Credit <= 10)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- =====================================================
-- 5. 选课表 SC
-- 演示：
-- 复合主键 / 外键 / CHECK / CASCADE
-- =====================================================
CREATE TABLE SC (
    StudentID VARCHAR(20) NOT NULL COMMENT '学号',
    CourseID VARCHAR(10) NOT NULL COMMENT '课程号',
    Grade INT COMMENT '成绩',
    PRIMARY KEY (StudentID, CourseID),
    FOREIGN KEY (StudentID)
        REFERENCES Student(ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (CourseID)
        REFERENCES Course(CourseID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (Grade IS NULL OR (Grade >= 0 AND Grade <= 100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选课表';

-- =====================================================
-- 6. 班级表 Class
-- 演示：
-- 主键 / 唯一 / 非空
-- =====================================================
CREATE TABLE Class (
    ClassID VARCHAR(10) NOT NULL COMMENT '班级编号',
    ClassName VARCHAR(50) NOT NULL COMMENT '班级名称',
    GradeYear INT NOT NULL COMMENT '年级',
    PRIMARY KEY (ClassID),
    UNIQUE (ClassName),
    CHECK (GradeYear >= 2020 AND GradeYear <= 2100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级表';

-- =====================================================
-- 7. 学生班级关系表 StudentClass
-- 演示：
-- 外键 / RESTRICT
-- =====================================================
CREATE TABLE StudentClass (
    StudentID VARCHAR(20) NOT NULL COMMENT '学号',
    ClassID VARCHAR(10) NOT NULL COMMENT '班级编号',
    EnrollDate DATE NOT NULL COMMENT '入班日期',
    PRIMARY KEY (StudentID),
    FOREIGN KEY (StudentID)
        REFERENCES Student(ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (ClassID)
        REFERENCES Class(ClassID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生班级表';

-- =====================================================
-- 8. 系主任表 Advisor
-- 演示：
-- UNIQUE / NOT NULL
-- =====================================================
CREATE TABLE Advisor (
    AdvisorID VARCHAR(10) NOT NULL COMMENT '教师编号',
    AdvisorName VARCHAR(50) NOT NULL COMMENT '教师姓名',
    Phone VARCHAR(20) UNIQUE COMMENT '电话',
    Dept VARCHAR(50) NOT NULL COMMENT '所属院系',
    PRIMARY KEY (AdvisorID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='导师表';

-- =====================================================
-- 9. 学生导师表 StudentAdvisor
-- 演示：
-- SET NULL
-- =====================================================
CREATE TABLE StudentAdvisor (
    StudentID VARCHAR(20) NOT NULL COMMENT '学号',
    AdvisorID VARCHAR(10) COMMENT '导师编号',
    PRIMARY KEY (StudentID),
    FOREIGN KEY (StudentID)
        REFERENCES Student(ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (AdvisorID)
        REFERENCES Advisor(AdvisorID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生导师表';

-- =====================================================
-- 10. 宿舍表 Dormitory
-- 演示：
-- 主键 / 唯一 / CHECK
-- =====================================================
CREATE TABLE Dormitory (
    DormID VARCHAR(10) NOT NULL COMMENT '宿舍编号',
    Building VARCHAR(20) NOT NULL COMMENT '楼栋',
    RoomNo VARCHAR(20) NOT NULL COMMENT '房间号',
    Capacity INT NOT NULL DEFAULT 4 COMMENT '容量',
    PRIMARY KEY (DormID),
    UNIQUE (Building, RoomNo),
    CHECK (Capacity >= 1 AND Capacity <= 8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='宿舍表';

-- =====================================================
-- 11. 学生住宿表 StudentDorm
-- 演示：
-- 一对一/多对一关系 / SET NULL
-- =====================================================
CREATE TABLE StudentDorm (
    StudentID VARCHAR(20) NOT NULL COMMENT '学号',
    DormID VARCHAR(10) COMMENT '宿舍编号',
    CheckInDate DATE,
    PRIMARY KEY (StudentID),
    FOREIGN KEY (StudentID)
        REFERENCES Student(ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (DormID)
        REFERENCES Dormitory(DormID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生住宿表';

-- =====================================================
-- 12. 插入测试数据
-- =====================================================

INSERT INTO Student (ID, Name, Sex, Age, Dept) VALUES
('2024001', '张三', '男', 19, 'CS'),
('2024002', '李四', '女', 20, 'CS'),
('2024003', '王五', '男', 18, 'MA'),
('2024004', '赵六', '女', 21, 'IS'),
('2024005', '钱七', '男', 22, 'EE');

INSERT INTO Course (CourseID, CourseName, Credit, Teacher) VALUES
('C001', '数据库原理', 4, '刘老师'),
('C002', '数据结构', 3, '王老师'),
('C003', '高等数学', 5, '陈老师'),
('C004', '计算机网络', 3, '张老师');

INSERT INTO SC (StudentID, CourseID, Grade) VALUES
('2024001', 'C001', 92),
('2024001', 'C002', 85),
('2024002', 'C001', 88),
('2024002', 'C004', 90),
('2024003', 'C003', 95),
('2024004', 'C002', 76),
('2024005', 'C004', 84);

INSERT INTO Class (ClassID, ClassName, GradeYear) VALUES
('CL01', '计算机241班', 2024),
('CL02', '数学241班', 2024),
('CL03', '信息241班', 2024);

INSERT INTO StudentClass (StudentID, ClassID, EnrollDate) VALUES
('2024001', 'CL01', '2024-09-01'),
('2024002', 'CL01', '2024-09-01'),
('2024003', 'CL02', '2024-09-01'),
('2024004', 'CL03', '2024-09-01'),
('2024005', 'CL03', '2024-09-01');

INSERT INTO Advisor (AdvisorID, AdvisorName, Phone, Dept) VALUES
('T001', '周老师', '13800000001', 'CS'),
('T002', '吴老师', '13800000002', 'MA'),
('T003', '郑老师', '13800000003', 'IS');

INSERT INTO StudentAdvisor (StudentID, AdvisorID) VALUES
('2024001', 'T001'),
('2024002', 'T001'),
('2024003', 'T002'),
('2024004', 'T003'),
('2024005', 'T003');

INSERT INTO Dormitory (DormID, Building, RoomNo, Capacity) VALUES
('D001', '1栋', '101', 4),
('D002', '1栋', '102', 4),
('D003', '2栋', '201', 6);

INSERT INTO StudentDorm (StudentID, DormID, CheckInDate) VALUES
('2024001', 'D001', '2024-09-02'),
('2024002', 'D001', '2024-09-02'),
('2024003', 'D002', '2024-09-02'),
('2024004', 'D003', '2024-09-02'),
('2024005', 'D003', '2024-09-02');Course