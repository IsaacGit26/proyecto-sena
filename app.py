from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import mysql.connector
from db.conexion import conectar

app = Flask(__name__)
app.secret_key = '1478'

@app.route("/")
def inicio():
    return render_template("index.html")

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

    
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)


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
    if usuario_encontrado and bcrypt.checkpw(
        password.encode('utf-8'), 
        usuario_encontrado['password'].encode('utf-8')):
        session["usuario"] = usuario_encontrado['correoElectronico']
        session["id_usuario"] = usuario_encontrado["idUsuarios"]
        flash("¡Bienvenido!", "success")
        return redirect(url_for("panel_principal"))
    else:
        flash("Usuario o contraseña incorrectos", "danger")
        return redirect(url_for("formulario_login"))


@app.route("/registro_personal", methods=["GET"])
def registro_personal():
    if "id_usuario" not in session:
        return redirect(url_for("formulario_login"))
    
    return render_template("registro_personal.html")

#Insertar
@app.route("/registro_personal", methods=["POST"])
def guardar_registro_personal():

    nombre = request.form["nombre"]
    tipoDocumento = request.form["tipoDocumento"]
    documento = request.form["documento"]
    genero = request.form["genero"]
    fechaNacimiento = request.form["fechaNacimiento"]
    edad = request.form["edad"]
    telefono = request.form["telefono"]
    direccion = request.form["direccion"]
    estadoCivil = request.form["estadoCivil"]
    bautizado = request.form["bautizado"]
    fechaBautismo = request.form["fechaBautismo"]

    id_usuario = session["id_usuario"]

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO personas (
                nombre,
                tipoDocumento,
                documento,
                genero,
                fechaNacimiento,
                edad,
                telefono,
                direccion,
                estadoCivil,
                bautizado,
                fechaBautismo,
                id_usuario
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre,
            tipoDocumento,
            documento,
            genero,
            fechaNacimiento,
            edad,
            telefono,
            direccion,
            estadoCivil,
            bautizado,
            fechaBautismo,
            id_usuario
        ))

        conexion.commit()

        if cursor.rowcount > 0:
            flash("Registro de datos exitoso", "success")
        else:
            flash("No se realizó la inserción de datos", "danger")

    except Exception as e:
        flash(f"Error: {e}", "danger")

    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for("personal"))
#Actualizar
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_persona(id):

    if "id_usuario" not in session:
        return redirect(url_for("formulario_login"))
    
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre"]
        tipoDocumento = request.form["tipoDocumento"]
        documento = request.form["documento"]
        genero = request.form["genero"]
        fechaNacimiento = request.form["fechaNacimiento"]
        edad = request.form["edad"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        estadoCivil = request.form["estadoCivil"]
        bautizado = request.form["bautizado"]
        fechaBautismo = request.form["fechaBautismo"]

        sql = """
            UPDATE personas SET 
            nombre = %s,
            tipoDocumento = %s,
            documento = %s,
            genero = %s,
            fechaNacimiento = %s,
            edad = %s,
            telefono = %s,
            direccion = %s,
            estadoCivil = %s,
            bautizado = %s,
            fechaBautismo = %s
            WHERE idPersonas = %s
            AND id_usuario =%s
        """
        cursor.execute(sql, (
            nombre,
            tipoDocumento,
            documento,
            genero,
            fechaNacimiento,
            edad,
            telefono,
            direccion,
            estadoCivil,
            bautizado,
            fechaBautismo,
            id,
            session ["id_usuario"]
        ) )

        conexion.commit()

        flash ("Datos actualizados correctamente", "success")

        cursor.close()
        conexion.close()

        return redirect(url_for("personal"))

    #peticion GET para buscar los datos actuales
    cursor.execute ("""
        SELECT * FROM personas
        WHERE idPersonas = %s
        AND id_usuario = %s
    """, (id, session["id_usuario"])
        
    )
    persona = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not persona:
        flash("Registro no encontrado", "danger")
        return redirect(url_for("personal"))

    return render_template("editar_persona.html", persona=persona)
#Eliminar

@app.route("/eliminar_persona/<int:id>")
def eliminar_persona(id):

    if "id_usuario" not in session:
        return redirect(url_for("formulario_login"))

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM personas
        WHERE idPersonas = %s
        AND id_usuario = %s
    """, (id, session["id_usuario"]))

    conexion.commit()

    cursor.close()
    conexion.close()

    flash("Registro eliminado", "success")

    return redirect(url_for("personal"))


@app.route("/home")
def panel_principal():

    if "id_usuario" not in session:
        return redirect(url_for("formulario_login"))

    return render_template("home.html")

@app.route("/personal")
def personal():
    
    if "id_usuario" not in session:
        return redirect(url_for("formulario_login"))

    conexion = conectar()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM personas 
            WHERE id_usuario = %s
        """, (session["id_usuario"],)
        )
            
        personas = cursor.fetchall()
        cursor.close()
    finally:
        conexion.close()

    return render_template("personal.html", personas=personas)

@app.route("/estado_personal")
def estado_personal():

    if "usuario" not in session:
        return redirect(url_for("formulario_login"))
    
    return render_template("estado_personal.html")

@app.route("/veredas")
def veredas():

    if "usuario" not in session:
        return redirect(url_for("formulario_login"))
    
    return render_template("veredas.html")

@app.route("/familias")
def familias():

    if "usuario" not in session:
        return redirect(url_for("formulario_login"))
    
    return render_template("familias.html")