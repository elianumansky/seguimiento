
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    interval_days INTEGER,
    last_followup TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    content TEXT,
    date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)''')

hashed_password = generate_password_hash('clave123')
c.execute('INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)', ('asesora@escuela.com', hashed_password))

conn.commit()
conn.close()
print("Base de datos inicializada con usuario asesora@escuela.com / clave123")
