import pytest
from pathlib import Path

from access_request_poc import ocr


def test_ocr_on_generated_pdf(tmp_path):
    # Create a small PDF using reportlab if available
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        pytest.skip("reportlab not installed")

    txt = "Employee ID: E-9001\nDepartment: Finance\nRequested Role: Finance Analyst\nManager Approved: Yes\n"
    pdf_path = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    y = height - 40
    for line in txt.splitlines():
        c.drawString(40, y, line)
        y -= 14
    c.save()

    extracted = ocr.ocr_pdf(str(pdf_path))
    if extracted is None:
        pytest.skip("OCR runtime (pdf2image/pytesseract) not available")

    assert "Employee ID" in extracted or "E-9001" in extracted
