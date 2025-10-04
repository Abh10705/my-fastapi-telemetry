from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

# Create the main FastAPI application object. This is the core of your API.
app = FastAPI()

# ==============================================================================
#  CORS MIDDLEWARE CONFIGURATION
# ==============================================================================
# This is the crucial part that fixes the "Enable CORS" error.
# A "middleware" is code that processes every single request before it reaches
# your main logic. The CORSMiddleware adds the necessary headers to the response
# to tell browsers that it's safe to allow requests from other websites.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # The '*' means to allow requests from ANY origin/website.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (like GET, POST, etc.).
    allow_headers=["*"],  # Allow all HTTP headers in the request.
)
# ==============================================================================


# --- Data Loading ---
# This section handles loading your data file.
DATA_LOADED_SUCCESSFULLY = False
df = None
try:
    # Vercel runs the script from the root of the project, so the path must be 'api/telemetry.csv'.
    data_file_path = Path("api/telemetry.csv")
    df = pd.read_csv(data_file_path)
    # This flag lets our endpoint know if the data is ready.
    DATA_LOADED_SUCCESSFULLY = True
except FileNotFoundError:
    # If the file isn't found during startup, we set the flag to False.
    # The endpoint will then return a helpful error message.
    DATA_LOADED_SUCCESSFULLY = False


# --- API Endpoint Definition ---
# This "decorator" tells FastAPI that the function below should handle
# any HTTP POST request that comes to the root URL ("/").
@app.post("/")
async def analyze_telemetry(request: Request):
    """
    This is the main logic of your API. It receives the POST request,
    processes the data based on the JSON payload, and returns the results.
    """
    
    # First, check if the data was loaded correctly during startup.
    if not DATA_LOADED_SUCCESSFULLY:
        return {"error": "Server-side error: The 'telemetry.csv' file could not be found on the server."}

    # 1. Get the JSON data from the body of the POST request.
    body = await request.json()
    
    # 2. Extract the 'regions' and 'threshold_ms' values.
    # .get() provides default values if the keys are missing from the JSON.
    regions_to_process = body.get("regions", [])
    latency_threshold = body.get("threshold_ms", 180)
    
    # 3. Prepare an empty dictionary to store our results.
    response_data = {}
    
    # 4. Loop through each region the user requested (e.g., ["apac", "emea"]).
    for region in regions_to_process:
        # Filter the DataFrame to get only the rows for the current region.
        region_df = df[df['region'] == region]
        
        if region_df.empty:
            response_data[region] = {"error": "No data found for this region"}
            continue
            
        # 5. Calculate the required metrics using pandas.
        avg_latency = region_df['latency_ms'].mean()
        p95_latency = region_df['latency_ms'].quantile(0.95)
        avg_uptime = region_df['uptime'].mean()
        
        # Count rows where latency is above the threshold.
        breaches = len(region_df[region_df['latency_ms'] > latency_threshold])
        
        # 6. Store the results for this region, rounding for a clean output.
        response_data[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": int(breaches)
        }
        
    # 7. Return the final dictionary. FastAPI automatically converts it to JSON.
    return response_data

