from types import TracebackType
from flask import (
    Flask,
    redirect,
    render_template,
    template_rendered,
    request,
    session,
    url_for,
)
import pymysql
from datetime import datetime
from datetime import timedelta
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")
app.secret_key = "estoy_cansado_jefe"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

mysql = MySQL()

""" Configuracion de la comection """
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "bafaf"
app.config["MYSQL_DATABASE_PASSWORD"] = "jpE1X^3Y%PfmZ0764#GB"
app.config["MYSQL_DATABASE_DB"] = "rbo_db"

mysql.init_app(app)


@app.route("/")
def home():
    """
    Renderiza la página de inicio con saludo dinámico y noticias.

    Determina el saludo (Buenos días/tardes/noches) según la hora actual del servidor
    y carga una lista estática de noticias y enlaces de navegación para el index.

    Returns:
        html: Plantilla 'index.html' con el contexto de saludo, noticias y links.
    """
    hora = datetime.now().hour
    if hora < 12:
        saludo = "Buenos días"
    elif 12 <= hora < 18:
        saludo = "Buenas tardes"
    else:
        saludo = "Buenas noches"

    news = [
        {
            "title": "Nuevos Puntos BBVA",
            "desc": "Ahora acumulas más por cada compra con tu tarjeta.",
            "tag": "Promoción",
            "img": "https://appmarketingnews.io/wp-content/uploads/2023/03/MODO-OSCURO-1024x653.jpg",
        },
        {
            "title": "Seguridad Blue AI",
            "desc": "Tu cuenta ahora está protegida por nuestra nueva IA.",
            "tag": "Seguridad",
            "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8fecv0RAaXDNaoyO50AhLRKd7qOaHJC7Npg&s",
        },
    ]

    link = [
        {
            "label": "Posicion Gobal",
            "link": "#",
            "icon": '<i class="fa-solid fa-globe text-cyan-400"></i>',
        }
    ]
    return render_template("index.html", saludo=saludo, news=news, link=link)


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Gestiona el registro de nuevos usuarios en el sistema.

    Procesa peticiones GET para mostrar el formulario y POST para validar 
    e insertar datos en la base de datos MySQL.

    Campos del formulario (POST):
        typeDocument (str): Tipo de documento (ej. 'V', 'E').
        document (str): Número de identificación.
        nameUser (str): Nombre del usuario.
        lastName (str): Apellido del usuario.
        email (str): Correo electrónico (debe ser único).
        birthdate (str): Fecha de nacimiento.
        password (str): Contraseña en texto plano.
        confirm_password (str): Verificación de contraseña.

    Returns:
        render_template: Redirección a la vista de registro (auth/register.html)
        con o sin mensajes de éxito/error.

    Raises:
        Exception: Captura errores de conexión a la base de datos o ejecución de SQL.
    """
    try:
        if (
            request.method == "POST"
            and "nameUser" in request.form
            and "password" in request.form
        ):
            typeDocument = request.form["typeDocument"]
            document = request.form["document"]
            nameUser = request.form["nameUser"]
            lastName = request.form["lastName"]
            email = request.form["email"]
            birthdate = request.form["birthdate"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            dni = f"{typeDocument}{document}"

            if confirm_password != password:
                print("las claves no son iguales")
                return render_template("auth/register.html")

            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)

            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            account = cur.fetchone()

            if account:
                print("El usuario ya esta registrado")
                return render_template("auth/register.html")

            else:
                password_encriptada = generate_password_hash(password)
                sql = "INSERT INTO users (dni, name, last_Name, email, birthdate, pass) VALUES(%s,%s,%s,%s,%s,%s)"

                valores = (
                    dni,
                    nameUser,
                    lastName,
                    email,
                    birthdate,
                    password_encriptada,
                )
                cur.execute(sql, valores)
                conn.commit()
                print("You have successfully registered!")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Gestiona la autenticación de usuarios y creación de sesiones.

    Valida las credenciales del usuario contra la base de datos. Si son correctas,
    inicializa la sesión de Flask con los datos del perfil y redirige al home.

    Flujo:
        1. Recibe email y password vía POST.
        2. Busca al usuario por email.
        3. Verifica el hash de la contraseña.
        4. Almacena: 'loggedin', 'id', 'name', 'lastName', 'email' y 'role' en session.

    Returns:
        redirect: Redirección a url_for('home') tanto en éxito como en fallo.
    
    Note:
        Los fallos de autenticación actualmente solo imprimen en consola y
        redirigen al home sin mensajes de error visuales.
    """
    try:
        if (
            request.method == "POST"
            and "email" in request.form
            and "pass" in request.form
        ):
            email = request.form["email"]
            password = request.form["pass"]

            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT * FROM users WHERE email = %s"
            valor = email

            cur.execute(sql, valor)
            user = cur.fetchone()

            if user:
                if check_password_hash(user["pass"], password):

                    if request.form.get("remember"):
                        session.permanent = True
                    else:
                        session.permanent = False

                    session["loggedin"] = True
                    session["id"] = user["id"]
                    session["name"] = user["name"]
                    session["lastName"] = user["last_name"]
                    session["email"] = user["email"]
                    session["role"] = user["rol"]

                    print(f"Sesión iniciada para: {user['name']}")

                    if session['role'] == "administrador":
                        return redirect(url_for("dashboard"))
                    else:
                        return redirect(url_for("home"))

                else:
                    print("Usuario o clave errada 404")
            else:
                print("Usuario no entontrado")

    except Exception as e:
        print(f"hubo un error {e}")

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    """
    Finaliza la sesión activa del usuario.

    Elimina todas las claves de identificación del diccionario de sesión de Flask 
    para asegurar que el usuario no pueda acceder a rutas protegidas.

    Returns:
        redirect: Redirección a la página de inicio (home) tras cerrar sesión.
    """
    session.clear()

    return redirect(url_for("home"))


