from fastapi import FastAPI

VERSION = "0.1.0"
app = FastAPI(title="Equipment Helpdesk", version=VERSION)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": VERSION}
