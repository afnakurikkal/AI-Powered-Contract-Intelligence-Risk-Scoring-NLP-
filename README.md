# AI-Powered-Contract-Intelligence-Risk-Scoring-NLP-

A sophisticated NLP platform designed for legal and compliance teams. This system ingests lengthy legal contracts (PDFs/word docs), automatically extracts key entities (dates, parties, jurisdiction),identifies specific clauses (e.g., termination ,confidentiality), and flags anomalous or high-risk language using a fine tuned Large Language Model(LLM) and Named Entity Recognition(NER).





\## Week 2 Progress

\- Data split into train/val/test (80/10/10, split by contract)

\- Added "Other" class, fixed label cleaning issues, computed class weights

\- Fine-tuned legal-roberta-base for 4 epochs — F1 Macro ≈ 0.70 on validation set

\- Next: evaluate on held-out test set

