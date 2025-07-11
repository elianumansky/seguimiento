from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'doecom34@gmail.com'   # <--- Cambiar
app.config['MAIL_PASSWORD'] = '1234'          # <--- Cambiar
mail = Mail(app)

# Función para obtener DB
def get_db_connection():
    conn = sqlite3.connect('seguimiento.db')
    conn.row_factory = sqlite3.Row
    return conn

# Scheduler para revisar seguimientos
def check_seguimientos():
    conn = get_db_connection()
    alumnos = conn.execute('SELECT * FROM alumnos').fetchall()
    for alumno in alumnos:
        ultima_fecha = datetime.strptime(alumno['ultima_fecha'], "%Y-%m-%d")
        frecuencia = alumno['frecuencia_dias']
        if datetime.now() >= ultima_fecha + timedelta(days=frecuencia):
            enviar_mail(alumno)
    conn.close()

def enviar_mail(alumno):
    msg = Message('Seguimiento pendiente',
                  sender='doecom34@gmail.com',   # <--- Cambiar
                  recipients=['doecom34@colegio.com'])
    msg.body = f"Se debe hacer el seguimiento de {alumno['nombre']}."
    mail.send(msg)

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_seguimientos, trigger="interval", hours=24)
scheduler.start()

# Rutas
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    email = request.form['email']
    clave = request.form['clave']
    if (email == 'doecom34@gmail.com' and clave == '1234') or \
       (email == 'doecom34@gmail.com' and clave == 'abcd'):
        session['usuario'] = email
        return redirect(url_for('dashboard'))
    flash('Login incorrecto')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    alumnos = conn.execute('SELECT * FROM alumnos').fetchall()
    conn.close()
    return render_template('dashboard.html', alumnos=alumnos)

@app.route('/add_alumno', methods=['POST'])
def add_alumno():
    nombre = request.form['nombre']
    frecuencia = int(request.form['frecuencia'])
    conn = get_db_connection()
    conn.execute('INSERT INTO alumnos (nombre, frecuencia_dias, ultima_fecha) VALUES (?, ?, ?)',
                 (nombre, frecuencia, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/ver_historial/<int:alumno_id>')
def ver_historial(alumno_id):
    conn = get_db_connection()
    informes = conn.execute('SELECT * FROM informes WHERE alumno_id = ?', (alumno_id,)).fetchall()
    conn.close()
    return render_template('historial.html', informes=informes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Puerto adaptado para Render ---
port = int(os.environ.get('PORT', 10000))
app.run(host='0.0.0.0', port=port)
