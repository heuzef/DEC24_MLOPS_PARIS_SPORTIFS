# -*- coding: utf-8 -*-
import streamlit as st
import base64
import os

def linked_img(img, url, size=70):
    img_format = os.path.splitext(img)[-1].replace('.', '')
    bin_str = base64.b64encode(open(st.session_state['imagePath'] + img, "rb").read()).decode()
    html_code = f'''
        <a href="{url}">
            <img src="data:image/{img_format};base64,{bin_str}" height={size}px/>
        </a>'''
    return html_code

def content():
    st.markdown("# Crédits")    
    st.divider()
    st.markdown(linked_img('datascientest.jpg', "https://www.datascientest.com/", 150),
    unsafe_allow_html=True,
    
)
    st.divider()
    st.markdown(f'''Le projet {st.session_state['app_name']} a été mené dans le cadre de la formation continue en MLOps de <a href="https://datascientest.com">DataScientest.com</a> promotion décembre 2024.''', unsafe_allow_html=True)
    
    c1, c2  = st.columns(2)
    with c1:
        st.write("## Auteurs")
        st.markdown("<b>Florent Heuze</b>" + linked_img('linkedin.png', 'https://www.linkedin.com/in/heuzef/', 20),  
        unsafe_allow_html=True)  
        st.markdown("<b>Pierre Cohen</b>" + linked_img('linkedin.png', 'https://www.linkedin.com/', 20),  
        unsafe_allow_html=True)  
        st.markdown("<b>Shi</b>" + linked_img('linkedin.png', 'https://www.linkedin.com/', 20),  
        unsafe_allow_html=True)  
    with c2:        
        st.write("## Mentor")
        st.markdown("<b>Antoine Fradin</b>" + linked_img('linkedin.png', 'https://www.linkedin.com/in/antoine-fradin/', 20),  
        unsafe_allow_html=True)    