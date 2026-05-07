"""Flask Web 应用 —— 数据库应用系统教学演示

本模块是本讲的核心教学演示，展示一个完整的 Web 数据库应用系统的架构：
1. 表现层（Flask 路由 + HTML 模板）—— 用户交互界面
2. 中间层（Database 类）—— 统一数据访问接口
3. 数据层（MySQL）—— 数据存储与管理

演示的核心概念（对应 PPT 第6讲）：
- 中间件架构：Flask 不直接访问 MySQL，通过 Database 类中转
- 嵌入式 SQL：Python 代码中嵌入 SQL 语句（宿主语言 + SQL）
- 存储过程与函数：fn_GetTotalCreditBySID、sp_CourseStat
- 参数化查询：防止 SQL 注入的预处理语句
- 游标与SQL通信区：cursor 对象承载 SQL 执行状态

使用方法：
    export FLASK_APP=app.py
    flask run --debug
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from config import DB_CONFIG
from database import Database
from models import Student, Course, StudentCourse, CourseStat
from quiz_data import QUIZZES, grade_quiz

app = Flask(__name__)
app.secret_key = 'db06-teaching-demo-secret-key'

# 全局数据库实例（中间件层）
db = Database(**DB_CONFIG)


# ==================== 首页 ====================

@app.route('/')
def index():
    """首页 —— 展示数据库应用系统架构概览"""
    return render_template('index.html')


# ==================== 学生管理 ====================

@app.route('/students')
def student_list():
    """学生列表 —— 演示 SELECT 查询 + 函数调用

    每个学生显示其已获得的总学分（调用 fn_GetTotalCreditBySID）。
    这展示了嵌入式 SQL 中"函数调用"的用法：
    Python 代码中嵌入 SELECT fn_GetTotalCreditBySID(...) 调用。
    """
    students_data = db.get_all_students()
    students = []
    for row in students_data:
        student = Student(row)
        # 调用数据库函数获取总学分
        student.total_credit = db.call_fn_get_total_credit(student.id)
        students.append(student)
    return render_template('students.html', students=students)


@app.route('/student/<int:student_id>')
def student_detail(student_id):
    """学生详情 —— 演示多表连接查询

    显示学生基本信息 + 选课记录 + 总学分。
    选课记录查询使用 JOIN 连接 student_course 和 course 表。
    """
    student_row = db.get_student_by_id(student_id)
    if not student_row:
        flash(f'学生 {student_id} 不存在', 'error')
        return redirect(url_for('student_list'))

    student = Student(student_row)
    student.total_credit = db.call_fn_get_total_credit(student_id)
    courses_data = db.get_student_courses(student_id)
    courses = [StudentCourse(row) for row in courses_data]

    return render_template('student_detail.html',
                           student=student, courses=courses)


@app.route('/student/add', methods=['GET', 'POST'])
def student_add():
    """新增学生 —— 演示 INSERT 操作（参数化查询）

    POST 处理流程：
    1. 从前端表单获取用户输入（共享变量概念）
    2. 通过 Database 中间层执行参数化 INSERT
    3. 重定向到学生列表

    参数化查询 %s 占位符防止 SQL 注入。
    """
    if request.method == 'POST':
        try:
            student_id = int(request.form['id'])
            name = request.form['name']
            sex = request.form['sex']
            age = int(request.form['age'])
            dept = request.form['dept']
            rid = request.form['rid']

            db.add_student(student_id, name, sex, age, dept, rid)
            flash(f'学生 {name} 添加成功', 'success')
            return redirect(url_for('student_list'))
        except Exception as e:
            flash(f'添加失败: {e}', 'error')

    return render_template('student_form.html', student=None)


@app.route('/student/<int:student_id>/edit', methods=['GET', 'POST'])
def student_edit(student_id):
    """编辑学生 —— 演示 UPDATE 操作"""
    student_row = db.get_student_by_id(student_id)
    if not student_row:
        flash(f'学生 {student_id} 不存在', 'error')
        return redirect(url_for('student_list'))

    student = Student(student_row)

    if request.method == 'POST':
        try:
            name = request.form['name']
            sex = request.form['sex']
            age = int(request.form['age'])
            dept = request.form['dept']

            db.update_student(student_id, name, sex, age, dept)
            flash(f'学生 {name} 更新成功', 'success')
            return redirect(url_for('student_detail', student_id=student_id))
        except Exception as e:
            flash(f'更新失败: {e}', 'error')

    return render_template('student_form.html', student=student)


@app.route('/student/<int:student_id>/delete', methods=['POST'])
def student_delete(student_id):
    """删除学生 —— 演示 DELETE 操作 + 外键约束处理

    必须先删除子表记录（选课），再删除主表记录（学生）。
    这展示了数据库应用系统中参照完整性约束的应用层处理。
    """
    try:
        db.delete_student(student_id)
        flash(f'学生 {student_id} 已删除', 'success')
    except Exception as e:
        flash(f'删除失败: {e}', 'error')
    return redirect(url_for('student_list'))


# ==================== 课程管理 ====================

@app.route('/courses')
def course_list():
    """课程列表 —— 演示 LEFT JOIN 查询（含先修课信息）

    course 表自引用（PID → course.ID），使用 LEFT JOIN 连接自身
    来获取先修课程名称。
    """
    courses_data = db.get_all_courses()
    courses = [Course(row) for row in courses_data]
    return render_template('courses.html', courses=courses)


@app.route('/course/<int:course_id>/stat')
def course_stat(course_id):
    """课程统计 —— 演示存储过程 sp_CourseStat 的调用

    这是实验任务2的核心演示：
    1. 调用存储过程 sp_CourseStat
    2. 获取 5 个输出参数：平均分、最高分、最低分、及格人数、总人数
    3. 展示存储过程相比多次查询的优势（一次调用，多组统计）

    如果课程没有选课记录，所有输出参数自动为 0。
    """
    course_row = db.get_course_by_id(course_id)
    if not course_row:
        flash(f'课程 {course_id} 不存在', 'error')
        return redirect(url_for('course_list'))

    course = Course(course_row)
    stat_data = db.call_sp_course_stat(course_id)
    stat = CourseStat(stat_data)

    # 获取选课学生列表
    students_data = db.get_course_students(course_id)

    return render_template('course_stat.html',
                           course=course, stat=stat, students=students_data)


# ==================== 教学概念讲解页 ====================

@app.route('/concepts/embedded-sql')
def concept_embedded_sql():
    """嵌入式 SQL 概念讲解页

    用本项目的实际代码展示嵌入式 SQL 的四个核心概念：
    1. 宿主语言 + SQL 语句的混合编程
    2. SQL 通信区（cursor 对象）
    3. 共享变量（参数化查询的 %s 占位符）
    4. 游标（cursor 处理结果集）
    """
    return render_template('embedded_sql.html')


@app.route('/concepts/middleware')
def concept_middleware():
    """中间件概念讲解页

    展示本项目的三层架构：
    Flask (表现层) → Database 类 (中间件) → MySQL (数据层)
    """
    return render_template('middleware.html')


@app.route('/concepts/history')
def concept_history():
    """数据管理技术发展历史讲解页

    展示数据库管理技术从手工管理到云原生融合的五个发展阶段。
    """
    return render_template('history.html')


@app.route('/concepts/trigger')
def concept_trigger():
    """触发器概念讲解页

    展示触发器的核心概念、本项目的 trg_grade_check 实现，
    以及触发器与应用程序校验的对比。
    """
    return render_template('trigger.html')


@app.route('/homework-guide')
def homework_guide():
    """作业参考答案要点页面

    提供DB06作业简答题和分析题的答题思路与要点提示。
    """
    return render_template('homework_guide.html')


# ==================== 实验平台 ====================

@app.route('/lab')
def lab_index():
    """实验平台首页 —— 列出可完成的实验任务"""
    return render_template('lab.html')


@app.route('/lab/task1', methods=['GET', 'POST'])
def lab_task1():
    """任务1：自定义函数在线评测

    GET: 显示题目和代码编辑器
    POST: 接收学生提交的 SQL，调用 grade_task1 自动评测
    """
    result = None
    sql_code = ''
    if request.method == 'POST':
        sql_code = request.form.get('sql', '').strip()
        if sql_code:
            result = db.grade_task1(sql_code)
    return render_template('lab_task1.html', result=result, sql=sql_code)


@app.route('/lab/task2', methods=['GET', 'POST'])
def lab_task2():
    """任务2：存储过程在线评测

    GET: 显示题目和代码编辑器
    POST: 接收学生提交的 SQL，调用 grade_task2 自动评测
    """
    result = None
    sql_code = ''
    if request.method == 'POST':
        sql_code = request.form.get('sql', '').strip()
        if sql_code:
            result = db.grade_task2(sql_code)
    return render_template('lab_task2.html', result=result, sql=sql_code)


@app.route('/lab/quiz/<quiz_id>', methods=['GET', 'POST'])
def lab_quiz(quiz_id):
    """概念测验 —— 中间件、嵌入式SQL、存储过程、发展历史

    GET: 显示测验题目
    POST: 接收学生答案，自动评分并显示解析
    """
    quiz = QUIZZES.get(quiz_id)
    if not quiz:
        flash(f'测验 {quiz_id} 不存在', 'error')
        return redirect(url_for('lab_index'))

    result = None
    if request.method == 'POST':
        user_answers = {}
        for q in quiz['questions']:
            if q['type'] == 'match':
                # 匹配题：收集每个 left_item 对应的值
                match_ans = {}
                for item in q['left_items']:
                    key = f"{q['id']}_{item}"
                    match_ans[item] = request.form.get(key, '')
                user_answers[q['id']] = match_ans
            elif q['type'] == 'multiple':
                # 多选：收集所有选中的值
                vals = request.form.getlist(q['id'])
                user_answers[q['id']] = vals
            else:
                user_answers[q['id']] = request.form.get(q['id'], '')

        result = grade_quiz(quiz_id, user_answers)

    return render_template('quiz.html', quiz_id=quiz_id, quiz=quiz, result=result)


# ==================== 应用启动 ====================

@app.before_request
def before_request():
    """每次请求前确保数据库连接可用"""
    if not db.connection or not db.connection.is_connected():
        db.connect()


@app.teardown_appcontext
def teardown(exception):
    """应用上下文销毁时的清理（不关闭连接，复用）"""
    pass


def init_app():
    """应用初始化：连接数据库并创建函数、存储过程和触发器"""
    if db.connect():
        db.init_db_objects()
        print("应用初始化完成")
    else:
        print("应用初始化失败：无法连接数据库")


# 无论直接运行还是 flask run，都会执行这里
init_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
