from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

ultimo_scan = {
    "code": None,
    "timestamp": None
}

class Scan(BaseModel):
    code: str

@app.post("/scan")
def recibir_scan(scan: Scan):
    ultimo_scan["code"] = scan.code
    ultimo_scan["timestamp"] = datetime.now().isoformat()
    return {"status": "ok"}

@app.get("/last")
def ultimo_codigo():
    return ultimo_scan

