import streamlit as st
from backend import graf_ecv_anual, graf_ecv_anual_queso, graf_ecv_mensual

#pg = st.navigation([st.Page("escalacv.py"), st.Page("pages/page_1.py")])
#pg.run()

st.set_page_config(
    page_title="Escala Cavero Vidal",
    page_icon=":bulb:",
    layout='wide',
)
st.title('Escala Cavero-Vidal :copyright:')
st.caption("Basada en los #telepool de Roberto Cavero. Copyright by Jose Vidal :ok_hand:")

#with st.sidebar():

#st.page_link("escalacv.py", label="Home", icon="🏠")
#st.page_link("pages/page_1.py", label="Page 1", icon="1️⃣")

#graf1_año=graf_ecv_anual()
st.plotly_chart(graf_ecv_anual())

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

col5,col6,col7=st.columns(3)
with col5:
    st.plotly_chart(graf_ecv_anual_queso())
with col6:
    st.plotly_chart(graf_ecv_mensual())
#st.plotly_chart(graf2_año)
#graf1_1=graf_dia()
#st.plotly_chart(graf1_1)