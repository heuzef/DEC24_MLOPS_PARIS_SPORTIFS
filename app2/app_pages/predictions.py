#INIT
from init import *

#-------------------------
# Définition des fonctions
#-------------------------
def predict_button(inputs):
    
    col1, col2, col3 = st.columns([1, 13, 1])

    with col2:
        if st.button("Calculer la prediction"):
            prediction = parivison_predict(inputs)
            if prediction > 0 : 
                st.html(f"""
                <style>
                    .container {{
                        background: linear-gradient(135deg, #3b2cd3, #f72585);  /* Dégradé violet-rose */
                        border: none;
                        padding: 1rem;
                        border-radius: 12px;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
                        text-align: center;
                        font-size: 1.8rem;
                        color: white;
                        font-weight: bold;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        max-width: 500px;
                        width: 250px;
                        height: 50px;
                        margin: auto;
                        animation: pulse 1.5s infinite;
                    }}
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.03); }}
                        100% {{ transform: scale(1); }}
                    }}
                    </style>
                    <div class="container">
                        <p>Tir réussi !</p>
                    </div>
                """)
            else:
                st.html(f"""
                <style>
                    .container {{
                        background: linear-gradient(135deg, #f72585,#3b2cd3);  /* Dégradé violet-rose */
                        border: none;
                        padding: 1rem;
                        border-radius: 12px;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
                        text-align: center;
                        font-size: 1.8rem;
                        color: white;
                        font-weight: bold;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        max-width: 500px;
                        width: 250px;
                        height: 50px;
                        margin: auto;
                        animation: pulse 1.5s infinite;
                    }}
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.03); }}
                        100% {{ transform: scale(1); }}
                    }}
                    </style>
                    <div class="container">
                        <p>Échec du tir !</p>
                    </div>
                """)

def calculer_distance_tir(x, y, panier_x, panier_y, pixel_cm):
    """
    Calcule la distance d'un tir depuis le panier en mètres.

    :param x: Coordonnée X du tir
    :param y: Coordonnée Y du tir
    :param panier_x: Coordonnée X du panier (défaut = 0)
    :param panier_y: Coordonnée Y du panier (défaut = 0)
    :param pixel_cm: Échelle de conversion (1 pixel = X cm), défaut = 1 (1 cm/pixel)
    :return: Distance en mètres (arrondie à 2 décimales)
    """
    dx = x - panier_x
    dy = y - panier_y
    distance_pixels = math.sqrt(dx**2 + dy**2)
    return round(distance_pixels*0.051, 2)

def classify_shot(x, y):
    for zone, props in correspondance_vertical.items():
        in_x = props["x_range"][0] <= x <= props["x_range"][1]
        in_y = props["y_range"][0] <= y <= props["y_range"][1]
        if in_x and in_y:
            return {
                "zone": zone,
                "shot_type": props["shot_type"],
            }
    return {
        "zone": "Zone inconnue",
        "shot_type": "Undetermined",
    }


def normalize_coord(val, min_val, max_val, target_min, target_max):
    return ((val - min_val) / (max_val - min_val)) * (target_max - target_min) + target_min

def normalize_point(x, y,
                    x_min, x_max,
                    y_min, y_max,
                    target_x_min, target_x_max,
                    target_y_min, target_y_max,
                    invert_y=False):
    """
    Normalise un point (x, y) vers une nouvelle échelle.
    :param invert_y: si True, inverse l'axe Y (utile pour image avec Y croissant vers le bas)
    """
    x_new = normalize_coord(x, x_min, x_max, target_x_min, target_x_max)
    
    if invert_y:
        y = y_max - y # inverser y pour images top-down
    
    y_new = normalize_coord(y, y_min, y_max, target_y_min, target_y_max - y_min - 3)

    return int(round(x_new, 2)), int(round(y_new, 2)) 


def distance_metre(x1, y1, x2, y2,
                   x_min=-250, x_max=250, terrain_largeur_m=15,
                   y_min=0, y_max=500, terrain_longueur_m=29):
    facteur_x = terrain_largeur_m / (x_max - x_min)
    facteur_y = terrain_longueur_m / (y_max - y_min)
    
    dx = (x2 - x1) * facteur_x
    dy = (y2 - y1) * facteur_y
    distance = math.sqrt(dx**2 + dy**2)
    return round(distance, 2)

def convert_combined_zone(area):
        if area == 'Restricted Area':
            return 1  # Zone restreinte près du panier
        elif area == 'In The Paint (Non-RA)':
            return 2  # Dans la raquette (hors zone restreinte)
        elif area in ['Mid-Range Left Side (L)', 'Mid-Range Left Side Center (LC)']:
            return 3  # Mid-range côté gauche
        elif area in ['Mid-Range Right Side (L)', 'Mid-Range Right Side Center (LC)']:
            return 4  # Mid-range côté droit ou centre
        elif area == 'Above the Break 3':
            return 5  # 3 points au-dessus de la ligne
        elif area == 'Right Corner 3' or area == 'Left Corner 3':
            return 6  # Corner 3 (gauche ou droite)
        elif area == 'Backcourt':
            return 7  # Tir depuis son propre terrain
        else:
            return 0  # Autre

