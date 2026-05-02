/*
 Navicat Premium Dump SQL

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 80023 (8.0.23)
 Source Host           : localhost:3306
 Source Schema         : dbsample

 Target Server Type    : MySQL
 Target Server Version : 80023 (8.0.23)
 File Encoding         : 65001

 Date: 28/04/2026 18:39:15
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for course
-- ----------------------------
DROP TABLE IF EXISTS `course`;
CREATE TABLE `course`  (
  `AID` int NOT NULL AUTO_INCREMENT COMMENT '课程AID',
  `Code` char(10) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '代码',
  `Name` varchar(50) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '名称',
  `Hours` smallint NOT NULL DEFAULT 0 COMMENT '学时',
  `Credit` decimal(3, 1) NOT NULL DEFAULT 0.0 COMMENT '学分',
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`Code` ASC) USING BTREE,
  CONSTRAINT `CHECK_Credit` CHECK (`Credit` >= 0),
  CONSTRAINT `CHECK_Hours` CHECK (`Hours` >= 0)
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '课程' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for course_leader
-- ----------------------------
DROP TABLE IF EXISTS `course_leader`;
CREATE TABLE `course_leader`  (
  `CourseAID` int NOT NULL COMMENT '课程AID',
  `LeaderAID` int NOT NULL COMMENT '负责人教师AID',
  PRIMARY KEY (`CourseAID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`LeaderAID` ASC) USING BTREE,
  CONSTRAINT `Course_Leader_FK_1` FOREIGN KEY (`CourseAID`) REFERENCES `course` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Course_Leader_FK_2` FOREIGN KEY (`LeaderAID`) REFERENCES `teacher` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '课程负责人' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for course_prerequisite
-- ----------------------------
DROP TABLE IF EXISTS `course_prerequisite`;
CREATE TABLE `course_prerequisite`  (
  `CourseAID` int NOT NULL COMMENT '课程AID',
  `PreCourseAID` int NOT NULL COMMENT '先修课程AID',
  PRIMARY KEY (`CourseAID`, `PreCourseAID`) USING BTREE,
  INDEX `Course_Pre_FK_2`(`PreCourseAID` ASC) USING BTREE,
  CONSTRAINT `Course_Pre_FK_1` FOREIGN KEY (`CourseAID`) REFERENCES `course` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Course_Pre_FK_2` FOREIGN KEY (`PreCourseAID`) REFERENCES `course` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '课程先修关系' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for dd_administrative_divisions
-- ----------------------------
DROP TABLE IF EXISTS `dd_administrative_divisions`;
CREATE TABLE `dd_administrative_divisions`  (
  `AID` int NOT NULL AUTO_INCREMENT COMMENT '行政区划AID',
  `Code` char(10) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '编码',
  `Name` varchar(50) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '名称',
  `Level` tinyint NOT NULL COMMENT '级别',
  `FatherCode` char(10) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NULL DEFAULT NULL COMMENT '上一级行政区划编码',
  `FullName` varchar(100) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '全称',
  `SimpleName` char(10) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NULL DEFAULT NULL COMMENT '简称',
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`Code` ASC) USING BTREE,
  UNIQUE INDEX `UIX2`(`Name` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '数据字典：国家行政区划编码' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for dd_professional_title
-- ----------------------------
DROP TABLE IF EXISTS `dd_professional_title`;
CREATE TABLE `dd_professional_title`  (
  `AID` smallint NOT NULL AUTO_INCREMENT COMMENT '职称编码ID',
  `Code` char(2) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '编码',
  `Name` varchar(20) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '名称',
  `Level` tinyint NOT NULL COMMENT '等级',
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`Code` ASC) USING BTREE,
  UNIQUE INDEX `UIX2`(`Name` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '数据字典：国家职称编码标准' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for dd_sex
-- ----------------------------
DROP TABLE IF EXISTS `dd_sex`;
CREATE TABLE `dd_sex`  (
  `AID` tinyint NOT NULL AUTO_INCREMENT COMMENT '性别编码AID',
  `Code` char(1) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '编码',
  `Name` char(2) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '名称',
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`Code` ASC) USING BTREE,
  UNIQUE INDEX `UIX2`(`Name` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '数据字典：性别编码' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for major
-- ----------------------------
DROP TABLE IF EXISTS `major`;
CREATE TABLE `major`  (
  `AID` smallint NOT NULL AUTO_INCREMENT COMMENT '专业AID',
  `Code` char(6) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '代码',
  `Name` varchar(30) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '名称',
  `Years` decimal(2, 1) NOT NULL DEFAULT 4.0 COMMENT '学制',
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`Code` ASC) USING BTREE,
  UNIQUE INDEX `UIX2`(`Name` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '专业' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for major_leader
-- ----------------------------
DROP TABLE IF EXISTS `major_leader`;
CREATE TABLE `major_leader`  (
  `MajorAID` smallint NOT NULL COMMENT '专业AID',
  `LeaderAID` int NOT NULL COMMENT '负责人教师AID',
  PRIMARY KEY (`MajorAID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`LeaderAID` ASC) USING BTREE,
  CONSTRAINT `Major_Leader_FK_1` FOREIGN KEY (`MajorAID`) REFERENCES `major` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Major_Leader_FK_2` FOREIGN KEY (`LeaderAID`) REFERENCES `teacher` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '专业负责人' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for student
-- ----------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student`  (
  `AID` int NOT NULL AUTO_INCREMENT COMMENT '学生AID（注册序号）',
  `Code` char(12) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '学号',
  `Name` varchar(50) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '姓名',
  `SexAID` tinyint NOT NULL COMMENT '性别编码',
  `Birthday` date NULL DEFAULT NULL COMMENT '生日',
  `YearInroll` smallint NOT NULL COMMENT '入学年份',
  `AddressCVAID` int NULL DEFAULT NULL COMMENT '家庭地址：社区/村AID',
  `AddressDetail` varchar(100) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NULL DEFAULT NULL COMMENT '家庭地址：详细地址',
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`Code` ASC) USING BTREE,
  INDEX `Student_FK_1`(`SexAID` ASC) USING BTREE,
  INDEX `Student_FK_6`(`AddressCVAID` ASC) USING BTREE,
  CONSTRAINT `Student_FK_1` FOREIGN KEY (`SexAID`) REFERENCES `dd_sex` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Student_FK_6` FOREIGN KEY (`AddressCVAID`) REFERENCES `dd_administrative_divisions` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `CHECK_YearInroll` CHECK (`YearInroll` > 0)
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '学生' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for student_course
-- ----------------------------
DROP TABLE IF EXISTS `student_course`;
CREATE TABLE `student_course`  (
  `AID` bigint NOT NULL AUTO_INCREMENT COMMENT '选修AID',
  `StudentAID` int NOT NULL COMMENT '学生AID',
  `CourseAID` int NOT NULL COMMENT '课程AID',
  `ForMajor` bit(1) NOT NULL DEFAULT b'1' COMMENT '主修/辅修：1-主修|0-辅修',
  `RegistDate` date NOT NULL COMMENT '选修日期',
  `AcademicYear` smallint NOT NULL COMMENT '学年',
  `Semester` bit(1) NOT NULL DEFAULT b'0' COMMENT '学期：0-上学期 | 1-下学期',
  `Score` decimal(4, 1) NULL DEFAULT NULL COMMENT '成绩',
  `HasPassed` tinyint GENERATED ALWAYS AS (if((`Score` >= 60),1,0)) VIRTUAL COMMENT '通过否：0-未通过 | 1-通过' NULL,
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`StudentAID` ASC, `CourseAID` ASC) USING BTREE,
  INDEX `Student_Course_FK_2`(`CourseAID` ASC) USING BTREE,
  CONSTRAINT `Student_Course_FK_1` FOREIGN KEY (`StudentAID`) REFERENCES `student` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Student_Course_FK_2` FOREIGN KEY (`CourseAID`) REFERENCES `course` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '学生选修课程' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for student_major1
-- ----------------------------
DROP TABLE IF EXISTS `student_major1`;
CREATE TABLE `student_major1`  (
  `StudentAID` int NOT NULL COMMENT '学生AID',
  `MajorAID` smallint NOT NULL COMMENT '专业AID',
  PRIMARY KEY (`StudentAID`) USING BTREE,
  INDEX `Student_Major1_FK_2`(`MajorAID` ASC) USING BTREE,
  CONSTRAINT `Student_Major1_FK_1` FOREIGN KEY (`StudentAID`) REFERENCES `student` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Student_Major1_FK_2` FOREIGN KEY (`MajorAID`) REFERENCES `major` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '学生主修专业' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for student_major2
-- ----------------------------
DROP TABLE IF EXISTS `student_major2`;
CREATE TABLE `student_major2`  (
  `StudentAID` int NOT NULL COMMENT '学生AID',
  `MajorAID` smallint NOT NULL COMMENT '专业AID',
  PRIMARY KEY (`StudentAID`) USING BTREE,
  INDEX `Student_Major2_FK_2`(`MajorAID` ASC) USING BTREE,
  CONSTRAINT `Student_Major2_FK_1` FOREIGN KEY (`StudentAID`) REFERENCES `student` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Student_Major2_FK_2` FOREIGN KEY (`MajorAID`) REFERENCES `major` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '学生辅修专业' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for student_phone
-- ----------------------------
DROP TABLE IF EXISTS `student_phone`;
CREATE TABLE `student_phone`  (
  `StudentAID` int NOT NULL COMMENT '学生AID',
  `PhoneNumber` char(11) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '电话号码',
  `FlagType` enum('0','1','2','3') CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '谁的电话：0-母亲 | 1-父亲| 2-我的 | 3-其它',
  `IsCommonlyUsed` bit(1) NOT NULL DEFAULT b'0' COMMENT '常用号码：1-是 | 0-否',
  PRIMARY KEY (`PhoneNumber`) USING BTREE,
  INDEX `Student_Phone_FK_1`(`StudentAID` ASC) USING BTREE,
  CONSTRAINT `Student_Phone_FK_1` FOREIGN KEY (`StudentAID`) REFERENCES `student` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '学生的电话' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for teacher
-- ----------------------------
DROP TABLE IF EXISTS `teacher`;
CREATE TABLE `teacher`  (
  `AID` int NOT NULL AUTO_INCREMENT COMMENT '教师AID',
  `Code` char(8) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '工号',
  `Name` varchar(50) CHARACTER SET gb18030 COLLATE gb18030_chinese_ci NOT NULL COMMENT '姓名',
  `TitleAID` smallint NOT NULL COMMENT '职称编码AID',
  PRIMARY KEY (`AID`) USING BTREE,
  UNIQUE INDEX `UIX1`(`Code` ASC) USING BTREE,
  INDEX `Teacher_FK_1`(`TitleAID` ASC) USING BTREE,
  CONSTRAINT `Teacher_FK_1` FOREIGN KEY (`TitleAID`) REFERENCES `dd_professional_title` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '教师' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for teacher_course
-- ----------------------------
DROP TABLE IF EXISTS `teacher_course`;
CREATE TABLE `teacher_course`  (
  `CourseAID` int NOT NULL COMMENT '课程AID',
  `TeacherAID` int NOT NULL COMMENT '授课教师AID',
  PRIMARY KEY (`CourseAID`) USING BTREE,
  INDEX `Teacher_Course_FK_2`(`TeacherAID` ASC) USING BTREE,
  CONSTRAINT `Teacher_Course_FK_1` FOREIGN KEY (`CourseAID`) REFERENCES `course` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Teacher_Course_FK_2` FOREIGN KEY (`TeacherAID`) REFERENCES `teacher` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '教师讲授课程' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for teacher_major
-- ----------------------------
DROP TABLE IF EXISTS `teacher_major`;
CREATE TABLE `teacher_major`  (
  `TeacherAID` int NOT NULL COMMENT '教师AID',
  `MajorAID` smallint NOT NULL COMMENT '专业AID',
  PRIMARY KEY (`TeacherAID`) USING BTREE,
  INDEX `Teacher_Major_FK_2`(`MajorAID` ASC) USING BTREE,
  CONSTRAINT `Teacher_Major_FK_1` FOREIGN KEY (`TeacherAID`) REFERENCES `teacher` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `Teacher_Major_FK_2` FOREIGN KEY (`MajorAID`) REFERENCES `major` (`AID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb18030 COLLATE = gb18030_chinese_ci COMMENT = '教师所属专业' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
