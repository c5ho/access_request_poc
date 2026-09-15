from typing import Optional
import os

try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None
    Image = None


def ocr_image(path: str) -> Optional[str]:
    """Run OCR on an image file and return extracted text.

    Requires `pytesseract` and `Pillow` to be installed. Returns None if
    the OCR runtime is not available.
    """
    if pytesseract is None or Image is None:
        return None

    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    return text


def _documentai_extract(path: str) -> Optional[str]:
    """Use Google Document AI to extract text from a PDF file.

    Requires `google-cloud-documentai` and env vars `GOOGLE_CLOUD_PROJECT` and
    `DOCUMENT_AI_PROCESSOR` to be set. Returns None if not configured.
    """
    try:
        from google.cloud import documentai
    except Exception:
        return None

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    processor = os.environ.get("DOCUMENT_AI_PROCESSOR")
    if not project or not processor:
        return None

    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(project, "us", processor)

    with open(path, "rb") as f:
        doc_bytes = f.read()

    raw_doc = documentai.RawDocument(content=doc_bytes, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=name, raw_document=raw_doc)
    result = client.process_document(request=request)
    document = result.document

    # Concatenate text from text_segments
    text = document.text or ""
    return text


def ocr_pdf(path: str) -> Optional[str]:
    """Attempt to extract text from a PDF.

    Preference order:
      1. Document AI (if configured via env vars)
      2. pdf2image + pytesseract (local OCR)
      3. None (OCR unavailable)
    """
    # Try Document AI first if configured
    da = _documentai_extract(path)
    if da:
        return da

    # Fallback to local OCR
    try:
        from pdf2image import convert_from_path
    except Exception:  # pragma: no cover - optional
        return None

    if pytesseract is None or Image is None:
        return None

    pages = convert_from_path(path)
    texts = []
    for p in pages:
        texts.append(pytesseract.image_to_string(p))

    return "\n".join(texts)
