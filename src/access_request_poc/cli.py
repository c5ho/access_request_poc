import argparse
import json
from .pipeline import process_file, process_text_request


def main():
    p = argparse.ArgumentParser(description="Access Request POC CLI")
    p.add_argument("source", help="Path to a text or PDF file (text supported)")
    args = p.parse_args()

    if args.source.lower().endswith(".txt"):
        result = process_file(args.source)
    else:
        # For PDFs we'd call OCR; for now try to read as text
        try:
            result = process_file(args.source)
        except Exception as e:
            print("Failed to process file:", e)
            return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
