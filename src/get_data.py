import requests
from pprint import pprint
import pymongo
import os
import argparse
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

def inject_json_to_mongo(mongo_uri, db_name, collection_name, api_url):
    """
    Récupère des données JSON depuis une API et les injecte dans une collection MongoDB.

    :param mongo_uri: URL de connexion MongoDB (ex: 'mongodb://localhost:27017/')
    :param db_name: Nom de la base de données MongoDB
    :param collection_name: Nom de la collection MongoDB
    :param api_url: URL de l'API renvoyant des données JSON
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

        # Récupération des données JSON depuis l'API
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Injection des données dans MongoDB
        if isinstance(data, list) and data:
            collection.insert_many(data)
        elif isinstance(data, dict) and data:
            collection.insert_one(data)
        else:
            print("Aucune donnée valide à insérer.")
            return False  # Échec car les données sont invalides

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

        pprint(result_dict)
        return True

    except pymongo.errors.PyMongoError as e:
        return False, f"Erreur lors de l'analyse de la base de données : {str(e)}"
        
    finally:
        client.close()

# Config
ip = "parivision.heuzef.com"
port = "27017"
username = os.getenv('MONGO_INITDB_ROOT_USERNAME')
password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
db_name = "parivision"
collection_name = "parivision_raw"
uri = "mongodb://"+username+":"+password+"@"+ip+":"+port

# Build and analyze ArgumentParser object
parser = argparse.ArgumentParser(description="Get Data Script")
parser.add_argument('quantity', type=int, help="quantity of data to retrieve")
args = parser.parse_args()

api_url = f"http://localhost:8800/getdata/{args.quantity}/" # VirtualBetsAPI

success = inject_json_to_mongo(uri, db_name, collection_name, api_url)

if success:
    print("L'opération a réussi !")
    check_mongo(uri, db_name)
else:
    print("L'opération a échoué !")