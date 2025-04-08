import pymongo
import os
from dotenv import load_dotenv
load_dotenv(".env")

def remove_data(uri, database_name):
    """
    Vide toutes les collections d'une base MongoDB.
    
    :param uri: URL de connexion MongoDB (ex: "mongodb://localhost:27017/")
    :param database_name: Nom de la base de données à vider.
    """
    try:
        # Connexion à MongoDB
        client = pymongo.MongoClient(uri)
        db = client[database_name]

        # Récupération des collections
        collections = db.list_collection_names()
        
        if not collections:
            print(f" La base '{database_name}' est déjà vide.")
            return

        # Suppression des documents dans chaque collection
        for collection in collections:
            db[collection].delete_many({})
            print(f"Table '{collection}' vidée.")

        print(f" Toutes les tables de la base '{database_name}' ont été vidées.")

    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        client.close()

# Fonction principale
if __name__ == "__main__":
    # Config
    ip = "parivision.heuzef.com"
    port = "27017"
    username = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    db_name = "parivision"

    uri = "mongodb://"+username+":"+password+"@"+ip+":"+port
    
    # Appel de la fonction
    remove_data(uri, db_name)