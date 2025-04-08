import pandas as pd
import bentoml
from bentoml.io import NumpyNdarray, JSON
from fastapi import FastAPI, HTTPException, Depends, status
import mlflow
from mlflow import MlflowClient
from mlflow.server import get_app_client
from mlflow.exceptions import MlflowException
import pymongo

# MLFlow Config :
mlflow_uri = "http://*********:*********@parivision.heuzef.com:5000"
mlflow.set_tracking_uri(mlflow_uri)
mlflow.set_experiment("test")

# https://docs.bentoml.com/en/1.1/integrations/mlflow.html

# Import du model Champion depuis MLFlow dans le store de BentoML
bento_model = bentoml.mlflow.import_model(
    name="champion",
    model_uri="models:/test@champion"
)

# Chargement du modele champion depuis le store BentoML
runner = bentoml.mlflow.get("champion:latest").to_runner() # Converti le modele en runner exploitable

# SERVICE API (BentoML / FastAPI)
champion_service = bentoml.Service("champion_service", runners=[runner])

# Login endpoint
# @champion_service.api(input=JSON(), output=JSON(), route='/login')
# async def login(credentials: dict) -> dict:
#     username = credentials.get("username")
#     password = credentials.get("password")

#     if username in USERS and USERS[username] == password:
#         return {"message": f"Hello, {username}!"}
#     else:
#         return JSONResponse(status_code=401)

# Prediction endpoint
# @champion_service.api(
#     input=JSON(pydantic_model=InputModel),
#     output=JSON(),
#     route='/predict'
# )
# async def predict(input_data: InputModel, ctx: bentoml.Context) -> dict:
#     request = ctx.request

#     # Convert the input data to a numpy array
#     input_series = np.array([
#         input_data.data1, 
#         input_data.data2, 
#         input_data.data3,
#         input_data.data4,
#         input_data.data5
#         ])

#     prediction = await champion.predict.async_run(input_series.reshape(1, -1))

#     return {
#         "PREDICTION : ": float(prediction[0])
#         }

# Get_params endpoint
# Requete sur MongoDB (PyMongo) pour récupérer la liste des params.
# 4 Inputs pour les listes de séléction.