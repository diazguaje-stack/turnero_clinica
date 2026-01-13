import sqlite3
import os

RUTA = os.path.join(os.path.dirname(__file__), "turnero.db")

conn = sqlite3.connect(RUTA)
cur = conn.cursor()

cur.execute("PRAGMA table_info(llamado_actual)")
columnas = [c[1] for c in cur.fetchall()]

if "activo" not in columnas:
    cur.execute("ALTER TABLE llamado_actual ADD COLUMN activo INTEGER DEFAULT 0")
    print("Columna activo creada")

if "hablado" not in columnas:
    cur.execute("ALTER TABLE llamado_actual ADD COLUMN hablado INTEGER DEFAULT 0")
    print("Columna hablado creada")

conn.commit()
conn.close()
