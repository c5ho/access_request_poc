from access_request_poc.extractor import extract_access_request
from pathlib import Path


def test_extract_from_sample_text():
    p = Path(__file__).parents[1] / "data" / "samples" / "sample_request_1.txt"
    text = p.read_text()
    data = extract_access_request(text)
    assert data.get("employee_id") == "E-2001"
    assert data.get("department") == "Finance"
    assert data.get("requested_role") == "Finance Analyst"
    assert data.get("manager_approved") is True
