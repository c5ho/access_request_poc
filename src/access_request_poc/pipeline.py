from typing import Dict, Any
from .extractor import extract_access_request
from . import ocr
from .validator import validate_request
from .summary import build_decision_summary
from .scoring import score_confidence


def process_text_request(text: str) -> Dict[str, Any]:
    request = extract_access_request(text)
    decision = validate_request(request)
    confidence = score_confidence(request)
    needs_human = decision.get("status") == "NEEDS_REVIEW" or confidence < 0.7
    summary = build_decision_summary(request, decision)

    return {
        "request": request,
        "decision": decision,
        "confidence": confidence,
        "needs_human_review": needs_human,
        "summary": summary,
    }


def process_file(path: str) -> Dict[str, Any]:
    lp = path.lower()
    if lp.endswith(".pdf"):
        text = ocr.ocr_pdf(path)
        if not text:
            # OCR not available or failed; mark for human review
            return {
                "request": {},
                "decision": {"status": "NEEDS_REVIEW", "reason": "ocr_unavailable"},
                "confidence": 0.0,
                "needs_human_review": True,
                "summary": {},
            }
        return process_text_request(text)

    # Support plain text files
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return process_text_request(text)
