from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import datetime
import os

app = Flask(__name__)

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'doecom34@gmail.com'
app.config['MAIL_PASSWORD'] = '1234'

mail = Mail(app)

@app.route('/')
def index():
    conn = sqlite3.connect('seguimiento.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM alumnos")
    alumnos = cursor.fetchall()
    conn.close()
    return render_template('index.html', alumnos=alumnos)

@app.route('/alumno/nuevo', methods=['GET', 'POST'])
def nuevo_alumno():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        seguimiento_cada_dias = request.form.get('seguimiento_cada_dias')
        if not nombre or not seguimiento_cada_dias:
            return "Faltan datos", 400
        conn = sqlite3.connect('seguimiento.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alumnos (nombre, seguimiento_cada_dias) VALUES (?, ?)", (nombre, int(seguimiento_cada_dias)))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('nuevo_alumno.html')

@app.route('/alumno/<int:alumno_id>', methods=['GET', 'POST'])
def detalle_alumno(alumno_id):
    conn = sqlite3.connect('seguimiento.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        contenido = request.form.get('contenido')
        fecha = datetime.date.today().isoformat()
        if contenido:
            cursor.execute("INSERT INTO informes (alumno_id, fecha, contenido) VALUES (?, ?, ?)", (alumno_id, fecha, contenido))
            conn.commit()
    cursor.execute("SELECT nombre FROM alumnos WHERE id = ?", (alumno_id,))
    alumno = cursor.fetchone()
    cursor.execute("SELECT fecha, contenido FROM informes WHERE alumno_id = ? ORDER BY fecha DESC", (alumno_id,))
    informes = cursor.fetchall()
    conn.close()
    return render_template('detalle_alumno.html', alumno=alumno, informes=informes, alumno_id=alumno_id)

# Tarea programada y función de envío de mail igual que antes...

# ... (aquí iría la función tarea_periodica, enviar_mail_seguimiento y scheduler)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
