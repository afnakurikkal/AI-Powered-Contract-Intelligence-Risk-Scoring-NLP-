import json
import spacy
from pathlib import Path

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Input and output paths
INPUT_FILE = Path("data/processed/sample_contract_clauses.json")
OUTPUT_FILE = Path("data/processed/sample_contract_entities.json")


def extract_entities():
    # Read clause JSON
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        clauses = json.load(f)

    results = []

    for clause in clauses:
        text = clause["clause_text"]
        doc = nlp(text)

        entities = []

        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_
            })

        results.append({
            "clause_id": clause["clause_id"],
            "clause_text": text,
            "entities": entities
        })

    # Save entity-annotated clauses
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"NER completed.")
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    extract_entities()