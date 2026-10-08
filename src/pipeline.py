"""Full contract pipeline: PDF -> OCR -> clauses -> NER -> classify -> embed -> Pinecone."""
import json
from functools import lru_cache
from pathlib import Path

from config import RESULTS_DIR
from ocr import extract_text_from_pdf
from clause_segmentation.clause_splitter import split_into_clauses
from classifier import classify
from vector_store import upsert_clauses


@lru_cache(maxsize=1)
def _nlp():
    import spacy
    return spacy.load("en_core_web_sm")


def process_contract(pdf_path, contract_id):
    text = extract_text_from_pdf(pdf_path)
    clauses = split_into_clauses(text)

    preds = classify(clauses)
    nlp = _nlp()
    records = []
    for i, (clause, pred) in enumerate(zip(clauses, preds), start=1):
        ents = [{"text": e.text, "label": e.label_} for e in nlp(clause).ents]
        records.append({"clause_id": i, "clause_text": clause, "entities": ents, **pred})

    stored = upsert_clauses(contract_id, records)

    result = {
        "contract_id": contract_id,
        "characters_extracted": len(text),
        "num_clauses": len(records),
        "vectors_stored": stored,
        "clauses": records,
    }
    (RESULTS_DIR / f"{contract_id}.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result
