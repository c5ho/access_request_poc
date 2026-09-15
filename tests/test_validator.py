from access_request_poc.validator import validate_request


def test_standard_role_is_approved():
    request = {
        "employee_id": "E-1001",
        "department": "Finance",
        "job_title": "Senior Analyst",
        "requested_role": "Finance Analyst",
        "manager_approved": True,
        "start_date": "2026-10-01",
        "end_date": "2026-12-31",
        "reason": "Quarterly reporting support",
    }

    decision = validate_request(request)
    assert decision["status"] == "APPROVE"


def test_unapproved_role_requires_review():
    request = {
        "employee_id": "E-1002",
        "department": "IT",
        "job_title": "Support Engineer",
        "requested_role": "Finance Manager",
        "manager_approved": False,
        "start_date": "2026-10-01",
        "end_date": "2026-12-31",
        "reason": "Needs access for reporting",
    }

    decision = validate_request(request)
    assert decision["status"] in {"REJECT", "NEEDS_REVIEW"}


def test_temp_access_without_manager_approval_requires_review():
    request = {
        "employee_id": "E-1003",
        "department": "Operations",
        "job_title": "Operations Analyst",
        "requested_role": "Operations Viewer",
        "manager_approved": False,
        "start_date": "2026-10-01",
        "end_date": "2026-11-15",
        "reason": "Project support",
    }

    decision = validate_request(request)
    assert decision["status"] == "NEEDS_REVIEW"
