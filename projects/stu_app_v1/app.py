# app.py - Flask应用主文件
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL配置
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'dylan'
app.config['MYSQL_PASSWORD'] = 'P@ssw0rd'
app.config['MYSQL_DB'] = 'student_db'

mysql = MySQL(app)

@app.route('/')
def index():
    """首页：显示所有学生"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM students ORDER BY student_id')
    students = cursor.fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """添加学生页面"""
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        major = request.form['major']
        phone = request.form['phone']
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO students (student_id, name, gender, age, major, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (student_id, name, gender, age, major, phone))
        mysql.connection.commit()
        flash('学生添加成功！', 'success')
        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/edit/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """编辑学生信息"""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        major = request.form['major']
        phone = request.form['phone']
        
        cursor.execute('''
            UPDATE students 
            SET name=%s, gender=%s, age=%s, major=%s, phone=%s
            WHERE student_id=%s
        ''', (name, gender, age, major, phone, student_id))
        mysql.connection.commit()
        flash('学生信息更新成功！', 'success')
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM students WHERE student_id = %s', (student_id,))
    student = cursor.fetchone()
    return render_template('edit.html', student=student)

@app.route('/delete/<student_id>')
def delete_student(student_id):
    """删除学生"""
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM students WHERE student_id = %s', (student_id,))
    mysql.connection.commit()
    flash('学生删除成功！', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)