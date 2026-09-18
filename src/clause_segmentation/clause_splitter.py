from pathlib import Path
import re
import json


INPUT_FILE = Path("data/processed/sample_contract_ocr.txt")
TEXT_OUTPUT_FILE = Path("data/processed/sample_contract_clauses.txt")
JSON_OUTPUT_FILE = Path("data/processed/sample_contract_clauses.json")


def split_into_clauses(text):
    """
    Split contract text into numbered clause-like sections.
    """

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    sections = re.split(
        r"\n(?=\d+(?:\.\d+)*[\.\)]?\s+)",
        text
    )

    clauses = []

    for section in sections:
        section = section.strip()

        if len(section) > 50:
            clauses.append(section)

    return clauses


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    text = INPUT_FILE.read_text(encoding="utf-8")

    clauses = split_into_clauses(text)

    TEXT_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save text format
    with TEXT_OUTPUT_FILE.open("w", encoding="utf-8") as file:

        for index, clause in enumerate(clauses, start=1):

            file.write(f"\n--- Clause {index} ---\n")
            file.write(clause)
            file.write("\n")

    # Create structured JSON data
    structured_clauses = []

    for index, clause in enumerate(clauses, start=1):

        structured_clauses.append({
            "clause_id": index,
            "clause_text": clause
        })

    # Save JSON format
    JSON_OUTPUT_FILE.write_text(
        json.dumps(
            structured_clauses,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("Clause segmentation completed.")
    print(f"Total clauses found: {len(clauses)}")
    print(f"Text output saved to: {TEXT_OUTPUT_FILE}")
    print(f"JSON output saved to: {JSON_OUTPUT_FILE}")


if __name__ == "__main__":
    main()