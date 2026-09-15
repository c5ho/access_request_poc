from datetime import datetime
from typing import Dict, Any

# Simple roles catalog for the POC
ROLE_CATALOG = {
    "Finance Analyst": {"allowed_departments": ["Finance"]},
    "Finance Manager": {"allowed_departments": ["Finance"]},
    "Operations Viewer": {"allowed_departments": ["Operations", "Logistics"]},
}


def validate_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an access request against a simple roles catalog and rules.

    Returns a decision dict with at least a `status` key.
    Possible statuses: APPROVE, REJECT, NEEDS_REVIEW
    """
    role = request.get("requested_role")
    department = request.get("department")
    manager_approved = bool(request.get("manager_approved"))

    # Unknown role -> needs review
    if role not in ROLE_CATALOG:
        return {"status": "NEEDS_REVIEW", "reason": "unknown_role"}

    allowed = ROLE_CATALOG[role]["allowed_departments"]

    # Department not allowed for this role -> reject
    if department not in allowed:
        return {"status": "REJECT", "reason": "department_not_allowed"}

    # If manager approved, allow
    if manager_approved:
        return {"status": "APPROVE", "reason": "manager_approved"}

    # Otherwise, require human review (policy requires manager approval)
    return {"status": "NEEDS_REVIEW", "reason": "manager_required"}
