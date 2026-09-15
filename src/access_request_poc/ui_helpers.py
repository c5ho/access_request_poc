from pathlib import Path
from typing import Dict, Any, Optional
try:
    from pdf2image import convert_from_path
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover - optional
    convert_from_path = None
    Image = None
    ImageDraw = None


def render_highlighted_image(pdf_path: str, annotations: Dict[str, Any]) -> Optional["Image.Image"]:
    """Render the first page of PDF as image and draw annotation boxes.

    Returns a PIL Image or None if runtime not available.
    """
    if convert_from_path is None or Image is None or ImageDraw is None:
        return None

    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    if not pages:
        return None
    img = pages[0].convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    for ann in annotations:
        bbox = ann.get("bbox")
        if not bbox:
            continue
        x0, y0, x1, y1 = bbox
        # reportlab origin is bottom-left, PIL uses top-left: convert
        w, h = img.size
        # convert y coordinates
        py0 = h - y1
        py1 = h - y0
        draw.rectangle([x0, py0, x1, py1], outline=(255, 0, 0, 200), width=2)
        draw.rectangle([x0, py0, x1, py1], fill=(255, 0, 0, 40))

    return img
