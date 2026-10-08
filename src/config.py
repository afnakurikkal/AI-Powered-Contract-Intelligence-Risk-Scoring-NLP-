"""Central settings. Every other file imports paths/keys from here."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent      # project root, works from any folder
load_dotenv(ROOT / ".env")

UPLOAD_DIR = ROOT / "data" / "raw" / "contracts"
RESULTS_DIR = ROOT / "data" / "processed" / "results"
MODEL_DIR = ROOT / "models" / "final_model"        # download from Google Drive (Week 2 model)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "contract-clauses")
EMBED_MODEL = "all-MiniLM-L6-v2"                   # 384 dimensions (same as notebook 07)
CONFIDENCE_THRESHOLD = 0.60                        # from Week 2 post-processing
UPLOAD_NAMESPACE = "uploads"                       # your uploaded contracts live here
CUAD_NAMESPACE = ""                                # the 13,718 CUAD clauses already in Pinecone
