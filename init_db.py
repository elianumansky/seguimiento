import sqlite3

conn = sqlite3.connect('seguimiento.db')
cursor = conn.cursor()

# Crear tabla de usuarios sin UNIQUE en email
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    clave TEXT NOT NULL,
    rol TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    curso TEXT DEFAULT 'Sin asignar',
    seguimiento_cada INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS informes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER,
    fecha TEXT,
    contenido TEXT,
    FOREIGN KEY (alumno_id) REFERENCES alumnos (id)
)
''')

usuarios = [
    ('doecom34@gmail.com', '1234', 'asesora'),
    ('doecom34@gmail.com', '1234', 'psicologa')
]

for email, clave, rol in usuarios:
    cursor.execute('SELECT * FROM usuarios WHERE email = ? AND rol = ?', (email, rol))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO usuarios (email, clave, rol) VALUES (?, ?, ?)', (email, clave, rol))

conn.commit()
conn.close()

print("Base de datos inicializada.")
