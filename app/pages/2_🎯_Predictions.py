#INIT
from init import *

def predict_button():
    with stylable_container(
        key="gold_button",
        css_styles="""
            button {
                display: flex;
                align-items: center;
                justify-content: center;
                line-height: 1;
                text-decoration: none;
                color: #000000;
                font-size: 18px;
                border-radius: 0px;
                width: 250px;
                height: 50px;
                font-weight: bold;
                border: 3px solid #5e227c;
                transition: 0.3s;
                text-shadow: 2px 2px 2px rgba(255, 255, 255, 0.8);
                transform: skew(-20deg);
                background-color: #ffd700;
                text-transform: uppercase;
            }
            """,
    ):
        if st.button("Calculer la prediction"):
            prediction = parivison_predict(inputs=inputs)
            if prediction > 0 : 
                st.markdown(f"""
                <style>
                    .container {{
                        border: 3px solid #5e227c;
                        padding-top: 10px;
                        border-radius: 5px;
                        background-color: gold;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 1);
                        text-align: center;
                        font-size: 30px;
                        color: green;
                        transform: skew(-20deg);
                        text-transform: uppercase;
                    }}
                </style>
                <div class="container">
                    <p>Tir réussi !</p>
                </div>

                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <style>
                    .container {{
                        border: 3px solid #5e227c;
                        padding-top: 10px;
                        border-radius: 5px;
                        background-color: gold;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 1);
                        text-align: center;
                        font-size: 20px;
                        color: red;
                        transform: skew(-20deg);
                    }}
                </style>
                <div class="container">
                    <p>Échec du tir</p>
                </div>
                """, unsafe_allow_html=True)


st.set_page_config(page_title="Prédictions", page_icon="🎯")
st.write(r"""<style>.stAppDeployButton { display: none; }</style>""", unsafe_allow_html=True) # Hide Deploy button

# BODY
colored_header(
    label="Prédictions des paniers",
    description="Utilisez ce formulaire pour prédire la probabilité de réussite d'un tir.",
    color_name="gray-80",
)

coordinates = streamlit_image_coordinates("terrain.png")
if coordinates is not None:
    x_location = coordinates["x"]
    y_location = coordinates["y"]

grid = grid(2, 2, 2, vertical_align="bottom")
players_name = parivision_raw.distinct("Player Name")
player = grid.selectbox("Joueur", players_name)
player_id = player_name_to_id(player_name=player)
if coordinates is not None:
    grid.warning(f"""
        Position du joueur : 
        {str(x_location)}, {str(y_location)}
        """)
else:
    grid.warning("Veuillez cliquer sur le terrain pour définir la position du joueur.")

match_progress = grid.slider("Avancement du match en secondes : ", 0, 2880, 2000)
total_seconds_remaining = 2880 - match_progress
shot_distance_meters = grid.slider("Distance du tir en mètres", 0, 29, 1)

zones_list = [
    "Restricted Area",
    "Mid-Range",
    "Above the Break 3",
    "Right Corner 3",
    "In The Paint (Non-RA)",
    "Left Corner 3",
    "Backcourt"
]

shot_zone_combined = button_selector(
    zones_list,
    index=1,
    spec=7,
    key="zones_selector",
    label="Zone du tir",
)

actions_list = [
    "Layup Shot",
    "Jump Shot",
    "Running Jump Shot",
    "Step Back Jump Shot",
    "Driving Layup Shot",
    "Hook Shot",
    "Tip Shot",
    "Turnaround Jump Shot",
    "Pullup Jump Shot",
    "Dunk Shot"
]

shot_type_encoded = button_selector(
    actions_list,
    index=1,
    spec=5,
    key="actions_selector",
    label="Type de tir",
)

inputs = {
    "Player_ID": player_id,
    "X_Location": x_location,
    "Y_Location": y_location,
    "Total_Seconds_Remaining": total_seconds_remaining,
    "Shot_Type_Encoded" : shot_type_encoded,
    "Shot_Distance_Meters": float(shot_distance_meters),
    "Shot_Zone_Combined": shot_zone_combined
}

st.divider()

left, middle, right = st.columns(3)
with middle:
    predict_button()

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