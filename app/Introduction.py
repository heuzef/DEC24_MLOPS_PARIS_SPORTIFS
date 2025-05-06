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

st.sidebar.title("L'équipe du projet")

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
    
    Tuteur Antoine Fradin. Juin 2025.
    """)

st.sidebar.divider()

# BODY
st.image("parivision_logo.png", caption=None, width=300)

st.markdown("""
*Projet d'étude concernant la mise en production d'un modèle d'IA dans le domaine du paris sportif.*
""")

st.link_button("🔗 Site principal du projet", type='primary', url="https://parivision.heuzef.com")
st.link_button("⬇️ Télécharger le rapport PDF", type='secondary', url="https://github.com/heuzef/parivision/src/branch/master/reports/parivision_report.pdf")

st.divider()

st.image("WORKFLOW.png", caption="Notre approche méthodologique pour la mise en production d'un modèle d'IA dans le domaine des paris sportifs.", use_container_width=True)