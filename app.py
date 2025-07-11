from flask import Flask, request, jsonify
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

# ==============================
# Funciones auxiliares
# ==============================

def enviar_mail_seguimiento(alumno_nombre):
    msg = Message('Seguimiento requerido',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=['doecom34@gmail.com'])
    msg.body = f"Se debe realizar un seguimiento para el alumno: {alumno_nombre}."
    mail.send(msg)
    print(f"Correo enviado solicitando seguimiento de {alumno_nombre}.")

# ==============================
# API Endpoints
# ==============================

@app.route('/alumnos', methods=['POST'])
def agregar_alumno():
    data = request.get_json()
    nombre = data.get('nombre')
    seguimiento_cada_dias = data.get('seguimiento_cada_dias')
    if not nombre or not seguimiento_cada_dias:
        return jsonify({'error': 'Datos incompletos'}), 400

    conn = sqlite3.connect('seguimiento.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alumnos (nombre, seguimiento_cada_dias) VALUES (?, ?)", (nombre, seguimiento_cada_dias))
    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Alumno agregado correctamente'})

@app.route('/informes', methods=['POST'])
def agregar_informe():
    data = request.get_json()
    alumno_id = data.get('alumno_id')
    contenido = data.get('contenido')
    fecha = datetime.date.today().isoformat()

    conn = sqlite3.connect('seguimiento.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO informes (alumno_id, fecha, contenido) VALUES (?, ?, ?)", (alumno_id, fecha, contenido))
    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Informe agregado correctamente'})

# ==============================
# Tarea programada
# ==============================

def tarea_periodica():
    conn = sqlite3.connect('seguimiento.db')
    cursor = conn.cursor()
    hoy = datetime.date.today()

    cursor.execute("SELECT id, nombre, seguimiento_cada_dias FROM alumnos")
    alumnos = cursor.fetchall()
    for alumno in alumnos:
        alumno_id, nombre, dias = alumno
        cursor.execute("SELECT fecha FROM informes WHERE alumno_id = ? ORDER BY fecha DESC LIMIT 1", (alumno_id,))
        ultimo_informe = cursor.fetchone()
        if ultimo_informe:
            ultima_fecha = datetime.datetime.strptime(ultimo_informe[0], "%Y-%m-%d").date()
            if (hoy - ultima_fecha).days >= dias:
                enviar_mail_seguimiento(nombre)
        else:
            enviar_mail_seguimiento(nombre)

    conn.close()

# ==============================
# Scheduler
# ==============================

scheduler = BackgroundScheduler()
scheduler.add_job(tarea_periodica, 'interval', days=1)
scheduler.start()

# ==============================
# Run app
# ==============================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
