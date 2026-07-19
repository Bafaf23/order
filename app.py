from flask import Flask, render_template, flash, request, redirect
import os
import pandas as pd
from formula import suggested, average_weekly_sales

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET", "ORDER_S")

# Extenciones de archivos permitdas
ALLOWED_EXTENSIONS = {".xlsx", ".xls", "csv"}


@app.route("/")
def home():
    """Ruta index de app"""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    """Obtiene el archvo para procesarlo eliminarndo los espacios en blancos"""
    file = request.files.get("file")

    if not file or file.filename == "":
        flash("Por favor, seleciona un archivo valido.", "error")
        return redirect("/")

    file_name, extention = os.path.splitext(file.filename.lower())
    print(f"Procesando {file_name}")
    print(f"Formato {extention}")

    if extention not in ALLOWED_EXTENSIONS:
        flash(
            f"Formato {extention} no soportado. Sube un archivo Excel o CSV.", "error"
        )
        return redirect("/")

    try:
        if extention == ".csv":
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, dtype=str)

        df.dropna(how="all", inplace=True)
        df.fillna("", inplace=True)

        register_proces = []
        for _, row in df.iterrows():

            def clane(value: str) -> int:
                """Limpia un text para trasformarlo a numero
                Args:
                    value (str): valor para limpiar y convertir
                Returns:
                    int: value formateado
                """
                text = str(value).strip()

                if text in ["", "None", "nan", "NaN"]:
                    return 0

                return float(text)

            pre_sale = [
                clane(row.get("SM1")),
                clane(row.get("SM2")),
                clane(row.get("SM3")),
                clane(row.get("SM4")),
            ]

            # Variables para el calculo
            vp = average_weekly_sales(pre_sale)
            tr = float(row.get("Tiempo_Reposicion", row.get("tiempo_reposicion", 1)))
            sa = float(row.get("Cantida en Mano", row.get("cantida en mano", 0)))
            ss = float(row.get("Stock_Seguridad", row.get("stock_seguridad", 0)))

            final_amount = suggested(vp, tr, sa, ss)

            register = {
                "interno": str(row.get("interno", row.get("Interno", "N/A"))).strip(),
                "descripcion": str(
                    row.get("Descripción", row.get("descripcion", "Sin Nombre"))
                ).strip(),
                "cantidad": int(
                    row.get("Cantidad en Mano", row.get("cantidad_en_mano", 0))
                ),
                "sugerida": final_amount,
                "venta_promedio": vp,
            }
            register_proces.append(register)

        file_uploaded = {"nombre": file.filename, "registros": register_proces}
        flash("¡Inventario cargado y analizado con éxito!", "success")
        return render_template("index.html", file=file_uploaded)
    except Exception as e:
        print(f"Error procesando el archivo {str(e)}")
        flash(
            "Ocurrio un error al procesar la estructura del archivo. Revisa las columnas.",
            "error",
        )
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
