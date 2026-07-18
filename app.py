from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")


@app.route("/")
def home():
    """ Ruta index de app """
    file_uploaded = None
    return render_template("index.html", file=file_uploaded)


@app.route("/upload", methods=["POST"])
def upload_file():
    """Porcesa los archivos"""
    print("Hola")
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)


    """ {
        "nombre":"Resumen de Ventas, inventario para generar ordenes de compras",
        "registros":[
            {
                "codigo":"10098766",
                "descripcion":"Auyama kg",
                "sugerencia":"",
            },
            {
                "codigo":"1009876655",
                "descripcion":"Papa Lavada kg",
                "sugerencia":"",
            },
            {
                "codigo":"100564333",
                "descripcion":"Zanahoria kg",
                "sugerencia":"",
            },
        ]
    } """