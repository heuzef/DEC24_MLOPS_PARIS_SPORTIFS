# init.py
import streamlit as st
from streamlit_extras.let_it_rain import rain
from streamlit_extras.colored_header import colored_header
from streamlit_extras.mention import mention
from streamlit_image_coordinates import streamlit_image_coordinates
from streamlit_extras.grid import grid
from streamlit_extras.button_selector import button_selector
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.echo_expander import echo_expander
from streamlit_extras.metric_cards import style_metric_cards

import os
import time
import json
import requests
import numpy as np
import pandas as pd
from pandas import json_normalize
import io
import sys

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from collections import Counter

# import mlflow
# from mlflow import MlflowClient
# from mlflow.server import get_app_client
# from mlflow.exceptions import MlflowException

from dotenv import load_dotenv
load_dotenv(".env")

# MONGODB
mongo_client = MongoClient("mongodb://"+os.getenv('MONGO_INITDB_ROOT_USERNAME')+":"+os.getenv('MONGO_INITDB_ROOT_PASSWORD')+"@parivision.heuzef.com:27017")
db = mongo_client["parivision"]
parivision_raw = db["parivision_raw"]
parivision_processed = db["parivision_processed"]

# MLFlow
# mlflow_uri = "http://parivision.heuzef.com:5000"
# mlflow_client = MlflowClient(tracking_uri=mlflow_uri)
# mlflow.set_tracking_uri(mlflow_uri)
# mlflow.set_experiment("parivision")
# champion = mlflow.pyfunc.load_model(f"models:/parivision@champion")

def parivison_predict(inputs):
    """Effectue une requête sur le modèle PariVision pour obtenir une prédiction.

    Cette fonction envoie les données fournies (`inputs`) à l'URL
    spécifiée (`api_url`) via une requête HTTP POST. Elle s'attend à
    recevoir une réponse JSON contenant une clé 'prediction' et retourne
    la valeur associée à cette clé.

    Args:
        inputs (Dict[str, Any]): Un dictionnaire contenant les données
            à envoyer dans le corps de la requête POST. La structure
            doit correspondre à ce qu'attend l'API cible.

    Returns:
        La valeur de la prédiction extraite de la réponse JSON, 
        si la requête réussit et que la clé 'prediction' est présente.

    Example:
        >>> parivison_predict(inputs=inputs)
    """

    # Init API
    api_url = "http://parivision.heuzef.com:3000/predict"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
        }
    
    # Try prediction
    try:
        response = requests.post(api_url, headers=headers, json=inputs) # Effectuer la requête POST
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
        response_data = response.json() # Extraire les données JSON de la réponse        
        prediction_value = response_data.get("prediction") # Utiliser .get() est plus sûr car il retourne None si la clé n'existe pas, évitant une KeyError

    # Raises errors
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")
    except json.JSONDecodeError:
        print("Erreur : La réponse de l'API n'est pas au format JSON valide.")
        print("Contenu de la réponse :", response.text)
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
    return prediction_value

def parivison_get_champion_infos():
    """Effectue une requête sur le modèle PariVision pour obtenir les infos du modèleChampion.

    Returns:
        Les informations du modèle Champion.

    Example:
        >>> parivison_get_champion_infos()
    """

    # Init API
    api_url = "http://parivision.heuzef.com:3000/get_champion_infos"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
        }
    
    # Get infos
    try:
        response = requests.get(api_url, headers=headers) # Effectuer la requête GET
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
        response_data = response.json() # Extraire les données JSON de la réponse        
        infos_value = response_data.get("champion") # Utiliser .get() est plus sûr car il retourne None si la clé n'existe pas, évitant une KeyError

    # Raises errors
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")
    except json.JSONDecodeError:
        print("Erreur : La réponse de l'API n'est pas au format JSON valide.")
        print("Contenu de la réponse :", response.text)
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
    return infos_value

def player_name_to_id(player_name):
    """
    Récupère l'ID à partir du nom du joueur.
    """
    try:
        result_document = parivision_raw.find_one(
            {"Player Name": player_name},  # Filtre: chercher ce nom de joueur
            {"Player ID": 1, "_id": 0}             # Projection: ne retourner que le Player ID
        )

        if result_document:
            # Extraire la valeur du champ "Player ID" du document trouvé
            # Utiliser .get() est plus sûr au cas où le champ serait manquant
            player_id = result_document.get("Player ID")

            if player_id is None:
                print(f"Le joueur '{player_name_to_find}' a été trouvé, mais le champ 'Player ID' est manquant ou vide dans le document.")
                print(f"Document trouvé (partiel) : {result_document}")

        else:
            # Aucun document correspondant n'a été trouvé
            print(f"Aucun joueur trouvé avec le nom '{player_name_to_find}' dans la collection '{collection.name}'.")

    except Exception as e:
        print(f"Une erreur est survenue lors de la recherche du joueur : {e}")

    return player_id