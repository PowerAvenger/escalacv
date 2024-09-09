import streamlit as st
from backend import download_esios_id
import time
import datetime
from datetime import datetime

#configuación general de la página
st.set_page_config(
    page_title="Escala Cavero Vidal",
    page_icon=":bulb:",
    layout='wide',
)




fecha_hoy=datetime.today().date()

id='600'
fecha_ini='2024-01-01'
fecha_fin='2024-12-31'
agrupacion='hour'

datos, datos_dia, datos_mes, graf_ecv_anual, graf_ecv_anual_queso, graf_ecv_mensual, graf_horaria =download_esios_id(id,fecha_ini,fecha_fin,agrupacion)

ultimo_registro= datos['fecha'].max()
valor_minimo_horario=datos['value'].min()
valor_maximo_diario=datos['value'].max()

valor_medio_diario=round(datos_dia['value'].mean(),2)
valor_minimo_diario=datos_dia['value'].min()
valor_maximo_diario=datos_dia['value'].max()

fecha_min = datos_dia['value'].idxmin().date()
fecha_max = datos_dia['value'].idxmax().date()

#st.write(fecha_descarga)
    

st.write(ultimo_registro) 
#   fecha_descarga=pasar_fecha()
    #st.write(ultima_descarga)




st.title('Escala Cavero-Vidal :copyright:')
st.caption("Basada en los #telepool de Roberto Cavero. Copyright by Jose Vidal :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
st.write("Visita mi página de [PowerAPPs](%s) con un montón de utilidades" % url_apps)

#valor_medio_diario,valor_minimo_diario,valor_maximo_diario=obtener_valores_diarios()
#fecha_min,fecha_max=fechas_minmax()

with st.container():
    col1,col2=st.columns([0.80,0.20])
    with col1:
        st.plotly_chart(graf_ecv_anual)
    with col2:
        st.subheader('Datos en €/MWh',divider='rainbow')
        st.metric('Precio medio diario 2024', value=valor_medio_diario)
        st.metric(f'Precio mínimo diario ( {fecha_min})', value=valor_minimo_diario)
        st.metric(f'Precio máximo diario ({fecha_max})', value=valor_maximo_diario)

col5,col6,col7=st.columns([.25,.4,.35])
with col5:
    st.plotly_chart(graf_ecv_anual_queso)
with col6:
    st.plotly_chart(graf_ecv_mensual)
with col7:
    st.plotly_chart(graf_horaria)
