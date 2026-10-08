"""Loads your Week 2 fine-tuned Legal-RoBERTa and classifies clauses."""
from functools import lru_cache
from config import MODEL_DIR, CONFIDENCE_THRESHOLD


@lru_cache(maxsize=1)
def _load():
    if not MODEL_DIR.exists():
        return None
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR).eval()
    return tok, model, torch


def classify(texts, batch_size=16):
    """Returns [{label, confidence, low_confidence}] for each text."""
    loaded = _load()
    if loaded is None:                      # model folder not downloaded yet
        return [{"label": "Unclassified", "confidence": 0.0, "low_confidence": True} for _ in texts]
    tok, model, torch = loaded
    out = []
    for i in range(0, len(texts), batch_size):
        enc = tok(texts[i:i + batch_size], truncation=True, padding=True,
                  max_length=256, return_tensors="pt")
        with torch.no_grad():
            probs = torch.softmax(model(**enc).logits, dim=-1)
        conf, idx = probs.max(dim=-1)
        for c, k in zip(conf.tolist(), idx.tolist()):
            out.append({"label": model.config.id2label[k], "confidence": c,
                        "low_confidence": c < CONFIDENCE_THRESHOLD})
    return out
