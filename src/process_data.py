import numpy as np
import pandas as pd
import pymongo
from bson import json_util
import json
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from dotenv import load_dotenv
import os
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

# Encodage du type de tir
def encode_shot_type(shot_type):
    if shot_type == '2PT Field Goal':
        return 2
    elif shot_type == '3PT Field Goal':
        return 3
    else:
        return 0  # Cas improbable

def processed_data_raw(df_raw):

    # Colonnes à supprimer
    cols_to_drop = ['Game ID', 'Game Event ID', 'Player Name', 'Team ID', 'Team Name',
                    'Period', 'Season Type', 'Game Date', 'Home Team', 'Away Team']

    # Création d'un nouveau dataframe sans ces colonnes
    nba_data_clean = df_raw.drop(columns=cols_to_drop)

    # Vérification des doublons
    duplicates_count = nba_data_clean.duplicated().sum()
    print(f"Nombre de doublons: {duplicates_count}")

    # Suppression des doublons si nécessaire
    nba_data_clean = nba_data_clean.drop_duplicates()

    # Vérification des valeurs manquantes
    missing_values = nba_data_clean.isnull().sum()
    print("Valeurs manquantes par colonne:")
    print(missing_values)

    # Remplacement des valeurs manquantes pour les colonnes numériques
    numeric_cols = nba_data_clean.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        if nba_data_clean[col].isnull().sum() > 0:
            # Remplacement par la médiane
            nba_data_clean[col].fillna(nba_data_clean[col].median(), inplace=True)


    # Conversion des minutes et secondes en secondes totales restantes
    try:

        # Convertir en numérique avec gestion d'erreur
        for col in ['Minutes Remaining', 'Seconds Remaining']:
            nba_data_clean[col] = pd.to_numeric(nba_data_clean[col], errors='coerce')

        # Supprimer les lignes où la conversion a échoué (NaN)
        nba_data_clean.dropna(subset=['Minutes Remaining', 'Seconds Remaining'], inplace=True)

        # Convertir en int proprement (type int64)
        nba_data_clean['Minutes Remaining'] = nba_data_clean['Minutes Remaining'].astype(int)
        nba_data_clean['Seconds Remaining'] = nba_data_clean['Seconds Remaining'].astype(int)

        # Calcul de la colonne finale
        nba_data_clean['Total_Seconds_Remaining'] = (
            nba_data_clean['Minutes Remaining'] * 60 + nba_data_clean['Seconds Remaining']
        )

        nba_data_clean = nba_data_clean.drop(columns=['Minutes Remaining', 'Seconds Remaining'])

    except KeyError:
        # Si erreur, trouver les colonnes temporelles
        time_cols = [col for col in nba_data_clean.columns if 'minute' in col.lower() or 'second' in col.lower() or 'remaining' in col.lower()]
        print(f"Colonnes temporelles disponibles: {time_cols}")

        # Trouver les noms exacts
        minutes_col = [col for col in time_cols if 'minute' in col.lower()][0]
        seconds_col = [col for col in time_cols if 'second' in col.lower()][0]

        # Créer la nouvelle caractéristique
        nba_data_clean['Total_Seconds_Remaining'] = (nba_data_clean[minutes_col] * 60) + nba_data_clean[seconds_col]
        nba_data_clean = nba_data_clean.drop(columns=[minutes_col, seconds_col])
    

    nba_data_clean['Shot_Type_Encoded'] = nba_data_clean['Shot Type'].apply(encode_shot_type)


    # Conversion de pieds en mètres (1 pied = 0.3048 mètre)
    shot_distance = nba_data_clean['Shot Distance'].astype(float)
    nba_data_clean['Shot_Distance_Meters'] = shot_distance * 0.3048


    # Création de la colonne Shot_Zone_Range_Numeric AVANT de l'utiliser
    zone_range_mapping = {
        'Less Than 8 ft.': 1,
        '8-16 ft.': 2,
        '16-24 ft.': 3,
        '24+ ft.': 4,
        'Back Court Shot': 5
    }
    nba_data_clean['Shot_Zone_Range_Numeric'] = nba_data_clean['Shot Zone Range'].map(zone_range_mapping).fillna(0)


    # Création de la colonne Shot_Zone_Range_Numeric AVANT de l'utiliser
    zone_range_mapping = {
        'Less Than 8 ft.': 1,
        '8-16 ft.': 2,
        '16-24 ft.': 3,
        '24+ ft.': 4,
        'Back Court Shot': 5
    }
    nba_data_clean['Shot_Zone_Range_Numeric'] = nba_data_clean['Shot Zone Range'].map(zone_range_mapping).fillna(0)


    # Création de la variable de zone combinée (7 zones)
    def create_combined_zone(basic, area, range_num):
        if basic == 'Restricted Area':
            return 1  # Zone restreinte près du panier
        elif basic == 'In The Paint (Non-RA)':
            return 2  # Dans la raquette (hors zone restreinte)
        elif basic == 'Mid-Range':
            if area in ['Left Side(L)', 'Left Side Center(LC)']:
                return 3  # Mid-range côté gauche
            else:
                return 4  # Mid-range côté droit ou centre
        elif basic == 'Above the Break 3':
            return 5  # 3 points au-dessus de la ligne
        elif 'Corner 3' in basic:
            return 6  # Corner 3 (gauche ou droite)
        elif basic == 'Backcourt':
            return 7  # Tir depuis son propre terrain
        else:
            return 0  # Autre

    # Maintenant on peut combiner cette colonne
    nba_data_clean['Shot_Zone_Combined'] = nba_data_clean.apply(
        lambda row: create_combined_zone(row['Shot Zone Basic'], row['Shot Zone Area'], row['Shot_Zone_Range_Numeric']),
        axis=1
    )

    # Sélection des variables finales
    dataset_final = nba_data_clean[[
        'Player ID',                  # Identifiant du joueur
        'X Location',                 # Position X sur le terrain
        'Y Location',                 # Position Y sur le terrain
        'Total_Seconds_Remaining',    # Temps total restant
        'Shot_Type_Encoded',          # Type de tir (2 pts ou 3 pts)
        'Shot_Distance_Meters',       # Distance convertie en mètres
        'Shot_Zone_Combined',         # Zone de tir (7 zones)
        'Shot Made Flag'              # Variable cible (si le tir est réussi)
    ]]

    dataset_final.rename(columns={
        'Player ID':'Player_ID',            # Identifiant du joueur
        'X Location':'X_Location',          # Position X sur le terrain
        'Y Location':'Y_Location',          # Position Y sur le terrain
        'Shot Made Flag':'Shot_Made_Flag'   # Variable cible (si le tir est réussi)
    }, inplace=True)
    
    dataset_final = dataset_final.astype({
        'Player_ID':int,                  # Identifiant du joueur
        'X_Location':int,                 # Position X sur le terrain
        'Y_Location':int,                 # Position Y sur le terrain
        'Total_Seconds_Remaining':int,    # Temps total restant
        'Shot_Type_Encoded':int,          # Type de tir (2 pts ou 3 pts)
        'Shot_Distance_Meters':float,      # Distance convertie en mètres
        'Shot_Zone_Combined':int,         # Zone de tir (7 zones)
        'Shot_Made_Flag':int              # Variable cible (si le tir est réussi)
    })

    # Enregistrement du dataset final
    json_processed = dataset_final.to_json(orient="records", lines=False)
    print("Preprocessing optimisé terminé avec 7 variables !")

    return json_processed


