from flask import (
    Flask,
    render_template,
    send_from_directory,
    flash,
    session,
    request,
    redirect,
)
import os
import pandas as pd
from formula import suggested, average_weekly_sales
from send_sms import send
from dotenv import load_dotenv

app = Flask(__name__, template_folder="templates")


# Extenciones de archivos permitdas
ALLOWED_EXTENSIONS = {".xlsx", ".xls", "csv"}

version = os.getenv("APP_VERSION", "1.0.0")
app.secret_key = os.environ.get("SECRET", "ORDER_S")


@app.route("/")
def home():
    """Ruta index de app"""
    return render_template("index.html", version=version)


@app.route("/ads.txt")
def ads_txt():
    """Sirve ads.txt ubicado en la raíz del directorio del proyecto."""
    return send_from_directory(app.root_path, "ads.txt", mimetype="text/plain")


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

        contac = None
        firma = None
        for _, row in df.iterrows():

            if pd.notna(row["contacto"]) and str(row["contacto"]).strip() != "":
                contac = str(row.get("contacto", "S/C"))
                firma = str(row.get("firma", "S/N"))

            pre_sale = [
                row.get("ITEM", row.get("interno")),
                row.get("ITEM_LONG_DESC", row.get("descripcion")),
                clane(row.get("SEM1")),
                clane(row.get("SEM2")),
                clane(row.get("SEM3")),
                clane(row.get("SEM4")),
                clane(row.get("SEM5")),
            ]

            ventas_calculadas = average_weekly_sales(pre_sale)

            # dicionario de la informacion del producto para el calculo
            product_data = {
                "average_sale": ventas_calculadas,
                "replenishment_time": float(
                    row.get("tiempo_reposicion", 2)
                ),  # Lee el '2' de tu tabla
                "current_stock": float(row.get("I_NETO", 0)),
                "packing": float(row.get("UXE", 1)),
                "is_weighable": ventas_calculadas.get("pesable", False),
                "frecuencia_despacho": int(row.get("frecuencia", 2)),
            }

            final_amount = suggested(product_data)

            # Ya no necesitas volver a llamar a la función aquí, usamos la variable de arriba
            vp = ventas_calculadas

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
                "contac": contac,
                "firma": firma,
            }
            register_proces.append(register)

        file_uploaded = {"nombre": file.filename, "registros": register_proces}
        flash("¡Inventario cargado y analizado con éxito!", "success")
        session["registros_temporales"] = register_proces
        return render_template(
            "index.html", file=file_uploaded, version=version, contact=contac
        )
    except Exception as e:
        print(f"Error procesando el archivo {str(e)}")
        flash(
            "Ocurrio un error al procesar la estructura del archivo. Revisa las columnas.",
            "error",
        )
        return redirect("/")


@app.route("/send_order", methods=["POST"])
def send_order():
    contacto = request.form.get("contacto")
    data = session.get("registros_temporales", [])
    firma = f"{data[0]["firma"]} - *Lider de Compra (Central Madeirense)*"

    if not contacto.startswith("+"):
        contacto = "+" + contacto

    message = []

    for i, row in enumerate(data):

        register = {
            "N": i,
            "codigo interno": row.get("interno"),
            "articulo": row.get("descripcion"),
            "pedido": row.get("sugerida_UXE"),
        }

        message.append(register)

    mensaje_texto = "📦 *Resumen del Pedido:*\n\n"

    for producto in message:
        if producto["pedido"] > 0:
            mensaje_texto += f"{producto['N']}. {producto["codigo interno"]} *{producto['articulo']}* - Cantidad: {producto['pedido']}\n"

    mensaje_texto += "\n_Por favor, confirma la recepción de esta orden._\n"
    mensaje_texto += firma

    order = send(contacto, mensaje_texto)

    if order == True:
        flash("El pedido se envio con exito, revisa tu Whatsapp web", "success")
    else:
        flash("No se pudo enviar el pedido, intenta de nuevo más tarde", "error")

    return redirect("/")


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=puerto)
