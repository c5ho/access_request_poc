import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


REVIEWERS_PATH = Path(__file__).parents[2] / "data" / "reviewers.json"


def _use_secret_manager() -> bool:
    return bool(os.environ.get("REVIEWERS_SECRET_NAME"))


def _load_from_secret() -> List[Dict[str, Any]]:
    try:
        from google.cloud import secretmanager
    except Exception:
        return []

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    secret_name = os.environ.get("REVIEWERS_SECRET_NAME")
    if not project or not secret_name:
        return []

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_name}/versions/latest"
    try:
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return json.loads(payload)
    except Exception:
        return []


def load_reviewers() -> List[Dict[str, Any]]:
    if _use_secret_manager():
        items = _load_from_secret()
        if items:
            return items
    if not REVIEWERS_PATH.exists():
        return []
    return json.loads(REVIEWERS_PATH.read_text(encoding="utf-8"))


def list_reviewer_names() -> List[str]:
    return [r.get("name") for r in load_reviewers()]


def validate_reviewer(name: str, token: str) -> Optional[Dict[str, Any]]:
    for r in load_reviewers():
        if r.get("name") == name and r.get("token") == token:
            return r
    return None
