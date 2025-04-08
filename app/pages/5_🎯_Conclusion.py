#INIT
from init import *

st.set_page_config(page_title="Conclusion", page_icon="🎯")
st.write(r"""<style>.stAppDeployButton { display: none; }</style>""", unsafe_allow_html=True) # Hide Deploy button

# SIDEBAR
st.sidebar.title("Librairies utilisés")

with open('requirements.txt', 'r') as fichier:
    st.sidebar.code(fichier.read(), language="python")

st.sidebar.divider()

st.sidebar.link_button("📖 Rapport détaillé du projet (PDF)", "https://git.heuzef.com/heuzef/parivision/src/branch/master/reports/parivision_report.pdf", type='primary')
st.sidebar.link_button("👩‍💻 Dépôt GIT du projet", "https://git.heuzef.com/heuzef/parivision/", type='primary')

# BODY
colored_header(
    label="Conclusion",
    description="Lorem Ipsum Dolor sit amet",
    color_name="red-70",
)

st.markdown("""
    ### Titre

    Lorem ipsum dolor sit amet ...

    """)

st.image("reports/WORKFLOW.png", caption="WORKFLOW du projet")

st.link_button("🔗 Accéder au serveur de tracking MLFlow", "https://parivision.heuzef.com:5000", type='primary')

st.divider()