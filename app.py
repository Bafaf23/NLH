from cProfile import label
from os import name
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
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")
app.secret_key = "estoy_cansado_jefe"

mysql = MySQL()

""" Configuracion de la comection """
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "bafaf"
app.config["MYSQL_DATABASE_PASSWORD"] = "jpE1X^3Y%PfmZ0764#GB"
app.config["MYSQL_DATABASE_DB"] = "rbo_db"

mysql.init_app(app)


@app.route("/")
def home():
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
        },
        {
            "label": "Cambiar rol",
            "link": "#",
            "icon": '<i class="fa-solid fa-address-card text-cyan-400"></i>',
        },
    ]
    return render_template("index.html", saludo=saludo, news=news, link=link)


@app.route("/auth", methods=["GET", "POST"])
def register():
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
                print(valores)
                cur.execute(sql, valores)
                conn.commit()
                print("You have successfully registered!")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    return render_template("auth/register.html")


@app.route("/", methods=["GET", "POST"])
def login():
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
                    session["loggedin"] = True
                    session["id"] = user["id"]
                    session["name"] = user["name"]
                    session["lastName"] = user["last_name"]
                    session["email"] = user["email"]
                    session["role"] = user["rol"]

                    print(f"Sesión iniciada para: {user['name']}")
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
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("name", None)
    session.pop("lastName", None)
    session.pop("email", None)
    session.pop("role", None)

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
