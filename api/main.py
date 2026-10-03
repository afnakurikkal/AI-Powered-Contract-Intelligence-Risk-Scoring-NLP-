from fastapi import FastAPI

app = FastAPI(title="Contract Intelligence API")

@app.get("/")
def health_check():
    return {"status":"running"}