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
                clane(row.get("SEM1")),
                clane(row.get("SEM2")),
                clane(row.get("SEM3")),
                clane(row.get("SEM4")),
                clane(row.get("SEM5")),
            ]

            # dicionario de la informacion del producto para el calculo
            product_data = {
                "average_sale": average_weekly_sales(pre_sale),
                "replenishment_time": int(
                    row.get("Tiempo_Reposicion", row.get("tiempo_reposicion", 1))
                ),
                "current_stock": int(row.get("I_NETO", row.get("cantidad_en_mano", 0))),
                "safety_stock": int(row.get("MIN", row.get("stock_seguridad", 0))),
                "packing": int(row.get("UXE", row.get("empaque", 1))),
            }

            final_amount = suggested(product_data)

            register = {
                "interno": str(row.get("ITEM", row.get("interno", "N/A"))).strip(),
                "descripcion": str(
                    row.get("ITEM_LONG_DESC", row.get("descripcion", "Sin Nombre"))
                ).strip(),
                "cantidad": int(row.get("I_NETO", row.get("cantidad_en_mano", 0))),
                "sugerida_UXE": final_amount["cantidad"],
                "sugerida_empaque": final_amount["empaque"],
                "venta_promedio": average_weekly_sales(pre_sale),
                "empaque": str(row.get("UXE", row.get("empaque", 1))),
                "estatus": str(row.get("S", row.get("estatus", "C"))),
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
    puerto = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=puerto)
