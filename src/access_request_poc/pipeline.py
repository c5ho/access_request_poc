from typing import Dict, Any
import sys
from .extractor import extract_access_request
from . import ocr
from .validator import validate_request
from .summary import build_decision_summary
from .scoring import score_confidence


def _needs_review_stub(reason: str) -> Dict[str, Any]:
    return {
        "request": {},
        "decision": {"status": "NEEDS_REVIEW", "reason": reason},
        "confidence": 0.0,
        "needs_human_review": True,
        "summary": {},
    }


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
    try:
        lp = path.lower()
        if lp.endswith(".pdf"):
            text = ocr.ocr_pdf(path)
            if not text:
                # OCR not available or failed; mark for human review
                return _needs_review_stub("ocr_unavailable")
            return process_text_request(text)

        # Support plain text files
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return process_text_request(text)
    except Exception as e:
        # Corrupt file, unexpected extraction error, etc. — never crash the caller.
        print(f"process_file failed for {path}: {e}", file=sys.stderr)
        return _needs_review_stub("processing_error")
