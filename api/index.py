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
    # Sample telemetry data with more realistic values for testing
    sample_data = {
        "apac": {
            "latencies": [165, 178, 190, 145, 167, 189, 201, 156, 184, 172, 195, 158, 176, 183, 191],
            "uptimes": [0.99, 0.98, 1.0, 0.97, 0.99, 0.98, 0.96, 0.99, 1.0, 0.98, 0.97, 0.99, 0.98, 1.0, 0.99]
        },
        "emea": {
            "latencies": [156, 187, 145, 178, 201, 167, 123, 145, 189, 174, 192, 168, 181, 159, 186],
            "uptimes": [0.99, 1.0, 0.98, 0.99, 0.97, 0.99, 0.98, 1.0, 0.99, 0.98, 0.99, 1.0, 0.97, 0.98, 0.99]
        },
        "americas": {
            "latencies": [134, 156, 178, 145, 112, 134, 167, 123, 145, 159, 171, 148, 162, 137, 155],
            "uptimes": [1.0, 0.99, 0.98, 0.99, 1.0, 0.98, 0.97, 0.99, 1.0, 0.98, 0.99, 1.0, 0.98, 0.99, 0.97]
        }
    }
    
    results = {}
    
    for region in request.regions:
        if region not in sample_data:
            results[region] = {
                "error": f"Region {region} not found"
            }
            continue
            
        latencies = np.array(sample_data[region]["latencies"])
        uptimes = np.array(sample_data[region]["uptimes"])
        
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
