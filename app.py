from flask import (
    Flask,
    render_template,
    send_from_directory,
    flash,
    session,
    request,
    url_for,
    redirect,
)
from urllib.parse import urlparse
import os
import pandas as pd
from formula import suggested, average_weekly_sales
""" from send_sms import send """
from playwright.sync_api import sync_playwright

is_production = os.environ.get("NODEV") == "production"

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

        UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # 2. Sanitizar el nombre y estructurar la ruta final en el servidor
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        ruta_guardada = os.path.join(UPLOAD_FOLDER, filename)
        
        # 3. Mover el puntero al inicio del buffer y guardar el archivo físico
        file.seek(0)
        file.save(ruta_guardada)

        file_uploaded = {"nombre": file.filename, "registros": register_proces}
        flash("¡Inventario cargado y analizado con éxito!", "success")


        session["registros_temporales"] = register_proces
        session["archivo"] = ruta_guardada 
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


""" @app.route("/send_order", methods=["POST"])
def send_order():
    contacto = request.form.get("contacto")
    data = session.get("registros_temporales", [])

    if not data:
        flash("No hay registros en la sesión para procesar.", "error")
        return redirect("/")

    # Cambio a comillas simples dentro de las llaves
    firma = f"{data[0]['firma']} - *Lider de Compra*"

    if contacto and not contacto.startswith("+"):
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
        if producto["pedido"] and float(producto["pedido"]) > 0:
            # Cambio a comillas simples dentro de las llaves
            mensaje_texto += f"{producto['N']}. {producto['codigo interno']} *{producto['articulo']}* - Cantidad: {producto['pedido']}\n"

    mensaje_texto += "\n_Por favor, confirma la recepción de esta orden._\n"
    mensaje_texto += firma

    order = send(contacto, mensaje_texto)

    if order is True:
        flash("El pedido se envió con éxito, revisa tu Whatsapp web", "success")
    else:
        flash("No se pudo enviar el pedido, intenta de nuevo más tarde", "error")

    return redirect("/")

"""

@app.route("/screenshot", methods=["GET"])
def screenshot():
    try:
        ruta_escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        nombre_archivo = "captura_flask.png"
        ruta_final = os.path.join(ruta_escritorio, nombre_archivo)

        ruta_archivo_subido = session.get('archivo')
        url_actual = request.url_root 
        parsed_url = urlparse(url_actual)
        url_base_limpia = f"{parsed_url.scheme}://{parsed_url.netloc}/"

        if not ruta_archivo_subido or not os.path.exists(ruta_archivo_subido):
            flash("No hay un archivo activo analizado para capturar.", "error")
            return redirect('/')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) 
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()
            
            page.goto(url_base_limpia, wait_until="networkidle")

            page.locator("#fileInput").set_input_files(str(ruta_archivo_subido))

            boton_enviar = page.locator('button[type="submit"], input[type="submit"]')
            boton_enviar.click()

            page.wait_for_selector("#table", state="visible", timeout=15000)

            page.evaluate("""() => {
    const btn = document.getElementById('btnSubmit');
    if (btn) {
        btn.removeAttribute('disabled');
        btn.classList.remove('bg-slate-300', 'text-slate-500', 'cursor-not-allowed');
        btn.classList.add('bg-orange-500', 'text-white', 'cursor-pointer'); // Cambia a tus colores activos si usas otros
    }
}""")

            page.add_style_tag(content="""
                #table th:nth-child(3), #table td:nth-child(3),
                #table th:nth-child(4), #table td:nth-child(4),
                #table th:nth-child(5), #table td:nth-child(5),
                #table th:nth-child(6), #table td:nth-child(6),
                #table th:nth-child(7), #table td:nth-child(7),
                #table th:nth-child(8), #table td:nth-child(8) {
                    display: none !important;
                }
            """)
        
            tabla = page.locator("#table") 
            tabla.screenshot(path=ruta_final)
            browser.close()

            flash("Captura realizada correctamente en tu Escritorio", "success")
            return redirect('/')
            
    except Exception as e:
        print(f"Error detectado: {str(e)}")
        flash(f"Error al tomar la captura: {str(e)}", "error")
        return redirect('/')
    
if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(debug= not is_production, host="0.0.0.0", port=puerto)
