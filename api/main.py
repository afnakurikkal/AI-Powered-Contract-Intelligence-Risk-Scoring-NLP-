from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import sys

app = FastAPI()

# Make src/ importable
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from ocr import extract_text_from_pdf

# ... (keep your existing model-loading code above this) ...

UPLOAD_DIR = "data/raw/contracts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_path)

    return {
        "filename": file.filename,
        "characters_extracted": len(text),
        "preview": text[:500]
    }