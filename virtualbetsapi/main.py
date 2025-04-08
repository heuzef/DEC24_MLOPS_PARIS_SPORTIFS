from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials 
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional
from pydantic import BaseModel, ValidationError, Field
import json
import os


app = FastAPI(
    title="Virtual Bets API",
    description="My Virtual Bets datas API powered by FastAPI.",
    version="1.0.0")

#----------------------------------------------------
# File paths
#----------------------------------------------------
chemin_fichier = "/app/data/data_nba.json"
counter_file = "/app/data/counter.txt"

#----------------------------------------------------
# Gestion du compteur
#----------------------------------------------------
# Fonction pour lire le compteur depuis le fichier
def read_counter():
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            counter = int(f.read())
            print(counter)
            return counter
    else:
        return 0  # Valeur par défaut si le fichier n'existe pas

# Fonction pour sauvegarder le compteur dans le fichier
def save_counter(counter):
    with open(counter_file, "w") as f:
        f.write(str(counter))

# Fonction pour raz le compteur dans le fichier
def reset_counter():
    with open(counter_file, "w") as f:
        f.write(str(0))

#----------------------------------------------------
# Personalisation du gestionnaire d'exception
#----------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Custom message for missing fields
    errors = []
    for error in exc.errors():
        if error['type'] == 'missing':
            errors.append({
                "type": "missing",
                #"loc": error['loc'],
                "msg": f"Le champ {error['loc'][1]} est manquant. Veuillez corriger le payload.",
                #"input": error.get('input', {}),
            })
        else:
            errors.append(error)
    
    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )

#----------------------------------------------------
# Définition des APIs
#----------------------------------------------------
@app.get('/getdata/reset', name='Remise à zero du compteur')
async def resetcompteur():
    try:
        reset_counter()
        api_counter = read_counter()
    
        return api_counter

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{chemin_fichier}' n'a pas été trouvé.")
        raise HTTPException(status_code=500, detail="Le payload est incorrect")
        return []
        

@app.get('/getdata/{nb_node:int}', name='Récupération des données en fonction du nombre de node souhaités')
async def getdata(nb_node:int):
    try:
        api_counter = read_counter()
        with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
            donnees = json.load(fichier)

            if not isinstance(donnees, list):
                print("Le contenu du fichier JSON doit être une liste.")
                raise ValueError("Le contenu du fichier JSON doit être une liste.")

            if not (0 <= nb_node + api_counter < len(donnees)):
                print("Index de début invalide.")
                reset_counter()
                return donnees[api_counter:len(donnees)]
                #raise ValueError("Index de début invalide.")

            #if not (api_counter <= nb_node + api_counter <= len(donnees)):
            #    print("Index de fin invalide.")
            #    raise ValueError("Index de fin invalide.") # passer sur un autre json

            save_counter(nb_node + api_counter)

            return donnees[api_counter:nb_node + api_counter]

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{chemin_fichier}' n'a pas été trouvé.")
        raise HTTPException(status_code=500, detail="Le payload est incorrect")
        return []
    except json.JSONDecodeError:
        print("Erreur : Le fichier JSON n'est pas valide.")
        raise HTTPException(status_code=500, detail="Le payload est incorrect")
        return []
