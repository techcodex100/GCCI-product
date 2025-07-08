from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from typing import Optional
from io import BytesIO
import os
import sys  # ✅ Added to check Python version

app = FastAPI(
    title="GCCI Certificate Generator",
    description="Generates GCCI Certificate of Origin (Non-Preferential) PDF with headings and background image",
    version="1.0.0"
)

class CertificateOfOriginData(BaseModel):
    exporter_name_address: Optional[str] = ""
    certificate_number: Optional[str] = ""
    consignee_name_address: Optional[str] = ""
    transport_details: Optional[str] = ""
    official_use: Optional[str] = ""
    item_number: Optional[str] = ""
    package_marks: Optional[str] = ""
    package_description: Optional[str] = ""
    origin_criteria: Optional[str] = ""
    gross_weight: Optional[str] = ""
    invoice_number_date: Optional[str] = ""
    hs_code: Optional[str] = ""
    certificate_place_date: Optional[str] = ""
    certificate_signature: Optional[str] = ""
    exporter_declaration_place_date: Optional[str] = ""
    exporter_signature: Optional[str] = ""
    importing_country: Optional[str] = ""

@app.get("/")
def root():
    return {"message": "GCCI Certificate Generator is live. Use POST /generate-origin-certificate-pdf/"}

# ✅ Added this route to check Python version on Render
@app.get("/python-version")
def get_python_version():
    return {"python_version": sys.version}

@app.post("/generate-origin-certificate-pdf/")
def generate_certificate(data: CertificateOfOriginData):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Background image
        bg_path = r"C:\Users\Lenovo\OneDrive\Desktop\certificate GCCI\bggcci.jpg"
        if os.path.exists(bg_path):
            c.drawImage(ImageReader(bg_path), 0, 0, width=width, height=height)
        else:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(100, 800, "⚠️ Missing background image: bggcci.jpg")

        # Helper functions
        def draw_heading(text, x, y):
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x, y, text)

        def draw_multiline(text, x, y_start, line_height=10):
            c.setFont("Helvetica", 8)
            for i, line in enumerate(text.splitlines()):
                c.drawString(x, y_start - i * line_height, line)

        # Header Fields
        draw_multiline("1. Goods consigned from\n(Exporter's name, address, country)", 30, 740)
        draw_multiline(data.exporter_name_address, 30, 720)

        draw_heading("Certificate of Origin No.", 295, 740)
        c.setFont("Helvetica", 8)
        c.drawString(295, 730, data.certificate_number)

        draw_multiline("2. Goods consigned to\n(Consignee's name, address, country)", 30, 585)
        draw_multiline(data.consignee_name_address, 30, 560)

        draw_multiline("3. Means of transport and route\n(as far as known)", 30, 480)
        draw_multiline(data.transport_details, 30, 460)

        draw_heading("4. For official use", 300, 480)
        draw_multiline(data.official_use, 300, 470)

        # Description Table Section
        draw_multiline("5. Item number", 30, 385)
        draw_multiline("6. Marks and numbers\nof packages", 125, 385)
        draw_multiline("7. Number and kind \nof packages,\ndescription of goods", 210, 385)
        draw_multiline("8. Origin criteria", 300, 385)
        draw_multiline("9. Gross weight or\nother quantity", 390, 385)
        draw_multiline("10. Number and date\nof invoices", 482, 385)

        c.setFont("Helvetica", 8)
        c.drawString(30, 300, data.item_number)
        draw_multiline(data.package_marks, 125, 300)
        draw_multiline(data.package_description, 210, 300)
        c.drawString(300, 300, data.origin_criteria)
        c.drawString(390, 300, data.gross_weight)
        draw_multiline(data.invoice_number_date, 482, 300)

        draw_heading("H.S. CODE", 270, 330)
        c.setFont("Helvetica", 8)
        c.drawString(270, 320, data.hs_code)

        # Certification Section
        draw_heading("11. Certification", 30, 150)
        draw_multiline(
            "It is hereby certified, on the basis of control carried out,\n"
            "that the declaration by the exporter is correct.", 30, 135)
        draw_multiline(data.certificate_place_date, 30, 100)

        # Exporter Declaration Section
        draw_heading("12. Declaration by the exporter", 300, 150)
        c.setFont("Helvetica", 8)
        c.drawString(300, 70, f"...exports to: {data.importing_country}")
        draw_multiline(data.exporter_declaration_place_date, 300, 140)
        draw_multiline(
            "The undersigned hereby declares by the above \ndetails and statements are correct\n"
            "that all the goods were produced in india and that \nthey comply with the origin requirements for \nexport to", 300, 130)

        c.save()
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=certificate_of_origin.pdf"}
        )

    except Exception as e:
        print("⚠️ PDF generation failed:", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
