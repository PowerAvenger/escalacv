import streamlit as st
from backend import graf_ecv_anual, graf_dia

st.set_page_config(layout='wide')
st.title('Escala Cavero-Vidal')

graf1_año=graf_ecv_anual()
st.plotly_chart(graf1_año)
#graf1_1=graf_dia()
#st.plotly_chart(graf1_1)