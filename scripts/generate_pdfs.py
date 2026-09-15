from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
import json


def txt_to_pdf_with_annotations(txt_path: Path, pdf_path: Path, meta_path: Path):
    text = txt_path.read_text(encoding="utf-8")
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    y = height - 40
    annotations = []
    line_h = 14
    for line in text.splitlines():
        # If line looks like `Key: Value`, record annotation for Key
        c.drawString(40, y, line)
        parts = line.split(":", 1)
        if len(parts) == 2:
            key = parts[0].strip().lower().replace(" ", "_")
            # record bbox approx where text was drawn
            annotations.append({
                "field": key,
                "bbox": [40, y - line_h, 520, y],
            })
        y -= line_h
        if y < 40:
            c.showPage()
            y = height - 40
    c.save()
    meta = {"source": str(txt_path.name), "annotations": annotations}
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    samples = Path(__file__).parents[1] / "data" / "samples"
    samples.mkdir(parents=True, exist_ok=True)
    for txt in samples.glob("*.txt"):
        pdf = txt.with_suffix(".pdf")
        meta = txt.with_suffix(".meta.json")
        txt_to_pdf_with_annotations(txt, pdf, meta)
        print("Wrote", pdf, "and", meta)
