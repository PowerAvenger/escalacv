import streamlit as st
#from streamlit_plotly_events import plotly_events
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

datos, datos_dia, datos_mes, graf_ecv_anual, graf_ecv_anual_queso, graf_ecv_mensual, graf_horaria, graf_ecv_anual_meses = download_esios_id(id,fecha_ini,fecha_fin,agrupacion)

ultimo_registro= datos['fecha'].max()
valor_minimo_horario=datos['value'].min()
valor_maximo_diario=datos['value'].max()

valor_medio_diario=round(datos_dia['value'].mean(),2)
valor_minimo_diario=datos_dia['value'].min()
valor_maximo_diario=datos_dia['value'].max()

#fecha_min = datos_dia['value'].idxmin().date()
fecha_min = datos_dia.loc[datos_dia['value'].idxmin(), 'fecha'].date()
#fecha_max = datos_dia['value'].idxmax().date()
fecha_max = datos_dia.loc[datos_dia['value'].idxmax(), 'fecha'].date()
    

st.write(ultimo_registro) 
#   fecha_descarga=pasar_fecha()
    #st.write(ultima_descarga)




st.title('Escala Cavero-Vidal©')
st.caption("Basada en los #telepool de Roberto Cavero. Copyright by Jose Vidal :ok_hand:")
url_apps = "https://powerappspy-josevidal.streamlit.app/"
st.write("Visita mi página de [ePowerAPPs](%s) con un montón de utilidades" % url_apps)


with st.container():
    col1,col2,col3=st.columns([0.7,0.1,0.2])
    with col1:
        st.plotly_chart(graf_ecv_anual)
    with col2:
        st.subheader('Datos en €/MWh',divider='rainbow')
        st.metric('Precio medio diario 2024', value=valor_medio_diario)
        st.metric(f'Precio mínimo diario ( {fecha_min})', value=valor_minimo_diario)
        st.metric(f'Precio máximo diario ({fecha_max})', value=valor_maximo_diario)
    with col3:
        st.plotly_chart(graf_ecv_anual_queso)

col5,col6,col7=st.columns([.4,.35,.25])

with col5:
    st.plotly_chart(graf_ecv_mensual)
with col6:
    st.plotly_chart(graf_horaria)


# Detección de clic en el gráfico de facetas
#evento=st.plotly_chart(graf_ecv_anual_meses, use_container_width=True, on_select='rerun') #selection_mode='points'
#evento=plotly_events(graf_ecv_anual_meses)
#evento.selection
st.plotly_chart(graf_ecv_anual_meses)