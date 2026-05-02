-- ============================================================
-- 测试数据生成脚本（严格满足所有主键和唯一约束）
-- 适用：MySQL 5.7
-- 生成：专业5、教师15、课程25、学生200 + 全部关联
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE student_course;
TRUNCATE TABLE course_prerequisite;
TRUNCATE TABLE student_phone;
TRUNCATE TABLE student_major2;
TRUNCATE TABLE student_major1;
TRUNCATE TABLE teacher_course;
TRUNCATE TABLE course_leader;
TRUNCATE TABLE major_leader;
TRUNCATE TABLE teacher_major;
TRUNCATE TABLE student;
TRUNCATE TABLE course;
TRUNCATE TABLE teacher;
TRUNCATE TABLE major;
TRUNCATE TABLE dd_administrative_divisions;
TRUNCATE TABLE dd_professional_title;
TRUNCATE TABLE dd_sex;

SET FOREIGN_KEY_CHECKS = 1;

-- ==================== 1. 数据字典 ====================
INSERT INTO dd_sex (Code, Name) VALUES ('1', '男'), ('2', '女');  -- AID自增
INSERT INTO dd_professional_title (Code, Name, Level) VALUES
('01', '教授', 1), ('02', '副教授', 2), ('03', '讲师', 3),
('04', '助教', 4), ('05', '研究员', 1), ('06', '副研究员', 2);
INSERT INTO dd_administrative_divisions (Code, Name, Level, FatherCode, FullName, SimpleName) VALUES
('110000', '北京市', 1, NULL, '中华人民共和国北京市', '京'),
('110100', '北京市辖区', 2, '110000', '北京市市辖区', NULL),
('110105', '朝阳区', 3, '110100', '北京市朝阳区', NULL),
('110106', '丰台区', 3, '110100', '北京市丰台区', NULL),
('120000', '天津市', 1, NULL, '中华人民共和国天津市', '津'),
('120100', '天津市辖区', 2, '120000', '天津市市辖区', NULL),
('120101', '和平区', 3, '120100', '天津市和平区', NULL),
('310000', '上海市', 1, NULL, '中华人民共和国上海市', '沪'),
('310100', '上海市辖区', 2, '310000', '上海市市辖区', NULL),
('310115', '浦东新区', 3, '310100', '上海市浦东新区', NULL),
('440000', '广东省', 1, NULL, '中华人民共和国广东省', '粤'),
('440100', '广州市', 2, '440000', '广东省广州市', '穗'),
('440105', '海珠区', 3, '440100', '广州市海珠区', NULL);

-- ==================== 2. 专业 ====================
INSERT INTO major (Code, Name, Years) VALUES
('080901', '计算机科学与技术', 4.0),
('080902', '软件工程', 4.0),
('080910', '数据科学与大数据技术', 4.0),
('080903', '网络工程', 4.0),
('080904', '信息安全', 4.0);

-- ==================== 3. 教师（15人） ====================
-- 确保 Code 唯一且长度=8 (T+7位数字)
SET @row = 0;
INSERT INTO teacher (Code, Name, TitleAID)
SELECT 
    CONCAT('T', LPAD(@row := @row + 1, 7, '0')),
    CONCAT(ELT(1 + FLOOR(RAND()*10), '李','王','张','刘','陈','杨','赵','黄','周','吴'),
           ELT(1 + FLOOR(RAND()*10), '伟','芳','强','敏','磊','静','军','丽','勇','婷')),
    1 + FLOOR(RAND() * 6)
FROM (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION
      SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION
      SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15) AS nums;

-- ==================== 4. 课程（25门） ====================
INSERT INTO course (Code, Name, Hours, Credit) VALUES
('MATH101', '高等数学', 64, 4.0), ('MATH102', '线性代数', 48, 3.0), ('MATH201', '概率论与数理统计', 48, 3.0),
('PHY101', '大学物理', 64, 4.0), ('PHY102', '物理实验', 32, 1.5),
('CS101',  '程序设计基础', 48, 3.0), ('CS102', '面向对象编程', 48, 3.0), ('CS201', '数据结构', 64, 4.0),
('CS202', '算法设计与分析', 48, 3.0), ('CS203', '操作系统', 64, 4.0), ('CS204', '数据库原理', 48, 3.0),
('CS205', '计算机网络', 48, 3.0), ('CS301', '软件工程', 48, 3.0), ('CS302', '编译原理', 64, 4.0),
('CS303', '计算机组成原理', 64, 4.0), ('AI301', '人工智能导论', 48, 3.0), ('AI302', '机器学习', 48, 3.0),
('AI401', '深度学习', 48, 3.0), ('DS301', '大数据技术', 48, 3.0), ('DS302', '数据挖掘', 48, 3.0),
('SE301', 'Web开发技术', 48, 3.0), ('SE302', '移动应用开发', 48, 3.0), ('SE401', '软件测试', 32, 2.0),
('NET301', '网络安全', 48, 3.0), ('NET302', '物联网技术', 48, 3.0);

