from pathlib import Path
import json

from .pipeline import process_file


def main():
    samples = Path(__file__).parents[2] / "data" / "samples"
    results = {}
    for f in sorted(samples.glob("*.txt")):
        results[f.name] = process_file(str(f))

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
