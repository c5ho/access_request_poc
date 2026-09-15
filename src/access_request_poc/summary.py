from typing import Dict, Any


def build_decision_summary(request: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
    """Create a compact summary combining request fields and decision rationale."""
    summary = {
        "employee_id": request.get("employee_id"),
        "requested_role": request.get("requested_role"),
        "status": decision.get("status"),
        "reason": decision.get("reason"),
    }
    return summary
