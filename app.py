from flask import Flask, render_template, template_rendered
from datetime import datetime

app = Flask(__name__, template_folder="templates")


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


@app.route("/auth/register")
def register():
    return render_template("auth/register.html")


if __name__ == "__main__":
    app.run(debug=True)
