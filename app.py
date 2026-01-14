from flask import Flask,render_template,request,jsonify,redirect
from bd import get_db
import random
import string
import os
import sqlite3

import sqlite3

def init_db():
    conn = sqlite3.connect("turnos.db")
    cursor = conn.cursor()

    # TABLA TURNOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS turnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        documento TEXT,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        medico TEXT,
        consultorio TEXT,
        codigo TEXT,
        estado TEXT DEFAULT 'en_espera'
    )
    """)

    # TABLA MEDICOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE
    )
    """)

    # TABLA CONSULTORIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE
    )
    """)

    # TABLA LLAMADO ACTUAL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS llamado_actual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        documento TEXT,
        codigo TEXT,
        consultorio TEXT,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        activo INTEGER DEFAULT 1,
        hablado INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

app=Flask(__name__)

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def generar_codigo():
    letras = ''.join(random.choices(string.ascii_uppercase, k=2))
    numeros = ''.join(random.choices("0123456789", k=3))
    return f"{letras}-{numeros}"

def generar_codigo_unico(cursor):
    while True:
        codigo = generar_codigo()
        cursor.execute("SELECT 1 FROM turnos WHERE codigo = ?", (codigo,))
        if not cursor.fetchone():
            return codigo


def obtener_medicos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM medicos ORDER BY nombre")
    data = cursor.fetchall()
    conn.close()
    return [m["nombre"] for m in data]

def obtener_consultorios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM consultorios ORDER BY nombre")
    data = cursor.fetchall()
    conn.close()
    return [c["nombre"] for c in data]


@app.route("/",methods=["GET"])
def form():
    return render_template("index.html")

@app.route("/guardar", methods=["POST"])
def guardar():
    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    codigo = generar_codigo_unico(cursor)

    cursor.execute("""
        INSERT INTO turnos (nombre, documento,codigo)
        VALUES (?, ?,?)
    """, (data["nombre"], data["documento"],codigo))

    conn.commit()
    conn.close()

    return jsonify({"ok": True,"codigo": codigo})


@app.route("/lista")
def lista():
    medico = request.args.get("medico")
    if medico in ("", "None"):
        medico = None

    conn = get_db()
    cursor = conn.cursor()

    if medico:
        cursor.execute("""
            SELECT id, nombre, documento, fecha, medico, consultorio, codigo
            FROM turnos
            WHERE medico = ? AND estado = 'en_espera'
            ORDER BY fecha ASC
        """, (medico,))
    else:
        cursor.execute("""
            SELECT id, nombre, documento, fecha, medico, consultorio, codigo
            FROM turnos
            WHERE estado = 'en_espera'
            ORDER BY fecha ASC
        """)


    turnos = cursor.fetchall()
    conn.close()

    return render_template(
        "lista.html",
        turnos=turnos,
        medicos=obtener_medicos(),
        consultorios=obtener_consultorios(),
        medico_seleccionado=medico
    )


@app.route("/admin")
def admin():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM medicos ORDER BY nombre")
    medicos = cursor.fetchall()

    cursor.execute("SELECT * FROM consultorios ORDER BY nombre")
    consultorios = cursor.fetchall()

    conn.close()

    return render_template("admin.html", medicos=medicos, consultorios=consultorios)


@app.route("/agregar_consultorio", methods=["POST"])
def agregar_consultorio():
    nombre = request.form["nombre"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO consultorios (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/borrar_consultorio/<int:id>")
def borrar_consultorio(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM consultorios WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")



@app.route("/agregar_medico", methods=["POST"])
def agregar_medico():
    nombre = request.form["nombre"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medicos (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/borrar_medico/<int:id>")
def borrar_medico(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicos WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")



@app.route("/asignar_medico", methods=["POST"])
def asignar_medico():
    id_turno = request.form["id"]
    medico = request.form["medico"]

    conn=get_db()
    cursor=conn.cursor()

    cursor.execute("""
        UPDATE turnos
        SET medico=?
        WHERE id=?
    """,(medico,id_turno))

    conn.commit()
    conn.close()

    return redirect("/lista")

@app.route("/asignar_consultorio",methods=["POST"])
def asignar_consultorio():
    id_turno= request.form["id"]
    consultorio=request.form["consultorio"]

    conn=get_db()
    cursor=conn.cursor()

    cursor.execute("""
        UPDATE turnos
        SET consultorio=?
        WHERE id=?
    """,(consultorio,id_turno))

    conn.commit()
    conn.close()

    return redirect("/lista")

@app.route("/llamar", methods=["POST"])
def llamar():
    id_turno = request.form["id"]
    medico_filtro = request.form.get("medico", "")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombre, documento, codigo, consultorio, medico
        FROM turnos
        WHERE id = ?
    """, (id_turno,))
    turno = cursor.fetchone()

    if not turno or not turno["medico"] or not turno["consultorio"]:
        conn.close()
        return redirect("/lista?medico=" + medico_filtro)

    cursor.execute("""
        UPDATE turnos
        SET estado = 'llamado'
        WHERE id = ?
    """, (id_turno,))
    cursor.execute("UPDATE llamado_actual SET activo = 0")

    cursor.execute("""
        INSERT INTO llamado_actual
        (nombre, documento, codigo, consultorio, activo, hablado)
        VALUES (?, ?, ?, ?, 1, 0)
    """, (
        turno["nombre"],
        turno["documento"],
        turno["codigo"],
        turno["consultorio"]
    ))

    conn.commit()
    conn.close()

    return redirect("/lista?medico=" + medico_filtro)






@app.route("/pantalla")
def pantalla():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT codigo, nombre, consultorio
        FROM llamado_actual
        ORDER BY fecha DESC
        LIMIT 5
        
    """)

    llamados= cursor.fetchall()
    conn.close()

    return render_template("pantalla.html", llamados=llamados)

@app.route("/api/llamados")
def api_llamados():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, codigo, nombre, consultorio,activo
        FROM llamado_actual
        WHERE activo = 1
        ORDER BY fecha DESC
        LIMIT 1
    """)

    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(x) for x in data])

@app.route("/api/marcar_leido/<int:id>", methods=["POST"])
def marcar_leido(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE llamado_actual
        SET hablado = 1
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()
    return "", 204



if __name__=="__main__":
    app.run()
