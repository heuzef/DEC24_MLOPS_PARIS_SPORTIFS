#INIT
from init import *

def content():

    st.write(f"# {st.session_state['app_name']}")
    st.markdown("""
    *Projet d'étude concernant la mise en production d'un modèle d'IA dans le domaine du paris sportif.*
    """)
    st.divider()
    st.image(st.session_state['imagePath'] + 'dunk.jpg', caption="")
    st.divider()
    st.write("## Présentation")
    st.write(
            "Le basketball, en particulier la NBA (National Basketball Association), figure parmi les sports les plus prisés au monde." 
            "Il attire des millions de spectateurs et génère un marché économique colossal, notamment dans le domaine des paris sportifs."
            "Avec une saison régulière comprenant 82 matchs par équipe et des playoffs intenses, la NBA offre un volume conséquent de données exploitables pour l’analyse prédictive."
            "Dans ce contexte, où chaque tir peut influencer l’issue d’un match et générer des enjeux stratégiques, économiques (paris sportifs, droits TV) ou émotionnels (engagement des fans), la capacité à prédire la réussite d’un tir spécifique devient un atout précieux."
            "Notre projet PariVision se concentre sur cette problématique en combinant machine learning et ingénierie MLOps pour concevoir un système prédictif robuste et automatisé, capable d’estimer les résultats des matchs NBA."
            "La complexité réside dans la modélisation des multiples facteurs influençant un tir : position sur le terrain, pression défensive, fatigue du joueur, ou même le contexte du match (dernières secondes, enjeux du score). Les approches statiques peinent à s’adapter à la variabilité des données sportives, nécessitant une infrastructure capable d’évoluer avec les saisons et les métriques émergentes."
            "Ce projet illustre comment le MLOps peut transformer des données brutes en entrées exploitable, en alignant précision algorithmique et exigences opérationnelles du monde sportif."
            )
    st.write("## Objectifs")
    st.write(
            "En ciblant cette problématique, nous élaborons les objectifs suivants :"
            "Prédiction contextuelle : Déterminer la probabilité de réussite d’un tir en temps réel, en s’appuyant sur des données synthétiques ou historiques."
            "Automatisation des workflows : Conteneuriser chaque étape (génération de données, feature engineering, entraînement) avec Docker, et orchestrer les pipelines via GitHub Actions et Jenkins."
            "Adaptabilité continue : Implémenter un système de ré-entrainement conditionnel, où un nouveau modèle (Random Forest, XGBoost) ne remplace l’ancien que si son accuracy dépasse celle de l’ancien modèle."
            "Garantir la traçabilité et la reproductibilité avec des intégrations CI/CD (GitHub Actions), MLFlow et Jenkins."
            "Surveillance en production grâce à Grafana et Prometheus, assurant un monitoring granulaire des requêtes API et de la base de données MongoDB."
            )

    

    st.link_button("🔗 Site principal du projet", type='primary', url="https://parivision.heuzef.com")
    st.link_button("⬇️ Télécharger le rapport PDF", type='secondary', url="https://github.com/heuzef/DEC24_MLOPS_PARIS_SPORTIFS/blob/main/reports/parivision_report.pdf")

    st.divider()
    
    st.write("## La pipeline Parivision")

    st.image(st.session_state['imagePath'] + 'WORKFLOW.png', caption="Notre approche méthodologique pour la mise en production d'un modèle d'IA dans le domaine des paris sportifs.")