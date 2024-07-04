import streamlit as st
from backend import graf_ecv_anual, graf_dia

st.set_page_config(layout='wide')
st.title('Escala Cavero-Vidal :copyright:')

graf1_año=graf_ecv_anual()
st.plotly_chart(graf1_año)

with st.container():
    col1, col2 = st.columns([0.4,0.6])
    with col1:
        with st.container():
            col3,col4=st.columns([0.7,0.3])
            with col3:
                st.empty()
                st.text("¿Quieres pasar al mercado minorista de indexado? Aquí: -->")
            with col4:
                st.link_button("Telemindex webapp","https://telemindexpy-josevidal.streamlit.app/")
    with col2:
        st.empty()
#graf1_1=graf_dia()
#st.plotly_chart(graf1_1)