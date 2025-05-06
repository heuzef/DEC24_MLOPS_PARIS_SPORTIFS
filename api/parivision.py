# Imports librairies et secrets
import os
import json
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
import mlflow
from mlflow import MlflowClient
from mlflow.server import get_app_client
from mlflow.exceptions import MlflowException
from fastapi import FastAPI, HTTPException, Depends, status
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from starlette.responses import Response

# Registry for metrics
collector = CollectorRegistry()
# Create an object Summary to save the inference time
inference_time_summary = Summary('inference_time_seconds', 'Time spent on inference', registry=collector)

# Pydantic model to validate input data
class InputModel(BaseModel):
    Player_ID: int
    X_Location: int
    Y_Location: int
    Total_Seconds_Remaining: int
    Shot_Type_Encoded: int
    Shot_Distance_Meters: float
    Shot_Zone_Combined: int

# Init FastAPI
api = FastAPI()
champion = None

@api.on_event("startup")
async def startup_event():
    global champion
    if champion is None:
        # Load the champion versioned model from MLFlow
        load_dotenv(".env")
        username = os.getenv('MLFLOW_TRACKING_USERNAME')
        password = os.getenv('MLFLOW_TRACKING_PASSWORD')
        mlflow_uri = f"http://{username}:{password}@parivision.heuzef.com:5000"
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment("parivision")
        champion = mlflow.pyfunc.load_model(f"models:/parivision@champion")

# @api.get(input=JSON(), output=JSON(), route='/login')
# async def login(credentials: dict) -> dict:
#     username = credentials.get("username")
#     password = credentials.get("password")

#     if username in USERS and USERS[username] == password:
#         return {"message": f"Hello, {username}!"}
#     else:
#         return JSONResponse(status_code=401)

@api.get("/")
async def root():
    return {"status": "alive"}

@api.get("/get_champion_infos")
def get_champion_infos():
    def filter_serializable(obj):
        if isinstance(obj, (dict, list)):
            if isinstance(obj, dict):
                return {k: filter_serializable(v) for k, v in obj.items() if not callable(v)}
            else:
                return [filter_serializable(item) for item in obj if not callable(item)]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    return {"champion": filter_serializable(champion.metadata)}

@api.post('/predict')
async def predict(input_data: InputModel):
    """
    Endpoint for secure prediction based on scoring parameters.

    Args:
        item (InputModel): Input parameters for prediction.

    Returns:
        dict: Prediction result, can be 1 or 0 indicating shot made or missed.
    """
    # Create a DataFrame with the data of the request object
    df = pd.DataFrame([input_data.model_dump()])

    # Make the prediction and save the inference time
    with inference_time_summary.time():
        prediction = champion.predict(df)

    # Return the prediction as an answer
    return {"prediction": int(prediction.item())}

@api.get("/metrics")
async def metrics():
    return Response(generate_latest(collector), media_type=CONTENT_TYPE_LATEST)