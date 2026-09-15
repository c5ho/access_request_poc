import json
from pathlib import Path


def export_jsonl(src: Path, dst: Path):
    arr = json.loads(src.read_text(encoding="utf-8"))
    lines = [json.dumps(x) for x in arr]
    dst.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    base = Path(__file__).parents[1] / "data"
    src = base / "reviews.json"
    dst = base / "exported_reviews.jsonl"
    if not src.exists():
        print("No reviews to export")
    else:
        export_jsonl(src, dst)
        print("Exported to", dst)