-- ==================== 5. 学生（200人） ====================
-- 生成数字辅助表 1..200
DROP TEMPORARY TABLE IF EXISTS temp_numbers;
CREATE TEMPORARY TABLE temp_numbers (n INT PRIMARY KEY);
SET @row = 0;
INSERT INTO temp_numbers (n)
SELECT @row := @row + 1 FROM 
(SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
(SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
(SELECT 0 UNION SELECT 1 UNION SELECT 2) c
LIMIT 200;

INSERT INTO student (Code, Name, SexAID, Birthday, YearInroll, AddressCVAID, AddressDetail)
SELECT 
    CONCAT(2021 + FLOOR(RAND() * 5), LPAD(n, 8, '0')),  -- 学号唯一（年份+固定宽度的序号）
    CONCAT(ELT(1 + FLOOR(RAND()*20), '李','王','张','刘','陈','杨','赵','黄','周','吴','徐','孙','马','朱','胡','郭','林','何','高','郑'),
           ELT(1 + FLOOR(RAND()*10), '宇','欣','伟','婷','磊','静','鹏','丽','浩','雅')),
    1 + IF(RAND() < 0.5, 0, 1),   -- 性别 AID 1或2
    DATE_SUB(CONCAT(2000 + FLOOR(RAND()*8), '-', LPAD(1 + FLOOR(RAND()*12),2,'0'), '-', LPAD(1 + FLOOR(RAND()*28),2,'0')), INTERVAL FLOOR(RAND()*100) DAY),
    2021 + FLOOR(RAND() * 5),
    1 + FLOOR(RAND() * 13),
    CONCAT('详细地址', n)
FROM temp_numbers;

-- ==================== 6. 关联表（严格满足唯一性） ====================
-- 6.1 学生主修专业（每个学生一个专业，主键 StudentAID 自动满足）
INSERT INTO student_major1 (StudentAID, MajorAID)
SELECT AID, 1 + FLOOR(RAND() * 5) FROM student;

-- 6.2 学生辅修专业（每个学生至多一个，主键 StudentAID 自动满足）
INSERT INTO student_major2 (StudentAID, MajorAID)
SELECT AID, 1 + FLOOR(RAND() * 5) FROM student WHERE RAND() < 0.3
ON DUPLICATE KEY UPDATE MajorAID = VALUES(MajorAID);

-- 6.3 学生电话（主键 PhoneNumber，随机生成几乎不重复，如有重复可忽略）
INSERT INTO student_phone (StudentAID, PhoneNumber, FlagType, IsCommonlyUsed)
SELECT 
    AID,
    CONCAT('1', FLOOR(3 + RAND() * 7), LPAD(FLOOR(RAND() * 100000000), 9, '0')),
    '2', b'1'
FROM student
UNION ALL
SELECT 
    AID,
    CONCAT('1', FLOOR(3 + RAND() * 7), LPAD(FLOOR(RAND() * 100000000), 9, '0')),
    ELT(1 + FLOOR(RAND() * 3), '0','1','3'), b'0'
FROM student WHERE RAND() < 0.5
ON DUPLICATE KEY UPDATE PhoneNumber = PhoneNumber;  -- 避免主键冲突（简单跳过）

-- 6.4 课程负责人（每门课程一个负责人，LeaderAID 唯一 -> 每个教师只能负责一门课）
-- 方法：随机取出最多 min(课程数, 教师数) 条记录，保证教师不重复
DROP TEMPORARY TABLE IF EXISTS tmp_courses_shuffle;
CREATE TEMPORARY TABLE tmp_courses_shuffle AS
SELECT AID, @cseq := @cseq + 1 AS seq FROM course, (SELECT @cseq := 0) init ORDER BY RAND() LIMIT 15;

DROP TEMPORARY TABLE IF EXISTS tmp_teachers_shuffle;
CREATE TEMPORARY TABLE tmp_teachers_shuffle AS
SELECT AID, @tseq := @tseq + 1 AS seq FROM teacher, (SELECT @tseq := 0) init ORDER BY RAND() LIMIT 15;

INSERT INTO course_leader (CourseAID, LeaderAID)
SELECT c.AID, t.AID
FROM tmp_courses_shuffle c JOIN tmp_teachers_shuffle t ON c.seq = t.seq;

-- 6.5 专业负责人（每个专业一个负责人，LeaderAID 唯一）
DROP TEMPORARY TABLE IF EXISTS tmp_major_teachers;
CREATE TEMPORARY TABLE tmp_major_teachers AS
SELECT AID, @mseq := @mseq + 1 AS seq FROM teacher, (SELECT @mseq := 0) init ORDER BY RAND() LIMIT 5;

INSERT INTO major_leader (MajorAID, LeaderAID)
SELECT m.AID, t.AID
FROM major m JOIN tmp_major_teachers t ON m.AID = t.seq;  -- major AID 为 1~5

-- 6.6 教师讲授课程（主键 CourseAID，确保每门课一个教师）
INSERT INTO teacher_course (CourseAID, TeacherAID)
SELECT AID, 1 + FLOOR(RAND() * 15) FROM course
ON DUPLICATE KEY UPDATE TeacherAID = VALUES(TeacherAID);  -- 实际不会重复，但保险

-- 6.7 教师所属专业（主键 TeacherAID，每个教师一个专业）
INSERT INTO teacher_major (TeacherAID, MajorAID)
SELECT AID, 1 + FLOOR(RAND() * 5) FROM teacher;

-- 6.8 课程先修关系（复合主键，无重复）
INSERT INTO course_prerequisite (CourseAID, PreCourseAID) VALUES
(7, 6), (9, 7), (10, 7), (11, 7), (12, 6), (16, 9), (17, 16), (18, 17), (19, 11), (20, 19);

-- 6.9 学生选课（唯一索引 (StudentAID, CourseAID)）
DROP TEMPORARY TABLE IF EXISTS tmp_student_course;
CREATE TEMPORARY TABLE tmp_student_course (
    StudentAID INT,
    CourseAID INT,
    PRIMARY KEY (StudentAID, CourseAID)
);

-- 为每个学生随机选择 5~12 门不同的课程
SET @row_number = 0;
SET @prev_student = NULL;
INSERT IGNORE INTO tmp_student_course (StudentAID, CourseAID)
SELECT StudentAID, CourseAID FROM (
    SELECT 
        s.AID AS StudentAID,
        c.AID AS CourseAID,
        @row_number := IF(@prev_student = s.AID, @row_number + 1, 1) AS rn,
        @prev_student := s.AID
    FROM student s
    CROSS JOIN course c
    CROSS JOIN (SELECT @row_number := 0, @prev_student := NULL) init
    ORDER BY s.AID, RAND()
) AS ranked
WHERE rn <= 5 + FLOOR(RAND() * 8);

-- 插入选课数据，生成成绩等
INSERT INTO student_course (StudentAID, CourseAID, ForMajor, RegistDate, AcademicYear, Semester, Score)
SELECT 
    t.StudentAID,
    t.CourseAID,
    IF(EXISTS(
        SELECT 1 FROM teacher_course tc 
        JOIN teacher_major tm ON tc.TeacherAID = tm.TeacherAID
        WHERE tc.CourseAID = t.CourseAID AND tm.MajorAID = sm.MajorAID
    ), IF(RAND() < 0.8, b'1', b'0'), IF(RAND() < 0.3, b'1', b'0')) AS ForMajor,
    DATE_ADD(MAKEDATE((SELECT YearInroll FROM student WHERE AID = t.StudentAID) + FLOOR(RAND() * 4), 1), INTERVAL FLOOR(RAND() * 365) DAY) AS RegistDate,
    (SELECT YearInroll FROM student WHERE AID = t.StudentAID) + FLOOR(RAND() * 4) AS AcademicYear,
    IF(RAND() < 0.5, b'0', b'1') AS Semester,
    CASE 
        WHEN RAND() < 0.1 THEN 50 + RAND() * 9
        WHEN RAND() < 0.3 THEN NULL
        ELSE 60 + RAND() * 40
    END AS Score
FROM tmp_student_course t
JOIN student_major1 sm ON t.StudentAID = sm.StudentAID
ON DUPLICATE KEY UPDATE Score = VALUES(Score);   -- 防止唯一键冲突

-- 清理临时表
DROP TEMPORARY TABLE IF EXISTS temp_numbers;
DROP TEMPORARY TABLE IF EXISTS tmp_courses_shuffle;
DROP TEMPORARY TABLE IF EXISTS tmp_teachers_shuffle;
DROP TEMPORARY TABLE IF EXISTS tmp_major_teachers;
DROP TEMPORARY TABLE IF EXISTS tmp_student_course;

-- ==================== 验证数据量 ====================
SELECT '专业' AS `表`, COUNT(*) AS `记录数` FROM major
UNION SELECT '课程', COUNT(*) FROM course
UNION SELECT '教师', COUNT(*) FROM teacher
UNION SELECT '学生', COUNT(*) FROM student
UNION SELECT '选课记录', COUNT(*) FROM student_course;