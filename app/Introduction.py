#INIT
from init import *

st.set_page_config(page_title="PariVison", page_icon="🏆", layout="wide")
st.write(r"""<style>.stAppDeployButton { display: none; }</style>""", unsafe_allow_html=True) # Hide Deploy button

# RAIN
rain(
    emoji="🏆",
    font_size=20,
    falling_speed=4,
    animation_length=1,
)

# SIDEBAR
heuzef = mention(
    label="Heuzef",
    icon="🌐",
    url="https://heuzef.com",
    write=False,
)

pierre = mention(
    label="Pierre Cohen",
    icon="🤓",
    url="#",
    write=False,
)

shi = mention(
    label="Shi Jianying",
    icon="🥢",
    url="#",
    write=False,
)

st.sidebar.title("Crédits")

st.sidebar.write(
    f"""
    {heuzef}
    {pierre}
    {shi}
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f"""
    Projet d'étude en datascience accompagné par [DataScientest](https://www.datascientest.com). 
    
    Juin 2025.
    """)

# BODY
colored_header(
    label="🏆 PariVision",
    description="MLOPS",
    color_name="blue-70",
)

st.markdown(
    """
    ## Sujet

    This project demonstrates MLOps best practices using a machine learning model that predicts if an NBA player will make a specific shot or not. The emphasis is less on the machine learning model, and more on the automated data pipeline to train the model, the deployment of the model, and the monitoring of the model.

    ## Contexte

    ...

    """)