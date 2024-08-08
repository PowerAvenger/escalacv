import streamlit as st
from backend import graf_ecv_anual, graf_ecv_anual_queso, graf_ecv_mensual, graf_horaria,obtener_valores_diarios,fechas_minmax,ultimo_registro,pasar_fecha
import time
import datetime
from datetime import datetime

st.set_page_config(
    page_title="Escala Cavero Vidal",
    page_icon=":bulb:",
    layout='wide',
)

ultimo_registro=ultimo_registro()
st.write(ultimo_registro) 
ultima_descarga=pasar_fecha()
st.write(ultima_descarga)
st.title('Escala Cavero-Vidal :copyright:')
st.caption("Basada en los #telepool de Roberto Cavero. Copyright by Jose Vidal :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
st.write("Visita mi página de [PowerAPPs](%s) con un montón de utilidades" % url_apps)

valor_medio_diario,valor_minimo_diario,valor_maximo_diario=obtener_valores_diarios()
fecha_min,fecha_max=fechas_minmax()

with st.container():
    col1,col2=st.columns([0.80,0.20])
    with col1:
        st.plotly_chart(graf_ecv_anual())
    with col2:
        st.subheader('Datos en €/MWh',divider='rainbow')
        st.metric('Precio medio diario 2024', value=valor_medio_diario)
        st.metric(f'Precio mínimo diario ( {fecha_min})', value=valor_minimo_diario)
        st.metric(f'Precio máximo diario ({fecha_max})', value=valor_maximo_diario)

col5,col6,col7=st.columns([.25,.4,.35])
with col5:
    st.plotly_chart(graf_ecv_anual_queso())
with col6:
    st.plotly_chart(graf_ecv_mensual())
with col7:
    st.plotly_chart(graf_horaria())
