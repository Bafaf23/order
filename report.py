from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
import time

my_color = HexColor("#9e9ea1")
style = ParagraphStyle(
    "Justificado",
    fontName="Helvetica",
    fontSize=10,
    leading=15,
    alignment=TA_JUSTIFY,
    textColor=my_color,
)

pdf = canvas.Canvas("Resumen_del_pedido.pdf")

# encabezado
proveedor = "Andres Misle"
date = time.strftime("%d/%m/%Y")
text_header = (
    "Les compartimos la información de nuestra solicitud.\n"
    "¡Estamos en contacto para cualquier consulta!\n"
)
y = 780

pdf.drawAlignedString(150, 800, f"Hola, {proveedor}")

for line in text_header.split("\n"):
    pdf.drawAlignedString(325, y, line)
    y -= 18

pdf.drawAlignedString(520, y, f"Fecha de la solicitud: {str(date)}")


# pie de pagina
text = (
    "El siguiente no es una orden de compra generada por tu cliente.\n"
    "Si después de recibir este documento no recibes la orden oficial,\n"
    "ponte en contacto con el vendedor de tu cliente,\n"
    "confirmando las cantidades solicitadas."
)

parrafo = Paragraph(text, style)
ancho = 500

_, alto = parrafo.wrap(ancho, 200)
parrafo.drawOn(pdf, 50, 90 - alto)

pdf.save()