def get_raw_json_from_mongo(mongo_uri, db_name, collection_name):
    """
    Récupère des données JSON brutes depuis une collection MongoDB.

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
        #db = client[database_name]
        collection = db[collection_name]

        # Récupération brute des documents (documents JSON)
        documents = list(collection.find())

        # Convertir les documents BSON/JSON en un format lisible par pandas
        # (le json_util permet de gérer les ObjectId, dates, etc.)
        json_data = json.loads(json_util.dumps(documents))

        # Convertir en DataFrame
        df_raw = pd.json_normalize(json_data)
        
        return df_raw

    except pymongo.errors.PyMongoError as e:
        print(f"Erreur MongoDB : {e}")
        return False

    finally:
        client.close()



def inject_processed_json_to_mongo(mongo_uri, db_name, collection_name, processed_data):
    """
    Injecte des données JSON processées dans une collection MongoDB.

    :param mongo_uri: URL de connexion MongoDB (ex: 'mongodb://localhost:27017/')
    :param db_name: Nom de la base de données MongoDB
    :param collection_name: Nom de la collection MongoDB
    :return: True si l'injection a réussi, False sinon
    """
    success, client = connect_to_mongo(mongo_uri)
    if not success:
        return False, "Impossible de se connecter à MongoDB"

    try:
        db = client[db_name]

        # Vérification et création de la collection si nécessaire
        if not ensure_collection_exists(db, collection_name):
            return False

        collection = db[collection_name]

        collection.delete_many({})

        data = json.loads(processed_data)

        try:
            if isinstance(data, list) and data:
                result = collection.insert_many(data)
                print(f"{len(result.inserted_ids)} documents insérés.")
            elif isinstance(data, dict) and data:
                result = collection.insert_one(data)
                print("1 document inséré.")
            else:
                print("Aucune donnée valide à insérer.")
                return False
        except Exception as e:
            print("Erreur lors de l'insertion :", e)

        print("Données insérées avec succès dans MongoDB !")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")
        return False
    except pymongo.errors.PyMongoError as e:
        print(f"Erreur MongoDB : {e}")
        return False
    finally:
        client.close()

def check_mongo(mongo_uri, db_name):
    """
    Vérifie l'état des collections d'une base MongoDB.
    """
    success, client = connect_to_mongo(mongo_uri)
    if not success:
        return False, "Impossible de se connecter à MongoDB"

    try:
        print("Analyse de la base de données")
        print("----------")
        db = client[db_name]
        
        # Récupération des informations sur les collections
        collections_info = []
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            doc_count = collection.count_documents({}) # Comptage des documents
            sample_docs = list(collection.aggregate([{"$sample": {"size": 3}}])) # Récupération d'un échantillon de documents
                
            # Analyse des champs
            fields = set()
            for doc in sample_docs:
                fields.update(doc.keys())
            
            # Estimation de la taille de la collection
            stats = db.command("collstats", collection_name)
            size_mb = stats["size"] / (1024 * 1024)
            
            collections_info.append({
                "name": collection_name,
                "document_count": doc_count,
                "fields": list(fields),
                "size_mb": round(size_mb, 2),
                "sample_docs": sample_docs
            })
        
        result_dict = {
            "db_name": db_name,
            "collections_info": collections_info
            }

        print(result_dict)
        return True

    except pymongo.errors.PyMongoError as e:
        return False, f"Erreur lors de l'analyse de la base de données : {str(e)}"
        
    finally:
        client.close()


if __name__ == '__main__':

    # Config
    host = "parivision.heuzef.com"
    port = "27017"
    username = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    database_name = "parivision"
    collection_raw_name = "parivision_raw"
    collection_processed_name = "parivision_processed"
    # URI MongoDB avec login/mot de passe
    mongo_uri = f"mongodb://{username}:{password}@{host}:{port}"

    # Récupère le json brut de mongodb
    df_raw = get_raw_json_from_mongo(mongo_uri, database_name, collection_raw_name)
    print("df_raw", df_raw)

    # Processes les données du dataframe
    json_processed = processed_data_raw(df_raw)
    print("json_processed", json_processed)

    # Insert le json proccesed dans mondo db
    success = inject_processed_json_to_mongo(mongo_uri, database_name, collection_processed_name, json_processed)

    if success:
        print("L'opération a réussi !")
        check_mongo(mongo_uri, database_name)
    else:
        print("L'opération a échoué !")