@app.route("/update_role/<int:id_user>", methods=["POST"])
def update_role(id_user: str) -> str:
    """
    Actualiza el rol de un usuario en la base de datos y en la sesión activa.

    Modifica el campo 'rol' del usuario especificado y, si el usuario editado 
    es el mismo que tiene la sesión iniciada, actualiza sus permisos en tiempo real.

    Args:
        id_user (int/str): Identificador único del usuario a modificar.

    Form Params (POST):
        new_role (str): El nuevo nombre o nivel del rol (ej. 'admin', 'user').

    Returns:
        redirect: Redirección al 'home' en caso de éxito.
        tuple: Mensaje de error y código de estado 500 en caso de fallo.

    """
    new_role = request.form.get("new_role")

    try:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("UPDATE users SET rol = %s WHERE id = %s", (new_role, id_user))
        conn.commit()
        cur.close()

        if session.get("id") == id_user:
            session["role"] = new_role

        return redirect(url_for("home"))
    except Exception as e:
        print(f"hubo un error{e}")
        return f"Error al actualizar: {e}", 500


@app.route("/dashboard")
def dashboard():

    def count_users():
        conn = mysql.connect()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM users")

        total = cur.fetchone()[0]
        cur.close()
        return total
    
    def get_info_user():
        """
        Obtiene todos los usuarios de la base de datos y los renderiza en una tabla.
        """
        try:
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            cur.execute("SELECT id, dni, name, last_name, email, rol FROM users")
            usuarios = cur.fetchall()
            cur.close()

            return usuarios
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return redirect(url_for("home"))

    get_info_user()

    return render_template("page/dashboard.html", user_total=count_users(), list_user=get_info_user())

@app.route("/verify_credentials", methods=["POST"])
def verify_credentials():
    """
    Verificacion de credenciales para aceder al dashboard
    """
    if "id" not in session:
        render_template("index")

    password = request.form.get("pass_verify")
    user_id = session["id"]

    try:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT pass FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user["pass"], password):
            return redirect(url_for("dashboard")) if session["role"] == "administrador" else  redirect(url_for("meme"))
        else:
            print("Clave incorrecta")
            return redirect(url_for("home"))

    except Exception as e:
        print(f"Error en verificación: {e}")
        return redirect(url_for("home"))


@app.route("/delete_user/<int:id_user>", methods=["DELETE"])
def delete(id_user):
    """ Elimina al usuario de la base datos mediante una peticion AJAX"""
    try:
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (id_user,))
        con.commit()
        con.close()

        return {"status": "success",  "message": "Usuario eliminado"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/meme")
def meme():
    return render_template("/page/meme.html")

if __name__ == "__main__":
    app.run(debug=True)