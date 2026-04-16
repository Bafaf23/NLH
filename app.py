from os import name
from flask import Flask, render_template, template_rendered, request, session
import pymysql
from datetime import datetime
from flaskext.mysql import MySQL

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

    return render_template("index.html", saludo=saludo, user=None, news=news)


@app.route("/auth", methods=["GET", "POST"])
def register():
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
            id_role_default = 2
            sql = "INSERT INTO users (dni, name, last_Name, email, birthdate, pass, role_id) VALUES(%s,%s,%s,%s,%s,%s,%s)"

            valores = (
                dni,
                nameUser,
                lastName,
                email,
                birthdate,
                password,
                id_role_default,
            )
            print(valores)
            cur.execute(sql, valores)
            conn.commit()
            print("You have successfully registered!")

    return render_template("auth/register.html")


if __name__ == "__main__":
    app.run(debug=True)
