import streamlit as st
from backend import graf_ecv_anual, graf_ecv_anual_queso, graf_ecv_mensual, graf_horaria,obtener_valores_diarios,fechas_minmax,download_esios_id, ultimo_registro
import time
import datetime
from datetime import datetime
#pg = st.navigation([st.Page("escalacv.py"), st.Page("pages/page_1.py")])
#pg.run()

#token=st.secrets['ESIOS_API_KEY']


st.set_page_config(
    page_title="Escala Cavero Vidal",
    page_icon=":bulb:",
    layout='wide',
)

id='600'
fecha_ini='2024-01-01'
fecha_fin='2024-12-31'
agrupacion='hour'

if'contador' not in st.session_state:
    st.session_state.contador=0
    datos,fecha_descarga=download_esios_id(id,fecha_ini,fecha_fin,agrupacion)
    #st.write(fecha_descarga)
    
    st.rerun()

ultimo_registro=ultimo_registro()
st.write(ultimo_registro)    

st.title('Escala Cavero-Vidal :copyright:')
st.caption("Basada en los #telepool de Roberto Cavero. Copyright by Jose Vidal :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
st.write("Visita mi página de [PowerAPPs](%s) con un montón de utilidades" % url_apps)


valor_medio_diario,valor_minimo_diario,valor_maximo_diario=obtener_valores_diarios()
fecha_min,fecha_max=fechas_minmax()

with st.container():
    col1,col2=st.columns([0.85,0.15])
    with col1:
        st.plotly_chart(graf_ecv_anual())
    with col2:
        st.subheader('Datos en €/MWh',divider='rainbow')
        st.metric('Precio medio diario', value=valor_medio_diario)
        st.metric(f'Precio mínimo diario ( {fecha_min})', value=valor_minimo_diario)
        st.metric(f'Precio máximo diario ({fecha_max})', value=valor_maximo_diario)
#with st.container():
#    col1, col2 = st.columns([0.4,0.6])
#    with col1:
#        with st.container():
#            col3,col4=st.columns([0.7,0.3])
#            with col3:
#                st.empty()
#                st.text("¿Quieres pasar al mercado minorista de indexado? Aquí: -->")
#            with col4:
#                st.link_button("Telemindex webapp","https://telemindexpy-josevidal.streamlit.app/")
#    with col2:
#        st.empty()

col5,col6,col7=st.columns(3)
with col5:
    st.plotly_chart(graf_ecv_anual_queso())
with col6:
    st.plotly_chart(graf_ecv_mensual())
with col7:
    st.plotly_chart(graf_horaria())
#st.plotly_chart(graf2_año)
#graf1_1=graf_dia()
#st.plotly_chart(graf1_1)
