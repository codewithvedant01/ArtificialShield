from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ScanRequest(BaseModel):
    text: str

@app.post("/scan")
def scan_text(request: ScanRequest):
    # Yahaan aap apna ML model integration daal sakte hain.
    # Abhi ke liye hum mock logic use kar rahe hain.
    
    if "attack" in request.text.lower():
        return {"status": "BLOCKED", "score": 0.95}
    
    return {"status": "ALLOWED", "score": 0.10}