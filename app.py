from flask import Flask, render_template, request, redirect, session
from db import init_db, mysql  # Importamos la función y la variable mysql
import bcrypt
import MySQLdb.cursors


app = Flask(__name__)


# Clave secreta para sesiones y seguridad
app.secret_key = 'mi_clave_secreta'

# Inicializamos la base de datos
init_db(app)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None  # Variable para almacenar el mensaje de error

    if request.method == "POST":
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        foto = ""
        usuario = request.form['usuario']
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        # Validar que los campos no estén vacíos
        if not nombre or not correo or not contrasena:
            error = "Por favor, completa todos los campos."
        else:
            # Hash de la contraseña usando bcrypt
            hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            try:
                cursor.execute("INSERT INTO usuario (nombre, apellido, foto, nombre_usuario, correo, contrasena) VALUES (%s, %s, %s, %s, %s, %s)", (nombre, apellido, foto, usuario, correo,hashed_password))
                mysql.connection.commit()
                return redirect("/login")
            except MySQLdb.IntegrityError:
                error = "El correo ya está registrado."
            finally:
                cursor.close()

    return render_template('registro.html', error=error)


@app.route("/login", methods=["GET", "POST"])
def login():

    error = None  # Variable para el mensaje de error

    if request.method == "POST":
        # Recibir los datos del formulario
        correo = request.form['correo']
        contrasena = request.form['contrasena'].encode('utf-8')  # Convertimos la contraseña a bytes

        # Validar que los campos no estén vacíos
        if not correo or not contrasena:
            error = "Por favor, completa todos los campos."
        else:
            # Conexión a la base de datos para obtener el usuario
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
            usuario = cursor.fetchone()  # Obtenemos el registro
            cursor.close()

            if usuario:
                # Comparar la contraseña ingresada con la encriptada almacenada
                if bcrypt.checkpw(contrasena, usuario['contrasena'].encode('utf-8')):
                    # Inicio de sesión exitoso, puedes redirigir al usuario
                    # Almacenar el ID del usuario en la sesión
                    session['usuario_id'] = usuario['id']
                    session['usuario_nombre'] = usuario['nombre']
                    return redirect("/")
                else:
                    error = "Contraseña incorrecta."
            else:
                error = "Correo no registrado."

    return render_template('login.html', error=error)


@app.route("/perfil")
def perfil():
    if 'usuario_id' not in session:
        return redirect("/login")  # Redirige al login si no está autenticado

    # Datos del usuario en la sesión
    usuario_nombre = session['usuario_nombre']
    
    return render_template("perfil.html", nombre=usuario_nombre)


@app.route("/logout")
def logout():
    # Limpiar la sesión
    session.pop('usuario_id', None)
    session.pop('usuario_nombre', None)
    return redirect("/login")


app.run(host="0.0.0.0", port=5001, debug=True)






