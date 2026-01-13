import sqlite3

conn = sqlite3.connect("turnero.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS turnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    documento TEXT NOT NULL,
    estado TEXT DEFAULT 'en_espera',
    medico TEXT,
    consultorio TEXT,
    codigo TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS llamado_actual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    documento TEXT,
    codigo TEXT,
    consultorio TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS medicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
)
""")



cursor.execute("""
CREATE TABLE IF NOT EXISTS consultorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
)
""")

# Datos iniciales
cursor.execute("INSERT INTO medicos (nombre) VALUES ('Juan Pérez')")
cursor.execute("INSERT INTO medicos (nombre) VALUES ('Niño')")
cursor.execute("INSERT INTO medicos (nombre) VALUES ('Jesús')")


cursor.execute("INSERT INTO consultorios (nombre) VALUES ('Consultorio 1')")
cursor.execute("INSERT INTO consultorios (nombre) VALUES ('Consultorio 2')")
cursor.execute("INSERT INTO consultorios (nombre) VALUES ('Consultorio 3')")


conn.commit()
conn.close()



print("Base de datos creada correctamente")
