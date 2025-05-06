#INIT
from init import *

st.set_page_config(page_title="EDA", page_icon="📊")
st.write(r"""<style>.stAppDeployButton { display: none; }</style>""", unsafe_allow_html=True) # Hide Deploy button

# BODY
colored_header(
    label="Visualisation des données",
    description="Explorez les données de la base MongoDB et visualisez les statistiques",
    color_name="gray-80",
)

st.markdown("""
    ## Connexion à la base de données MongoDB
    Cette page se connecte à la base MongoDB avec PyMongo pour récupérer les données d'analyse.
    La base de données contient principalement 2 collections :

    * parivision_raw : Données brutes collectées (matchs, joueurs, tirs, etc.)
    * parivision_processed : Données traitées et préparées pour le modèle prédictif
    """)

st.divider()

st.markdown("""
    ### Liste des collections connectés
    """)
for collection in db.list_collection_names():
    st.write(collection)

st.divider()

col1, col2 = st.columns(2)
col1.metric(label="Nombre de documents bruts", value=parivision_raw.count_documents({}))
col2.metric(label="Nombre de documents pré-traités", value=parivision_processed.count_documents({}))

st.divider()

st.markdown("""
    ### Afficher un document brut et un document pré-traité
    """)

col1, col2 = st.columns(2)
col1.write(parivision_raw.find_one({}))
col2.write(parivision_processed.find_one({}))

style_metric_cards()