import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


REVIEWS_PATH = Path(__file__).parents[2] / "data" / "reviews.json"


def _use_gcs() -> bool:
    return bool(os.environ.get("GCS_BUCKET"))


def _ensure_store():
    if _use_gcs():
        return
    REVIEWS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not REVIEWS_PATH.exists():
        REVIEWS_PATH.write_text("[]", encoding="utf-8")


def _read_local() -> List[Dict[str, Any]]:
    _ensure_store()
    return json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))


def _write_local(arr: List[Dict[str, Any]]) -> None:
    REVIEWS_PATH.write_text(json.dumps(arr, indent=2), encoding="utf-8")


def _read_gcs() -> List[Dict[str, Any]]:
    try:
        from google.cloud import storage
    except Exception:
        # GCS client not available; fallback to local
        return _read_local()

    bucket_name = os.environ["GCS_BUCKET"]
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob("reviews.json")
    if not blob.exists():
        return []
    return json.loads(blob.download_as_text())


def _write_gcs(arr: List[Dict[str, Any]]) -> None:
    try:
        from google.cloud import storage
    except Exception:
        return _write_local(arr)

    bucket_name = os.environ["GCS_BUCKET"]
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob("reviews.json")
    blob.upload_from_string(json.dumps(arr), content_type="application/json")


def save_review(review: Dict[str, Any]) -> None:
    review_record = {"timestamp": datetime.utcnow().isoformat() + "Z", **review}
    if _use_gcs():
        arr = _read_gcs()
        arr.append(review_record)
        _write_gcs(arr)
        return

    arr = _read_local()
    arr.append(review_record)
    _write_local(arr)


def list_reviews() -> List[Dict[str, Any]]:
    if _use_gcs():
        return _read_gcs()
    return _read_local()
