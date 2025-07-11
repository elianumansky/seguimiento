import sqlite3

def init_db():
    conn = sqlite3.connect('seguimiento.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        clave TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        seguimiento_cada_dias INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS informes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER,
        fecha TEXT NOT NULL,
        contenido TEXT,
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
    )
    """)

    # Insertar usuarios con el mail común
    cursor.execute("""
    INSERT INTO usuarios (email, clave, rol)
    VALUES ('doecom34@gmail.com', 'clave123', 'asesora')
    """)
    cursor.execute("""
    INSERT INTO usuarios (email, clave, rol)
    VALUES ('doecom34@gmail.com', 'clave123', 'psicologa')
    """)

    conn.commit()
    conn.close()
    print("Base de datos inicializada con usuarios asesora y psicologa en doecom34@gmail.com / clave123")

if __name__ == '__main__':
    init_db()
