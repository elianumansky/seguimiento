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
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        curso = request.form['curso']
        seguimiento_cada = request.form['seguimiento_cada']
        conn = sqlite3.connect('seguimiento.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO alumnos (nombre, apellido, curso, seguimiento_cada) VALUES (?, ?, ?, ?)',
                       (nombre, apellido, curso, seguimiento_cada))
        conn.commit()
        conn.close()
        return redirect(url_for('alumnos'))
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

@app.route('/alumno/eliminar/<int:alumno_id>', methods=['POST'])
def eliminar_alumno(alumno_id):
    conn = sqlite3.connect('seguimiento.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM alumnos WHERE id = ?', (alumno_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('alumnos'))

# Tarea programada y función de envío de mail igual que antes...

# ... (aquí iría la función tarea_periodica, enviar_mail_seguimiento y scheduler)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
