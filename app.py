
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
import threading
import time
import schedule
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'clave-secreta-para-sesiones'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect(url_for('index'))
        flash('Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=('GET', 'POST'))
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        interval_days = int(request.form['interval_days'])
        last_followup = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        conn.execute('INSERT INTO students (name, email, interval_days, last_followup) VALUES (?, ?, ?, ?)',
                     (name, email, interval_days, last_followup))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/student/<int:student_id>', methods=('GET', 'POST'))
def student_detail(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    reports = conn.execute('SELECT * FROM reports WHERE student_id = ? ORDER BY date DESC', (student_id,)).fetchall()
    if request.method == 'POST':
        content = request.form['content']
        date = datetime.now().strftime('%Y-%m-%d')
        conn.execute('INSERT INTO reports (student_id, content, date) VALUES (?, ?, ?)', 
                     (student_id, content, date))
        conn.execute('UPDATE students SET last_followup = ? WHERE id = ?', (date, student_id))
        conn.commit()
    conn.close()
    return render_template('student_detail.html', student=student, reports=reports)

def check_followups():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    users = conn.execute('SELECT email FROM users').fetchall()
    for student in students:
        last_date = datetime.strptime(student['last_followup'], '%Y-%m-%d')
        next_due = last_date + timedelta(days=student['interval_days'])
        if datetime.now().date() >= next_due.date():
            for user in users:
                send_email(user['email'], student['name'])
    conn.close()

def send_email(to_email, student_name):
    msg = MIMEText(f"Recordatorio: realizar seguimiento de {student_name}")
    msg['Subject'] = f"Seguimiento pendiente de {student_name}"
    msg['From'] = 'tu_email@gmail.com'
    msg['To'] = to_email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('tu_email@gmail.com', 'tu_clave_app')
            server.send_message(msg)
            print(f"Email enviado a {to_email} por {student_name}")
    except Exception as e:
        print(f"Error enviando a {to_email}: {e}")

def run_scheduler():
    schedule.every(12).hours.do(check_followups)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(debug=True)
