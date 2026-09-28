# AI-Powered-Contract-Intelligence-Risk-Scoring-NLP-

A sophisticated NLP platform designed for legal and compliance teams. This system ingests lengthy legal contracts (PDFs/word docs), automatically extracts key entities (dates, parties, jurisdiction),identifies specific clauses (e.g., termination ,confidentiality), and flags anomalous or high-risk language using a fine tuned Large Language Model(LLM) and Named Entity Recognition(NER).
## Project Progress

## Week 1 — Data Preparation & NLP Pipeline ✅

- CUAD dataset preparation
- Train / validation / test split (80/10/10 by contract)
- OCR pipeline
- Text preprocessing
- Clause segmentation
- Structured JSON generation
- Baseline NER

## Week 2 — Legal Clause Classification ✅

- Label cleaning
- Added `Other` class
- Class weights calculated
- Legal-RoBERTa fine-tuning
- 4 epochs of training
- Validation after each epoch
- Final validation Macro F1: **~0.70**
- Fresh model loading and verification
- Untouched test-set evaluation
- Test set: **1,512 samples**
- Precision, Recall and F1 calculated for **42 clause types**
- Incorrect predictions and class confusions inspected
- Evaluation reports and notebook saved

### Current Step — Post-Processing 🔄

- Confidence-score analysis
- Validation-based confidence threshold selection
- Low-confidence prediction identification
- Confidence-based post-processing
- Before/after evaluation comparison

