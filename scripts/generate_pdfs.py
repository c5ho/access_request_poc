import io
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Internal resolution used to rasterize degraded pages, in pixels-per-point.
RENDER_DPI = 200

# quality -> (blur_radius, noise_sigma, noise_alpha, contrast, max_rotation_deg, jpeg_quality)
QUALITY_PROFILES = {
    "medium": (0.6, 12, 0.12, 0.9, 1.0, 70),
    "low": (1.8, 28, 0.28, 0.7, 3.0, 30),
}


def _record_annotation(annotations, line, y, line_h):
    parts = line.split(":", 1)
    if len(parts) == 2:
        key = parts[0].strip().lower().replace(" ", "_")
        annotations.append({"field": key, "bbox": [40, y - line_h, 520, y]})


def _degrade_image(img: Image.Image, quality: str) -> Image.Image:
    profile = QUALITY_PROFILES.get(quality)
    if not profile:
        return img
    blur_radius, noise_sigma, noise_alpha, contrast, max_angle, jpeg_quality = profile

    noise = Image.effect_noise(img.size, noise_sigma)
    img = Image.blend(img, noise, noise_alpha)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    img = img.rotate(random.uniform(-max_angle, max_angle), fillcolor=255, resample=Image.BICUBIC)

    # Re-encode through JPEG to add compression artifacts, like a real scanner/fax would.
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=jpeg_quality)
    buf.seek(0)
    return Image.open(buf)


def _render_page_image(lines, width_pt, height_pt, line_h, quality) -> Image.Image:
    scale = RENDER_DPI / 72.0
    img = Image.new("L", (int(width_pt * scale), int(height_pt * scale)), color=255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=int(12 * scale))

    y = height_pt - 40
    for line in lines:
        x_px = int(40 * scale)
        y_px = int((height_pt - y) * scale) - int(10 * scale)
        draw.text((x_px, y_px), line, fill=0, font=font)
        y -= line_h
        if y < 40:
            y = height_pt - 40

    return _degrade_image(img, quality).convert("RGB")


def txt_to_pdf_with_annotations(txt_path: Path, pdf_path: Path, meta_path: Path, quality: str = "high"):
    """Render a text sample to PDF.

    `quality` simulates scan fidelity for OCR/IDP testing:
      - "high": crisp vector text (perfect OCR conditions)
      - "medium"/"low": rasterized with noise, blur, skew, and JPEG artifacts
    """
    text = txt_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    width, height = letter
    line_h = 14
    annotations = []

    c = canvas.Canvas(str(pdf_path), pagesize=letter)

    if quality == "high":
        y = height - 40
        for line in lines:
            c.drawString(40, y, line)
            _record_annotation(annotations, line, y, line_h)
            y -= line_h
            if y < 40:
                c.showPage()
                y = height - 40
    else:
        img = _render_page_image(lines, width, height, line_h, quality)
        c.drawImage(ImageReader(img), 0, 0, width=width, height=height)
        y = height - 40
        for line in lines:
            _record_annotation(annotations, line, y, line_h)
            y -= line_h
            if y < 40:
                y = height - 40

    c.save()
    meta = {"source": txt_path.name, "quality": quality, "annotations": annotations}
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    samples = Path(__file__).parents[1] / "data" / "samples"
    samples.mkdir(parents=True, exist_ok=True)
    for txt in samples.glob("*.txt"):
        for quality in ("high", "medium", "low"):
            suffix = "" if quality == "high" else f"_{quality}"
            pdf = txt.with_name(f"{txt.stem}{suffix}.pdf")
            meta = txt.with_name(f"{txt.stem}{suffix}.meta.json")
            txt_to_pdf_with_annotations(txt, pdf, meta, quality=quality)
            print("Wrote", pdf, "and", meta, f"[{quality}]")
