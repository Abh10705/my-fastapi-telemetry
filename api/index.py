from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import json
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.get("/")
def read_root():
    return {"message": "eShopCo Latency Analytics API"}

@app.post("/api/latency")
def analyze_latency(request: LatencyRequest):
    # Real telemetry data from eShopCo
    telemetry_data = [
        {"region": "apac", "service": "analytics", "latency_ms": 115.34, "uptime_pct": 99.405},
        {"region": "apac", "service": "checkout", "latency_ms": 134.67, "uptime_pct": 98.733},
        {"region": "apac", "service": "catalog", "latency_ms": 108.61, "uptime_pct": 98.332},
        {"region": "apac", "service": "payments", "latency_ms": 202.13, "uptime_pct": 98.371},
        {"region": "apac", "service": "payments", "latency_ms": 114.43, "uptime_pct": 97.767},
        {"region": "apac", "service": "recommendations", "latency_ms": 116.86, "uptime_pct": 98.591},
        {"region": "apac", "service": "recommendations", "latency_ms": 184.42, "uptime_pct": 98.927},
        {"region": "apac", "service": "recommendations", "latency_ms": 124.05, "uptime_pct": 97.826},
        {"region": "apac", "service": "recommendations", "latency_ms": 170.74, "uptime_pct": 98.778},
        {"region": "apac", "service": "recommendations", "latency_ms": 152.91, "uptime_pct": 97.282},
        {"region": "apac", "service": "payments", "latency_ms": 211.55, "uptime_pct": 98.137},
        {"region": "apac", "service": "analytics", "latency_ms": 170.73, "uptime_pct": 97.35},
        {"region": "emea", "service": "checkout", "latency_ms": 187.82, "uptime_pct": 99.451},
        {"region": "emea", "service": "catalog", "latency_ms": 188.63, "uptime_pct": 97.706},
        {"region": "emea", "service": "recommendations", "latency_ms": 195.15, "uptime_pct": 98.706},
        {"region": "emea", "service": "recommendations", "latency_ms": 185.52, "uptime_pct": 97.675},
        {"region": "emea", "service": "support", "latency_ms": 140.54, "uptime_pct": 98.15},
        {"region": "emea", "service": "support", "latency_ms": 231.38, "uptime_pct": 99.345},
        {"region": "emea", "service": "checkout", "latency_ms": 115.95, "uptime_pct": 98.679},
        {"region": "emea", "service": "payments", "latency_ms": 127.04, "uptime_pct": 97.617},
        {"region": "emea", "service": "payments", "latency_ms": 190.33, "uptime_pct": 98.852},
        {"region": "emea", "service": "checkout", "latency_ms": 130.63, "uptime_pct": 97.219},
        {"region": "emea", "service": "catalog", "latency_ms": 164.19, "uptime_pct": 98.176},
        {"region": "emea", "service": "recommendations", "latency_ms": 204.93, "uptime_pct": 97.304},
        {"region": "amer", "service": "checkout", "latency_ms": 154.84, "uptime_pct": 99.348},
        {"region": "amer", "service": "support", "latency_ms": 181.45, "uptime_pct": 98.553},
        {"region": "amer", "service": "recommendations", "latency_ms": 127.5, "uptime_pct": 98.257},
        {"region": "amer", "service": "catalog", "latency_ms": 146.61, "uptime_pct": 98.779},
        {"region": "amer", "service": "support", "latency_ms": 124.19, "uptime_pct": 98.552},
        {"region": "amer", "service": "analytics", "latency_ms": 219.99, "uptime_pct": 97.52},
        {"region": "amer", "service": "support", "latency_ms": 236.89, "uptime_pct": 98.589},
        {"region": "amer", "service": "recommendations", "latency_ms": 133.0, "uptime_pct": 97.447},
        {"region": "amer", "service": "payments", "latency_ms": 217.97, "uptime_pct": 97.536},
        {"region": "amer", "service": "support", "latency_ms": 133.0, "uptime_pct": 99.41},
        {"region": "amer", "service": "analytics", "latency_ms": 210.25, "uptime_pct": 98.287},
        {"region": "amer", "service": "payments", "latency_ms": 215.46, "uptime_pct": 99.358}
    ]
    
    results = {}
    
    for region in request.regions:
        # Filter data for this region
        region_data = [d for d in telemetry_data if d["region"] == region]
        
        if not region_data:
            results[region] = {
                "error": f"Region {region} not found"
            }
            continue
            
        latencies = np.array([d["latency_ms"] for d in region_data])
        uptimes = np.array([d["uptime_pct"] / 100.0 for d in region_data])  # Convert percentage to decimal
        
        # Calculate metrics
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(np.sum(latencies > request.threshold_ms))
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": breaches
        }
    
    return results
