from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def conectar():
    return sqlite3.connect("turnos.db")

def init_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente TEXT,
            medico TEXT,
            fecha TEXT,
            hora TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turnos")
    turnos = cursor.fetchall()
    conn.close()
    return render_template("index.html", turnos=turnos)

@app.route("/agregar", methods=["POST"])
def agregar():
    datos = (
        request.form["paciente"],
        request.form["medico"],
        request.form["fecha"],
        request.form["hora"]
    )

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO turnos (paciente, medico, fecha, hora)
        VALUES (?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM turnos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/editar/<int:id>")
def editar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turnos WHERE id=?", (id,))
    turno = cursor.fetchone()
    conn.close()
    return render_template("editar.html", turno=turno)

@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    datos = (
        request.form["paciente"],
        request.form["medico"],
        request.form["fecha"],
        request.form["hora"],
        id
    )

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE turnos 
        SET paciente=?, medico=?, fecha=?, hora=?
        WHERE id=?
    """, datos)
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()


