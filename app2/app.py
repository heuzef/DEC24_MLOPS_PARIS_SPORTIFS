#INIT
from init import *
    
import app_pages.home
import app_pages.eda
import app_pages.predictions
import app_pages.credits


# Define the "working directory" for streamlit as the ofolder containing app.py
    # This creates a relative path valid for anyone
    # This path can be exported to all pages of the streamlit, and remains a valid way to reference the images folder
    
st.session_state['imagePath'] = 'images/'
st.session_state['app_name'] = 'Parivison'

list_pages = {
    "Home": app_pages.home,
    "Exploratory Data Analysis (EDA)": app_pages.eda,
    "Prédictions": app_pages.predictions,
    "Credits": app_pages.credits
}

def main():

    st.set_page_config(
                    page_title=f"{st.session_state['app_name']} - Projet Parivison",
                    )
    title = f'''<p style="font-family:sans-serif; color:Red; font-size: 48px;"><span class="bolded">{st.session_state['app_name']}</span></p>'''
    
    theme = st_theme()
    dark_mode = theme['base'] == 'dark'
    logo = st.session_state['imagePath'] + 'parivision_logo.png'
    if dark_mode: logo = st.session_state['imagePath'] + 'parivision_logo.png'
    st.html("""
  <style>
    [alt=Logo] {
      height: 15rem;
    }
  </style>
        """)
    st.logo(logo)
  #   st.sidebar.markdown(title, unsafe_allow_html=True)
  #   st.sidebar.image(st.session_state['imagePath'] + 'title.png')
    st.sidebar.title("Sommaire")
    selected_page = st.sidebar.radio("Go to", list(list_pages.keys()))


    page = list_pages[selected_page]
    page.content()

if __name__ == "__main__":
    main()