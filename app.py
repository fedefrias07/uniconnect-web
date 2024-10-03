from flask import Flask, render_template, request, redirect, session
from db import init_db, mysql  # Importamos la función y la variable mysql
import bcrypt, MySQLdb.cursors, os 
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)

app.secret_key = os.urandom(24)  # Genera una clave secreta aleatoria para sesiones y seguridad

# Configuraciones de cookies de sesión
app.config['SESSION_COOKIE_SECURE'] = True  # Solo se envían a través de HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No accesibles a JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Previene ataques CSRF

# Protección contra Ataques CSRF
csrf = CSRFProtect(app)

# Inicializamos la base de datos
init_db(app)


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/auth", methods=["GET", "POST"])
def auth():
    error_registro = None  # Variable para almacenar el mensaje de error
    error_login = None  # Variable para almacenar el mensaje de error

    if request.method == "POST":
        action = request.form.get('action')

        if action == 'register':  # Registro
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            foto = ""
            nombre_usuario = request.form['nombre_usuario']
            correo = request.form['correo']
            contrasena = request.form['contrasena']
            confirmar_contrasena = request.form['confirmar_contrasena']

            # Validar que los campos no estén vacíos
            if not nombre or not correo or not contrasena or not apellido or not nombre_usuario:
                error_registro = "Por favor, completa todos los campos."
            elif contrasena != confirmar_contrasena:
                error_registro = "Las contraseñas no coinciden."
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                
                # Verificar si el correo ya existe
                cursor.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
                correo_registrado = cursor.fetchone()

                # Verificar si el nombre de usuario ya existe
                cursor.execute("SELECT * FROM usuario WHERE nombre_usuario = %s", (nombre_usuario,))
                usuario_registrado = cursor.fetchone()

                if correo_registrado:
                    error_registro = "El correo ya está registrado."
                elif usuario_registrado:
                    error_registro = "El nombre de usuario ya está registrado." 
                else:
                    # Hash de la contraseña usando bcrypt
                    hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

                    try:
                        # Insertar el nuevo usuario
                        cursor.execute(
                            "INSERT INTO usuario (nombre, apellido, foto, nombre_usuario, correo, contrasena) VALUES (%s, %s, %s, %s, %s, %s)",
                            (nombre, apellido, foto, nombre_usuario, correo, hashed_password)
                        )
                        mysql.connection.commit()
                        return redirect("/auth")
                    except MySQLdb.IntegrityError:
                        error_registro = "Ocurrió un error al registrarse."
                    finally:
                        cursor.close()

        elif action == 'login':  # Inicio de sesión
            correo = request.form['correo']
            contrasena = request.form['contrasena'].encode('utf-8')

            # Validar que los campos no estén vacíos
            if not correo or not contrasena:
                error_login = "Por favor, completa todos los campos."
            else:
                # Conexión a la base de datos para obtener el usuario
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
                usuario = cursor.fetchone()  # Obtenemos el registro
                cursor.close()

                if usuario:
                    # Comparar la contraseña ingresada con la encriptada almacenada
                    if bcrypt.checkpw(contrasena, usuario['contrasena'].encode('utf-8')):
                        # Inicio de sesión exitoso, redirigir al usuario
                        session['usuario_id'] = usuario['id_usuario']
                        session['usuario_nombre'] = usuario['nombre']
                        return redirect("/")
                    else:
                        error_login = "Credenciales incorrectas."
                else:
                    error_login = "Correo no registrado."
    return render_template('auth/auth.html', error_login=error_login, error_registro= error_registro)



@app.route("/perfil")
def perfil():
    if 'usuario_id' not in session:
        return redirect("/auth")  # Redirige al login si no está autenticado

    # Datos del usuario en la sesión
    usuario_nombre = session['usuario_nombre']
    
    return render_template("perfil.html", nombre=usuario_nombre)


@app.route("/logout")
def logout():
    # Limpiar la sesión
    session.pop('usuario_id', None)
    session.pop('usuario_nombre', None)
    return redirect("/auth")


# Manejo de errores - > Falta terminar...
@app.errorhandler(400)
def handle_bad_request(e):
    # Verificamos si el error está relacionado con CSRF
    if 'The CSRF session token is missing' in str(e):
        return render_template('errors/csrf_error.html'), 400
    return render_template('errors/400.html'), 400  # Otro error 400 genérico


app.run(host="0.0.0.0", port=5001, debug=True)






