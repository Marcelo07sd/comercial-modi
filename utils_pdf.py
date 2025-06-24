# utils_pdf.py
from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generar_pdf_venta(cliente, venta, detalles):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Boleta de Venta")

    pdf.drawString(50, 750, f"Comercial Alex 2025 - Boleta de Venta")
    pdf.drawString(50, 735, f"Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    pdf.drawString(50, 720, f"Cliente: {cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}")
    pdf.drawString(50, 705, f"DNI: {cliente.dni}")

    y = 680
    pdf.drawString(50, y, "Detalle de Productos:")
    y -= 20

    for item in detalles:
        nombre = item.producto.nombre
        cantidad = item.cantidad
        precio = item.precio_unitario
        subtotal = round(cantidad * precio, 2)
        pdf.drawString(60, y, f"- {nombre} x{cantidad} = S/ {subtotal}")
        y -= 15

    pdf.drawString(50, y - 10, f"Tipo de pago: {venta.tipo_pago}")
    pdf.drawString(50, y - 25, f"Total: S/ {venta.total}")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='boleta.pdf', mimetype='application/pdf')
