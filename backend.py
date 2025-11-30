from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(title="Malware Detection System API")

# --- Helper to load mock data ---
def load_mock(filename):
    path = os.path.join("mock_data", filename)
    with open(path, "r") as f:
        return json.load(f)

# --- Data Models (Based on Project Docs) ---
class Alert(BaseModel):
    ip: str
    sha256: str
    threat_score: float
    severity: str

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "System Online", "mode": "Mock Data"}

@app.get("/alerts", response_model=List[Alert])
def get_alerts():
    """Returns the list of correlated alerts for the dashboard."""
    data = load_mock("alerts.json")
    return data

@app.get("/file/{sha256}")
def get_file_details(sha256: str):
    """Fetches ML scores, SHAP values, and file metadata."""
    ml_data = load_mock("ml_scores.json")
    file_data = load_mock("files.json")
    
    if sha256 not in ml_data:
        raise HTTPException(status_code=404, detail="File analysis not found")
    
    return {
        "metadata": file_data.get(sha256, {}),
        "analysis": ml_data.get(sha256, {})
    }

@app.get("/network/{ip}")
def get_network_stats(ip: str):
    """Fetches anomaly scores and features for a specific host."""
    net_data = load_mock("network_anomalies.json")
    
    if ip not in net_data:
        raise HTTPException(status_code=404, detail="Host data not found")
        
    return net_data[ip]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
