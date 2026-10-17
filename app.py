from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from db.conexion import conectar
app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/registro", methods=["POST"])
def registrar():
    nombre = request.form["nombre"]
    correoElectronico = request.form["correoElectronico"]
    password = request.form["password"]

    conexion = conectar()
    cursor = conexion.cursor()

    
    cursor.execute(
        """
        INSERT INTO usuarios(nombre, correoElectronico, password)
        VALUES(%s,%s,%s)
        """,
        (nombre, correoElectronico, password)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(url_for("formulario_login"))

@app.route("/login", methods=["GET"])
def formulario_login():
    return render_template("login.html")



@app.route("/login", methods=["POST"])
def login():
    correoElectronico = request.form["correoElectronico"]
    password = request.form["password"]

    conexion = conectar()
    cursor = conexion.cursor()

    
    cursor.execute(
        """
        SELECT * FROM usuarios
        WHERE correoElectronico=%s AND password=%s
        """,
        (correoElectronico, password)
    )

    usuario_encontrado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if usuario_encontrado:
        return redirect(url_for("panel_principal"))
    else:
        return "Usuario o contraseña incorrectos"

@app.route("/home")
def panel_principal():
    return render_template("home.html")

@app.route("/personal")
def personal():
    return render_template("personal.html")

@app.route("/estado_personal")
def estado_personal ():
    return render_template("estado_personal.html")

@app.route("/veredas")
def veredas():
    return render_template("veredas.html")

@app.route("/familias")
def familias():
    return render_template("familias.html")
