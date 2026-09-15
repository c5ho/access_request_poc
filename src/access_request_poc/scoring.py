from typing import Dict, Any


def score_confidence(request: Dict[str, Any]) -> float:
    """Return a simple confidence score (0.0 - 1.0) for extracted fields.

    Heuristic: presence of required fields, manager approval, and dates.
    """
    required = ["employee_id", "department", "requested_role"]
    present = sum(1 for f in required if request.get(f))
    base = present / len(required)

    manager_bonus = 0.25 if request.get("manager_approved") else 0.0
    date_bonus = 0.1 if request.get("start_date") else 0.0

    score = min(1.0, base * 0.65 + manager_bonus + date_bonus)
    return round(score, 3)
