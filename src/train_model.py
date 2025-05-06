# Import des bibliothèques
import pandas as pd
import numpy as np
import pymongo
from bson import json_util
import mlflow
from mlflow.server import get_app_client
import setuptools
import json
import requests
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
#from xgboost import XGBClassifier
#from lightgbm import LGBMClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                            confusion_matrix, classification_report, roc_curve, auc)
import os
import mlflow
import mlflow.sklearn

from dotenv import load_dotenv
load_dotenv(".env")

def connect_to_mongo(mongo_uri):
    """
    Établit une connexion à la base MongoDB et retourne l'objet client.

    :param mongo_uri: URL de connexion MongoDB (ex: 'mongodb://localhost:27017/')
    :return: Tuple (bool, client) -> (True, client) si connexion réussie, (False, None) sinon
    """
    try:
        client = pymongo.MongoClient(mongo_uri)
        # Test rapide pour voir si la connexion fonctionne
        client.admin.command('ping')
        print("Connexion à MongoDB réussie.")
        return True, client
    except pymongo.errors.ConnectionFailure as e:
        print(f"Échec de connexion à MongoDB : {e}")
        return False, None

def ensure_collection_exists(db, collection_name):
    """
    Vérifie si une collection existe dans la base MongoDB, sinon la crée.

    :param db: Objet de la base de données MongoDB
    :param collection_name: Nom de la collection à vérifier/créer
    :return: True si la collection existe ou a été créée, False en cas d'erreur
    """
    try:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Collection '{collection_name}' créée.")
        else:
            print(f"Collection '{collection_name}' existe déjà.")
        return True
    except pymongo.errors.PyMongoError as e:
        print(f" Erreur lors de la vérification/création de la collection : {e}")
        return False

def get_processed_data_from_mongo(mongo_uri, db_name, collection_name):
    """
    Récupère des données JSON processées depuis une collection MongoDB.

    :param mongo_uri: URL de connexion MongoDB (ex: 'mongodb://localhost:27017/')
    :param db_name: Nom de la base de données MongoDB
    :param collection_name: Nom de la collection MongoDB
    :return: dataframe_raw
    """

    success, client = connect_to_mongo(mongo_uri)
    if not success:
        return False, "Impossible de se connecter à MongoDB"

    try:
        db = client[db_name]

        # Vérification et création de la collection si nécessaire
        if not ensure_collection_exists(db, collection_name):
            return False
        
        # Connexion à MongoDB
        client = pymongo.MongoClient(mongo_uri)

        # Sélection base + collection
        db = client[database_name]
        collection = db[collection_name]

        # Récupération brute des documents (documents JSON)
        documents = list(collection.find())

        # Convertir les documents BSON/JSON en un format lisible par pandas
        # (le json_util permet de gérer les ObjectId, dates, etc.)
        json_data = json.loads(json_util.dumps(documents))

        # Convertir en DataFrame
        df_proccessed = pd.json_normalize(json_data)
        
        return df_proccessed

    except pymongo.errors.PyMongoError as e:
        print(f"Erreur MongoDB : {e}")
        return False

    finally:
        client.close()


def connection_mlflow():
    # Config MLFlow
    username = os.getenv('MLFLOW_TRACKING_USERNAME')
    password = os.getenv('MLFLOW_TRACKING_PASSWORD')

    try:
        # Connexion au serveur MLflow
        mlflow_uri = "http://parivision.heuzef.com:5000"
        client_mlflow = get_app_client("basic-auth", tracking_uri=mlflow_uri)

        # Vérification de l'utilisateur
        user = client_mlflow.get_user(username)
        print(f"Utilisateur : {user.username}")
        print(f"Est admin : {user.is_admin}")

        # Définir l'URI de tracking + l'expérience
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment("parivision")  # Le nom de l'expérience

        # Test de disponibilité du serveur
        response = requests.get(f"{mlflow_uri}/", auth=(username, password))

        if response.status_code == 200:
            print("Le serveur MLflow est disponible !")
            print("Message :", response.text)
            return True
        else:
            print(f"Échec de la connexion. Code : {response.status_code}")
            print("Message :", response.text)
            return False

    except requests.exceptions.RequestException as req_err:
        print("Erreur de connexion HTTP :", req_err)
        return False

    except Exception as e:
        print("Une erreur s'est produite :", e)
        return False


def train_models(df):

    # 1. conneciton mlflow
    print(f"Dimensions du dataset: {df.shape}")
    print(f"Colonnes: {df.columns.tolist()}")

    # 2. Préparation des données
    # Renommer les colonnes
    df.rename(columns={
        'Player ID': 'Player_ID',
        'X Location': 'X_Location',
        'Y Location': 'Y_Location',
        'Shot Made Flag': 'Shot_Made_Flag'
    }, inplace=True)

    X = df[['Player_ID', 'X_Location', 'Y_Location', 'Total_Seconds_Remaining',
           'Shot_Type_Encoded', 'Shot_Distance_Meters', 'Shot_Zone_Combined']]
    y = df['Shot_Made_Flag']

    # Division en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                      random_state=42, stratify=y)

    print(f"Ensemble d'entraînement: {X_train.shape}")
    print(f"Ensemble de test: {X_test.shape}")

    # Paramètres choisis manuellement
    rf_model = RandomForestClassifier(
        n_estimators=np.random.randint(50, 100),
        max_depth=np.random.randint(1, 10),
        min_samples_split=np.random.randint(3, 6),
        random_state=42
    )

    # Active le tracking automatique pour les modèles scikit-learn
    mlflow.sklearn.autolog()

    # Démarre un run MLflow
    with mlflow.start_run():

        # Entraînement du modèle
        rf_model.fit(X_train, y_train)

        # Prédictions
        y_pred = rf_model.predict(X_test)
        y_pred_proba = rf_model.predict_proba(X_test)[:, 1]

        # Conversion des labels (au cas où ils sont en string)
        y_test = y_test.astype(int)
        y_pred = y_pred.astype(int)

        # Métriques
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        # ROC AUC
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)

        # Affichage des résultats
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print(f"ROC AUC: {roc_auc:.4f}")


if __name__ == '__main__':
    
    # Config MongoDB
    host = "parivision.heuzef.com"
    port = "27017"
    username = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    database_name = "parivision"
    collection_processed_name = "parivision_processed"
    # URI MongoDB avec login/mot de passe
    mongo_uri = f"mongodb://{username}:{password}@{host}:{port}"

    # Récupération des données proccessées
    df_proccessed = get_processed_data_from_mongo(mongo_uri, database_name, collection_processed_name)

    #Connection à MLFlow
    success_mlflow_connection = connection_mlflow()

    if success_mlflow_connection:
        train_models(df_proccessed)
    else:
        print("L'opération a échoué !")