from typing import Text
from flask import Flask, render_template, flash, request, redirect
import os
import pandas as pd
from pandas.core.arrays import boolean
from formula import suggested, average_weekly_sales
from dotenv import load_dotenv

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET", "ORDER_S")

# Extenciones de archivos permitdas
ALLOWED_EXTENSIONS = {".xlsx", ".xls", "csv"}

version = os.getenv("APP_VERSION", "1.0.0")


@app.route("/")
def home():
    """Ruta index de app"""
    return render_template("index.html", version=version)


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

        def clane(value: str) -> tuple[float | int, bool]:
            """Limpia un texto, lo convierte a número e identifica si es pesable.

            Args:
                value (str): Texto o valor a procesar.

            Returns:
                tuple[float | int, bool]: Una tupla con (valor_numerico, es_pesable).
            """

            text = str(value).strip().replace(",", ".")

            if text in ["", "None", "nan", "NaN"]:
                return 0, False

            try:
                val = float(text)

                is_weighable = not val.is_integer()

                number = val if is_weighable else int(val)

                return number, is_weighable
            except ValueError:
                return 0, False

        def truncar(numero, decimales, weighable):
            """Corta los decimales de una cademan de numeros muy larga"""
            if weighable:
                factor = 10**decimales
                return int(numero * factor) / factor

            return int(round(numero))

        for _, row in df.iterrows():

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
                "replenishment_time": float(
                    row.get("Tiempo_Reposicion", row.get("tiempo_reposicion", 1))
                ),
                "current_stock": float(
                    float(row.get("I_NETO", row.get("cantidad_en_mano", 0)))
                ),
                "packing": int(row.get("UXE", row.get("empaque", 1))),
                "is_weighable": average_weekly_sales(pre_sale).get("pesable", False),
            }

            final_amount = suggested(product_data)
            vp = average_weekly_sales(pre_sale)

            register = {
                "interno": str(row.get("ITEM", row.get("interno", "N/A"))).strip(),
                "descripcion": str(
                    row.get("ITEM_LONG_DESC", row.get("descripcion", "Sin Nombre"))
                ).strip(),
                "cantidad": str(row.get("I_NETO", row.get("cantidad_en_mano", 0))),
                "sugerida_UXE": final_amount["cantidad"],
                "sugerida_empaque": final_amount["empaque"],
                "venta_promedio": truncar(vp["vp"], 2, final_amount.get("pesable")),
                "vp_diaria": truncar(vp["vp_diaria"], 2, final_amount.get("pesable")),
                "empaque": str(row.get("UXE", row.get("empaque", 1))),
                "estatus": str(row.get("S", row.get("estatus", "C"))),
                "stock_seguridad": truncar(
                    (
                        final_amount.get("stock_seguridad", 0)
                        if isinstance(final_amount, dict)
                        else 0
                    ),
                    2,
                    final_amount.get("pesable"),
                ),
                "stock_ideal": truncar(
                    final_amount.get("stock_ideal", 0), 2, final_amount.get("pesable")
                ),
                "pesable": final_amount.get("pesable"),
            }
            register_proces.append(register)

        file_uploaded = {"nombre": file.filename, "registros": register_proces}
        flash("¡Inventario cargado y analizado con éxito!", "success")
        return render_template("index.html", file=file_uploaded, version=version)
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
