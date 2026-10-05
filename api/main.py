from fastapi import FastAPI
from transformers import AutoTokenizer , AutoModelForSequenceClassification
import torch


app = FastAPI(title="Contract Intelligence API")

#Loaded once , when the server starts
MODEL_PATH = "models/clause_classifier"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval() #inference mode , nt training mode 

device = torch.device("cuda" if torch.cuda.is_available( else) "cpu")
model.to(device)

print("Model loaded. using device:", device)

@app.get("/")
def health_check():
    return {"status":"running"}