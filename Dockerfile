
FROM python:3.13-slim

WORKDIR /app

# Install system tools required for PDF OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy application source code
COPY api/ ./api/
COPY src/ ./src/



# Create directories used by the application
RUN mkdir -p data/raw/contracts data/processed/results models/final_model && chmod -R a+rwX /app

ENV HF_HOME=/tmp/hf_cache

EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
