from flask_mysqldb import MySQL

mysql = MySQL()

def init_db(app):
    # Configuración de la conexión a MySQL
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'unibase'

    try:
        # Inicializamos la extensión MySQL con la app de Flask
        mysql.init_app(app)
        print("Conexión a la base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error al inicializar MySQL: {e}")


# CREATE TABLE usuarios (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     nombre VARCHAR(100) NOT NULL,
#     correo VARCHAR(100) NOT NULL UNIQUE,
#     contrasena VARCHAR(255) NOT NULL
# );





