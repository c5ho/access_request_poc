import re
from typing import Dict, Any


def _first_match(pattern: str, text: str) -> str:
    m = re.search(pattern, text, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_access_request_from_text(text: str) -> Dict[str, Any]:
    """Extract access request fields from raw OCR/text content.

    This is a simple rule-based extractor for the POC. It expects text
    that contains lines like `Employee ID: E-1001`, `Department: Finance`, etc.
    """
    data: Dict[str, Any] = {}

    data["employee_id"] = _first_match(r"employee\s*id[:\-\s]+([A-Za-z0-9\-]+)", text)
    data["first_name"] = _first_match(r"first\s*name[:\-\s]+([A-Za-z\-]+)", text)
    data["last_name"] = _first_match(r"last\s*name[:\-\s]+([A-Za-z\-]+)", text)
    data["department"] = _first_match(r"department[:\-\s]+([A-Za-z &]+)", text)
    data["job_title"] = _first_match(r"job\s*title[:\-\s]+(.+)", text)
    data["requested_role"] = _first_match(r"requested\s*role[:\-\s]+(.+)", text)
    data["manager_approved"] = bool(_first_match(r"manager[_\s]*approved[:\-\s]+(yes|true|1)", text))
    data["start_date"] = _first_match(r"start\s*date[:\-\s]+([0-9T\-\/]+)", text)
    data["end_date"] = _first_match(r"end\s*date[:\-\s]+([0-9T\-\/]+)", text)
    data["reason"] = _first_match(r"reason[:\-\s]+(.+)", text)

    # Normalize empty strings to None
    for k, v in list(data.items()):
        if isinstance(v, str) and not v:
            data[k] = None

    return data


def extract_access_request(source: Any) -> Dict[str, Any]:
    """Main extraction entrypoint.

    If `source` is a string, treat it as raw text. In future this can accept
    file paths or binary PDFs and run OCR before calling the text extractor.
    """
    if isinstance(source, str):
        return extract_access_request_from_text(source)

    # For other types, return empty dict for now
    return {}
