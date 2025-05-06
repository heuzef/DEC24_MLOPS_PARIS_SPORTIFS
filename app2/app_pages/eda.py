#INIT
from init import *

def content():
   
    st.write(r"""<style>.stAppDeployButton { display: none; }</style>""", unsafe_allow_html=True) # Hide Deploy button

    st.write(f"# Visualisation des données")
    st.divider()

    st.image(st.session_state['imagePath'] + 'mongodb.png', width=200, caption="")
    st.markdown("## Connexion à la base de données MongoDB")

    st.markdown("Cette page se connecte à la base MongoDB avec PyMongo pour récupérer les données d'analyse.")
    st.markdown("La base de données contient principalement 2 collections :")
    st.markdown("* parivision_raw : Données brutes collectées (matchs, joueurs, tirs, etc.)")
    st.markdown("* parivision_processed : Données traitées et préparées pour le modèle prédictif")


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