"""Embeddings + Pinecone. Models/clients are loaded ONCE, on first use."""
from functools import lru_cache
from config import PINECONE_API_KEY, PINECONE_INDEX, EMBED_MODEL, UPLOAD_NAMESPACE


@lru_cache(maxsize=1)
def get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBED_MODEL)


@lru_cache(maxsize=1)
def get_index():
    from pinecone import Pinecone
    if not PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY missing. Create a .env file (see .env.example).")
    return Pinecone(api_key=PINECONE_API_KEY).Index(PINECONE_INDEX)


def upsert_clauses(contract_id, clauses, namespace=UPLOAD_NAMESPACE):
    """clauses = list of dicts: clause_id, clause_text, label, confidence."""
    if not clauses:
        return 0
    vectors = get_embedder().encode([c["clause_text"] for c in clauses], batch_size=32)
    items = [{
        "id": f"{contract_id}_{c['clause_id']}",
        "values": vec.tolist(),
        "metadata": {
            "contract": contract_id,
            "clause_text": c["clause_text"][:1000],
            "label": c["label"],
            "confidence": round(float(c["confidence"]), 4),
        },
    } for c, vec in zip(clauses, vectors)]
    index = get_index()
    for i in range(0, len(items), 100):
        index.upsert(vectors=items[i:i + 100], namespace=namespace)
    return len(items)


def search(query, top_k=5, namespace=UPLOAD_NAMESPACE, label=None, contract=None):
    flt = {}
    if label:
        flt["label"] = {"$eq": label}
    if contract:
        flt["contract"] = {"$eq": contract}
    res = get_index().query(
        vector=get_embedder().encode(query).tolist(),
        top_k=top_k, include_metadata=True, namespace=namespace,
        filter=flt or None,
    )
    return [{"score": round(m["score"], 4), **m["metadata"]} for m in res["matches"]]