def convert_shot_type(shot_type):
        if shot_type == '2PT Field Goal':
            return 2  # Zone restreinte près du panier
        elif shot_type == '3PT Field Goal':
            return 3
        else:
            return 0  # Autre

# Table de correspondance
correspondance_vertical = {
    "Restricted Area": {
        "x_range": (-180,180),
        "y_range": (0,60),
        "shot_type": "2PT Field Goal"
    },
    "In the paint (non-RA)": {
        "x_range": (-250,250),
        "y_range": (60,190),
        "shot_type": "2PT Field Goal"
    },
    "Mid-Range Left Side (L)": {
        "x_range": (-220,-60),
        "y_range": (190,280),
        "shot_type": "2PT Field Goal"
    },
    "Mid-Range Left Side Center (LC)": {
        "x_range": (-80,0),
        "y_range": (90,280),
        "shot_type": "2PT Field Goal"
    },
    "Mid-Range Right Side Center (RC)": {
        "x_range": (0,80),
        "y_range": (190,280),
        "shot_type": "2PT Field Goal"
    },
    "Mid-Range Right Side (R)": {
        "x_range": (80,220),
        "y_range": (190,280),
        "shot_type": "2PT Field Goal"
    },
    "Above the Break 3": {
        "x_range": (-220,220),
        "y_range": (280,470),
        "shot_type": "3PT Field Goal"
    },
    "Right Corner 3": {
        "x_range": (200,250),
        "y_range": (60,120),
        "shot_type": "3PT Field Goal"
    },
    "Left Corner 3": {
        "x_range": (-250,-200),
        "y_range": (60,120),
        "shot_type": "3PT Field Goal"
    },
    "Backcourt": {
        "x_range": (-300,300),
        "y_range": (470,600),
        "shot_type": "3PT Field Goal"
    }
}

def content():

    st.write(f"# Prédictions de paniers")

    st.divider()

    img = Image.open("images/nba_playground.jpg")
    img = img.resize((468, 700))  # largeur x hauteur en pixels
    st.write(f"Veuillez cliquer sur le terrain pour définir la position du joueur.")    
    coordinates = streamlit_image_coordinates(img)

    visible = 0

    new_x, new_y = 0, 0

    if coordinates is not None:

        new_x, new_y = normalize_point(
            coordinates["x"], coordinates["y"],
            x_min=42, x_max=422,
            y_min=-41, y_max=610,
            target_x_min=-250, target_x_max=250,
            target_y_min=0, target_y_max=500,
            invert_y=True  # car image = haut → bas
        )
   
    my_grid = grid(2, 2, 2, vertical_align="bottom")
    players_name = parivision_raw.distinct("Player Name")
    player = my_grid.selectbox("Joueur", players_name)
    player_id = int(player_name_to_id(player_name=player))

    resultat = {
        "zone": "",
        "shot_type": ""
    }
    
    selected_type = ""

    distance = 0

    if coordinates is not None:

        visible = 1

        img_with_point = img.copy()
        draw = ImageDraw.Draw(img_with_point)
        r = 6  # rayon du point
        draw.ellipse((new_x - r, new_y - r, new_x + r, new_y + r), fill="red", outline="black")

        resultat = classify_shot(new_x, new_y)

        distance = distance_metre(new_x, new_y, 0, 25)

        # my_grid.warning(f"""
        #     Position du joueur : 
        #     {str(new_x)}, {str(new_y)}, {str(resultat["zone"])}, {str(resultat["types_probables"])}, {str(resultat["distance_range_m"])}, {str(distance)}
        #     """)

        my_grid.warning(f"""
            Position du joueur : 
            {str(new_x)}, {str(new_y)},
            """)
    else:
        my_grid.warning("Veuillez cliquer sur le terrain pour définir la position du joueur.")

    match_progress = st.slider("Avancement du match en secondes : ", 0, 2880, 2000)
    total_seconds_remaining = 2880 - match_progress

    inputs = {
        "Player_ID": player_id,
        "X_Location": new_x,
        "Y_Location": new_y,
        "Total_Seconds_Remaining": total_seconds_remaining,
        "Shot_Type_Encoded" : convert_shot_type(resultat["shot_type"]),
        "Shot_Distance_Meters": float(distance),
        "Shot_Zone_Combined": convert_combined_zone(resultat["zone"])
    }

    st.divider()
    if visible == 1:
        left, middle, right = st.columns(3)
        with middle:
            predict_button(inputs)

    # SIDEBAR
    st.sidebar.markdown("""
    ## Comment utiliser ce modèle
    Ce modèle prédictif analyse plusieurs facteurs pour estimer la probabilité qu'un joueur marque un panier dans les conditions spécifiées sur un terrain de NBA (demi-terrain FIBA).

    * Cliquez sur le terrain pour définir la position du joueur
    * Sélectionnez le joueur dans la liste
    * Précisez les paramètres du tir
    * Obtenez une prédiction basée sur des milliers de données historiques
    """)

    st.sidebar.divider()

    st.sidebar.markdown("""
    ## Paramètres séléctionnés
    """)

    st.sidebar.json(inputs)

    st.sidebar.divider()

    st.sidebar.markdown("""
    ## Modèle champion
    """)

    st.sidebar.json(
        {
            parivison_get_champion_infos()
        }
    )

