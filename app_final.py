from fastapi import FastAPI

app = FastAPI(title="Equipment Helpdesk")


@app.get("/health")
def health():
    return {"status": "ok"}
