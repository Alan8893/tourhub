from fastapi import FastAPI

app = FastAPI(title="TourHub")

@app.get("/health")
def health():
    return {"status": "ok"}