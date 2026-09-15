from access_request_poc.pipeline import process_file, process_text_request
from pathlib import Path


def test_pipeline_on_sample_text():
    p = Path(__file__).parents[1] / "data" / "samples" / "sample_request_1.txt"
    result = process_file(str(p))
    assert result["decision"]["status"] == "APPROVE"
    assert result["confidence"] >= 0.7
    assert result["needs_human_review"] is False


def test_pipeline_process_text_function():
    text = (
        "Employee ID: E-3001\nDepartment: IT\nRequested Role: Finance Manager\nManager Approved: No\n"
    )
    result = process_text_request(text)
    assert result["decision"]["status"] in {"REJECT", "NEEDS_REVIEW"}
    # Since manager not approved and role mismatched, expect review or reject
