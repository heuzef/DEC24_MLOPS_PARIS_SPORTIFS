# Imports librairies et secrets
import mlflow
from mlflow import MlflowClient
from mlflow.server import get_app_client
from mlflow.exceptions import MlflowException
import requests
import setuptools
import os
from dotenv import load_dotenv
load_dotenv(".env")
username = os.getenv('MLFLOW_TRACKING_USERNAME')
password = os.getenv('MLFLOW_TRACKING_PASSWORD')
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
import numpy as np

def register_model_champion(mlflow_uri, model_name):
    """
    Vérifie la meilleur Run présente, la compare avec le tenant au titre.
    Si la meilleur Run est un challenger, définir le nouveau champion puis
    crée une nouvelle version du model sur MlFlow et lui decerne l'alias "champion".
    """

    # Configuration du client
    mlflow_client = MlflowClient(tracking_uri=mlflow_uri)

    # Récupérer la dernière version du modèle
    model_latest = mlflow_client.search_model_versions(f"name='{model_name}'")[0].version

    # Récupérer les runs MLFlow dans un dataframe
    runs = mlflow.search_runs(experiment_names=[model_name], order_by=["start_time ASC"])
    runs = runs[runs['status'] == 'FINISHED'] # Supprimer les runs échoués

    # Récupérer l'ID de la Run tenant au titre de champion
    run_tenant = mlflow.pyfunc.load_model(f"models:/"+model_name+"@champion").metadata

    # Récupérer l'ID de la run du champion actuel, filtré sur la variable training_score maximal
    run_champion = runs.loc[runs['metrics.training_score'].idxmax()]

    # Créer une nouvelle version du modèle s'il y a un nouveau champion
    if run_champion.run_id == run_tenant.run_id :
        print("Pas de nouveau champion.")
    else:
        print("NOUVEAU CHAMPION !")
        print(run_champion['tags.mlflow.runName'])
        print("---------------------------------")
        print("Création d'une nouvelle version")
        model_uri = f"runs:/"+run_champion.run_id+"/model"
        mlflow.register_model(model_uri=model_uri, name=model_name)
        model_latest = str(int(model_latest)+1)
        print("---------------------------------")
        mlflow_client.set_registered_model_alias(model_name, "champion", version=model_latest)

# Fonction principale
if __name__ == "__main__":
    # Config
    mlflow_uri = "http://parivision.heuzef.com:5000"
    client = get_app_client("basic-auth", tracking_uri=mlflow_uri)
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("parivision")
    # Appel de la fonction
    register_model_champion(mlflow_uri=mlflow_uri, model_name="parivision")