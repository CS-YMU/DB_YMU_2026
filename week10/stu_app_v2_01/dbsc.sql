/*
 Navicat Premium Dump SQL

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 80023 (8.0.23)
 Source Host           : localhost:3306
 Source Schema         : dbsc

 Target Server Type    : MySQL
 Target Server Version : 80023 (8.0.23)
 File Encoding         : 65001

 Date: 08/03/2026 14:51:11
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for course
-- ----------------------------
DROP TABLE IF EXISTS `course`;
CREATE TABLE `course`  (
  `ID` int NOT NULL COMMENT '课程编号',
  `Name` varchar(255) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL COMMENT '课程名称',
  `PID` int NULL DEFAULT NULL COMMENT '前修课程编号',
  `Credit` decimal(3, 1) NOT NULL COMMENT '学分',
  PRIMARY KEY (`ID`) USING BTREE,
  UNIQUE INDEX `Name_UNIQUE`(`Name` ASC) USING BTREE,
  INDEX `FK_course_PID`(`PID` ASC) USING BTREE INVISIBLE,
  CONSTRAINT `FK_course_PID_r_course_ID` FOREIGN KEY (`PID`) REFERENCES `course` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf16 COLLATE = utf16_general_ci COMMENT = '课程及其先修课程' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of course
-- ----------------------------
INSERT INTO `course` VALUES (1, '数据库', 5, 4.0);
INSERT INTO `course` VALUES (2, '数学', NULL, 2.0);
INSERT INTO `course` VALUES (3, '信息系统', 1, 4.0);
INSERT INTO `course` VALUES (4, '操作系统', 6, 3.0);
INSERT INTO `course` VALUES (5, '数据结构', 7, 4.0);
INSERT INTO `course` VALUES (6, '数据处理', NULL, 2.0);
INSERT INTO `course` VALUES (7, 'C程序设计', NULL, 4.0);

-- ----------------------------
-- Table structure for student
-- ----------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student`  (
  `ID` int NOT NULL COMMENT '学号',
  `Name` varchar(255) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL COMMENT '姓名',
  `Sex` char(1) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL COMMENT '性别',
  `Age` tinyint NOT NULL COMMENT '年龄',
  `Dept` char(2) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL COMMENT '所在系',
  `RID` char(18) CHARACTER SET utf16 COLLATE utf16_general_ci NOT NULL COMMENT '身份证号',
  PRIMARY KEY (`ID`) USING BTREE,
  UNIQUE INDEX `RID_UNIQUE`(`RID` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf16 COLLATE = utf16_general_ci COMMENT = '学生' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of student
-- ----------------------------
INSERT INTO `student` VALUES (200215121, '李勇', '男', 20, 'CS', '530101200601042000');
INSERT INTO `student` VALUES (200215122, '刘晨', '女', 19, 'CS', '230102200706081000');
INSERT INTO `student` VALUES (200215123, '王敏', '女', 18, 'MA', '530401200804055000');
INSERT INTO `student` VALUES (200215125, '张立', '男', 19, 'IS', '530102200706081000');

-- ----------------------------
-- Table structure for student_course
-- ----------------------------
DROP TABLE IF EXISTS `student_course`;
CREATE TABLE `student_course`  (
  `StudentID` int NOT NULL COMMENT '学号',
  `CourseID` int NOT NULL COMMENT '课程编号',
  `Grade` decimal(4, 1) NULL DEFAULT NULL COMMENT '成绩',
  PRIMARY KEY (`StudentID`, `CourseID`) USING BTREE,
  INDEX `FK_SC_CourseID_r_course_ID`(`CourseID` ASC) USING BTREE,
  CONSTRAINT `FK_SC_CourseID_r_course_ID` FOREIGN KEY (`CourseID`) REFERENCES `course` (`ID`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_SC_StudentID_r_Student_ID` FOREIGN KEY (`StudentID`) REFERENCES `student` (`ID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf16 COLLATE = utf16_general_ci COMMENT = '学生选修课程' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of student_course
-- ----------------------------
INSERT INTO `student_course` VALUES (200215121, 1, 93.0);
INSERT INTO `student_course` VALUES (200215121, 2, 86.0);
INSERT INTO `student_course` VALUES (200215121, 3, 89.0);
INSERT INTO `student_course` VALUES (200215122, 2, 91.0);
INSERT INTO `student_course` VALUES (200215122, 3, 81.0);

-- ----------------------------
-- Table structure for student_course_retake
-- ----------------------------
DROP TABLE IF EXISTS `student_course_retake`;
CREATE TABLE `student_course_retake`  (
  `StudentID` int NOT NULL COMMENT '学号',
  `CourseID` int NOT NULL COMMENT '课程编号',
  `Grade` decimal(4, 1) NULL DEFAULT NULL COMMENT '成绩',
  PRIMARY KEY (`StudentID`, `CourseID`) USING BTREE,
  CONSTRAINT `FK_SCRetake_StudnetID&CourseID_r_SC` FOREIGN KEY (`StudentID`, `CourseID`) REFERENCES `student_course` (`StudentID`, `CourseID`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf16 COLLATE = utf16_general_ci COMMENT = '学生重修课程' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of student_course_retake
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
