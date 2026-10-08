"""FastAPI app. Run from the project root:  uvicorn api.main:app --reload"""
import json
import shutil
import sys
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from config import UPLOAD_DIR, RESULTS_DIR, UPLOAD_NAMESPACE, CUAD_NAMESPACE  # noqa: E402

app = FastAPI(title="Contract Intelligence API")
JOBS = {}   # job_id -> {"status": ..., "filename": ..., "error": ...}  (in memory)


def run_job(job_id, pdf_path):
    """Runs in the background so /upload returns immediately."""
    try:
        from pipeline import process_contract      # heavy imports happen here, not at startup
        JOBS[job_id]["status"] = "processing"
        process_contract(pdf_path, job_id)
        JOBS[job_id]["status"] = "done"
    except Exception as exc:
        JOBS[job_id].update(status="failed", error=str(exc))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload", status_code=202)
async def upload_contract(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")
    job_id = uuid.uuid4().hex[:12]
    pdf_path = UPLOAD_DIR / f"{job_id}.pdf"          # our own name: no unsafe filenames, no overwrites
    with open(pdf_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    JOBS[job_id] = {"status": "queued", "filename": file.filename}
    background_tasks.add_task(run_job, job_id, pdf_path)
    return {"job_id": job_id, "status": "queued"}


@app.get("/status/{job_id}")
def status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(404, "Unknown job_id")
    return {"job_id": job_id, **JOBS[job_id]}


@app.get("/contracts/{job_id}")
def get_metadata(job_id: str):
    path = RESULTS_DIR / f"{job_id}.json"
    if not path.exists():
        state = JOBS.get(job_id, {}).get("status", "unknown")
        raise HTTPException(404, f"Result not ready (status: {state})")
    return json.loads(path.read_text(encoding="utf-8"))


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source: str = "uploads"        # "uploads" = your PDFs, "cuad" = the CUAD dataset
    label: str | None = None
    contract: str | None = None


@app.post("/search")
def search_clauses(req: SearchRequest):
    from vector_store import search
    ns = UPLOAD_NAMESPACE if req.source == "uploads" else CUAD_NAMESPACE
    return {"query": req.query,
            "results": search(req.query, req.top_k, ns, req.label, req.contract)}
