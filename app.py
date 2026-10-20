from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import mysql.connector
from db.conexion import conectar

app = Flask(__name__)
app.secret_key = '1478'

@app.route("/")
def inicio():
    return render_template("index.html")

# Ruta GET para mostrar el formulario de registro (por si la necesitas)
@app.route("/registro", methods=["GET"])
def formulario_registro():
    return render_template("registro.html")

@app.route("/registro", methods=["POST"])
def registrar():
    nombre = request.form["nombre"]
    correoElectronico = request.form["correoElectronico"]
    password = request.form["password"]

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM usuarios WHERE correoElectronico = %s",
        (correoElectronico,)
    )

    usuario_existente = cursor.fetchone()

    if usuario_existente:
        cursor.close()
        conexion.close()
        flash("Este correo electrónico ya está registrado.", "danger")
        return redirect(url_for("formulario_registro"))

    # 1. Generar hash con Bcrypt
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    # 2. Insertar usando el hash convertido a string (.decode('utf-8'))
    cursor.execute(
        """
        INSERT INTO usuarios(nombre, correoElectronico, password)
        VALUES(%s, %s, %s)
        """,
        (nombre, correoElectronico, password_hash.decode('utf-8'))
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    flash("¡Registro exitoso! Por favor inicia sesión.", "success")
    return redirect(url_for("formulario_login"))

@app.route("/login", methods=["GET"])
def formulario_login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    correoElectronico = request.form["correoElectronico"]
    password = request.form["password"]

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    # 3. Consultar SOLO por correo electrónico (la contraseña se valida abajo con bcrypt)
    cursor.execute(
        """
        SELECT * FROM usuarios
        WHERE correoElectronico = %s
        """,
        (correoElectronico,)
    )

    usuario_encontrado = cursor.fetchone()
    cursor.close()
    conexion.close()

    # 4. Verificar la contraseña de forma segura con bcrypt
    if usuario_encontrado and bcrypt.checkpw(password.encode('utf-8'), usuario_encontrado['password'].encode('utf-8')):
        session["usuario"] = usuario_encontrado['correoElectronico']
        flash("¡Bienvenido!", "success")
        return redirect(url_for("panel_principal"))
    else:
        flash("Usuario o contraseña incorrectos", "danger")
        return redirect(url_for("formulario_login"))

@app.route("/home")
def panel_principal():
    return render_template("home.html")

@app.route("/personal")
def personal():
    return render_template("personal.html")

@app.route("/estado_personal")
def estado_personal():
    return render_template("estado_personal.html")

@app.route("/veredas")
def veredas():
    return render_template("veredas.html")

@app.route("/familias")
def familias():
    return render_template("familias.html")