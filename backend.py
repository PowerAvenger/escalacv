# %%
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import streamlit as st
import numpy as np
from datetime import datetime

# %%
@st.cache_data(ttl=100)
def download_esios_id(id,fecha_ini,fecha_fin,agrupacion):
                       
    token = st.secrets['ESIOS_API_KEY']
    cab = dict()
    cab ['x-api-key']= token
    url_id = 'https://api.esios.ree.es/indicators'
    url=f'{url_id}/{id}?geo_ids[]=3&start_date={fecha_ini}T00:00:00&end_date={fecha_fin}T23:59:59&time_trunc={agrupacion}'
    print(url)
    datos_origen = requests.get(url, headers=cab).json()
    
    #arreglamos los datos origen    
    datos=pd.DataFrame(datos_origen['indicator']['values'])
    datos = (datos
        .assign(datetime=lambda vh_: pd #formateamos campo fecha, desde un str con diferencia horaria a un naive
            .to_datetime(vh_['datetime'],utc=True)  # con la fecha local
            .dt
            .tz_convert('Europe/Madrid')
            .dt
            .tz_localize(None)
        )   
        .loc[:,['datetime','value']]
    )
    datos['fecha']=datos['datetime'].dt.date
    datos['hora']=datos['datetime'].dt.hour
    datos['dia']=datos['datetime'].dt.day
    datos['mes']=datos['datetime'].dt.month
    datos['año']=datos['datetime'].dt.year
    datos.set_index('datetime', inplace=True)
    
    #creamos df con las medias diarias
    datos_dia=datos.copy()
   
    #datos_dia=datos.reset_index()
    datos_dia=datos.drop(columns=['hora'])
    datos_dia['fecha']=pd.to_datetime(datos['fecha'],format='%d/%m/%Y')
    meses_español = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
                 7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}
    datos_dia['mes_nombre']=datos_dia['mes'].map(meses_español)
    datos_dia=datos_dia.groupby('fecha').agg({
        
        'value':'mean',
        'dia':'first',
        'mes':'first',
        'año':'first',
        'mes_nombre':'first'

    })
    #datos_dia=datos_dia.resample('D').mean()
    datos_dia['value']=datos_dia['value'].round(2)
    datos_dia[['dia','mes','año']]=datos_dia[['dia','mes','año']].astype(int)
    datos_dia.reset_index(inplace=True)
    #print (datos_dia)

    
    
    #calculams medias mensuales
    datos_mes=datos_dia.copy()
    datos_mes=datos_dia.drop(columns=['fecha', 'dia'])
    datos_mes=datos_mes.groupby('mes').agg({
        'value':'mean',
        'año':'first',
        'mes_nombre':'first'
    }).reset_index()
    datos_mes['value']=datos_mes['value'].round(2)
    datos_mes[['mes','año']]=datos_mes[['mes','año']].astype(int)
    
    media_mensual=round(datos_dia['value'].mean(),2)
    
    df_fila_espacio = pd.DataFrame({'mes': [None], 'value': [0], 'año': [None], 'mes_nombre': ['']})
    df_fila_media=pd.DataFrame({'mes': [13],'value':[media_mensual],'año':['2024'],'mes_nombre':['media']})
    datos_mes=pd.concat([datos_mes, df_fila_espacio, df_fila_media], ignore_index=True)
    print(datos_mes)
    
    # definimos escala en rango y color
    datos_limites = {
        'rango': [-10, 20.01, 40.01, 60.01, 80.01, 100.01, 120.01, 140.01, 10000], #9 elementos
        'valor_asignado': ['muy bajo', 'bajo', 'medio', 'alto', 'muy alto', 'chungo', 'xtrem', 'defcon3', 'defcon2'],
    }
    df_limites=pd.DataFrame(datos_limites)
    etiquetas = df_limites['valor_asignado'][:-1]
    datos_horarios=datos.copy()
    datos_horarios['escala']=pd.cut(datos_horarios['value'],bins=df_limites['rango'],labels=etiquetas,right=True)
    lista_escala=datos_horarios['escala'].unique()
    datos_dia['escala']=pd.cut(datos_dia['value'],bins=df_limites['rango'],labels=etiquetas,right=False)
    datos_mes['escala']=pd.cut(datos_mes['value'],bins=df_limites['rango'],labels=etiquetas,right=False)

    colores = {
        'muy bajo': 'lightgreen',
        'bajo': 'green',
        #'medio': 'blue',
        'medio': '#24d4ff',
        #'alto': 'orange',
        'alto': '#004280',
        #'muy alto': 'red',
        'muy alto': 'orange',
        #'chungo': 'purple',
        'chungo': 'red',
        #'xtrem':'black',
        'xtrem':'darkred',
        'defcon3': 'purple',
        'defcon2': 'purple',
    }

    datos_horarios['color']=datos_horarios['escala'].map(colores)
    datos_dia['color']=datos_dia['escala'].map(colores)

    valor_asignado_a_rango = {row['valor_asignado']: row['rango'] for _, row in df_limites.iterrows()}
    escala_horaria=['alto', 'medio', 'bajo', 'muy bajo', 'muy alto', 'chungo']
    escala_ordenada_hora = sorted(escala_horaria, key=lambda x: valor_asignado_a_rango[x], reverse=True)
    datos_horarios['escala']=pd.Categorical(datos_horarios['escala'],categories=escala_ordenada_hora, ordered=True)
    escala_dia=datos_dia['escala'].unique()
    escala_ordenada_dia = sorted(escala_dia, key=lambda x: valor_asignado_a_rango[x], reverse=True)
    datos_mes['color']=datos_mes['escala'].map(colores)
    escala_mes= datos_mes['escala'].unique()
    escala_ordenada_mes = sorted(escala_mes, key=lambda x: valor_asignado_a_rango[x], reverse=True)
    datos_dia['escala']=pd.Categorical(datos_dia['escala'],categories=escala_ordenada_dia, ordered=True)
    datos_mes['escala']=pd.Categorical(datos_mes['escala'],categories=escala_ordenada_mes, ordered=True)
    #print(datos_mes)

    datos_dia_queso=datos_dia.groupby(['escala'])['escala'].count()
    datos_dia_queso=datos_dia_queso.reset_index(name='num_dias')
    print (datos_dia_queso)

    #GRÁFICO PRINCIPAL CON LOS PRECIOS MEDIOS DIARIOS DEL AÑO. ecv es escala cavero vidal-----------------------------------------------------------
    graf_ecv_anual=px.bar(datos_dia, x='fecha', y='value', 
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada_dia},
        labels={'fecha':'fecha','value':'precio medio diario €/MWh', 'escala':'escala_cv'},
        title= f'Precios medios del mercado diario OMIE. Año {st.session_state.año_seleccionado}',
        hover_name='escala'
    )

    graf_ecv_anual.update_xaxes(
        tickformat="%b",  # Mostrar sólo el mes abreviado (Ej: Jan, Feb)
        tickvals=pd.date_range(
            start=datos_dia['fecha'].min(),
            end=datos_dia['fecha'].max(),
            freq='MS'  # Generar ticks al inicio de cada mes
        ),
        showgrid=True
    )

    graf_ecv_anual.update_traces(
        marker_line_width=0,
        customdata=datos_dia['escala'],
        hovertemplate=(
            #"<b>Escala:</b> %{customdata}<br>"
            "<b>Fecha:</b> %{x|%d-%m-%Y}<br>"  # Formato DD-MM-YYYY
            "<b>Precio:</b> %{y:.2f} €/MWh<br>"
        )
    )

    ymax=datos_dia['value'].max()
    graf_ecv_anual.update_layout(
        title={'x':0.5,'xanchor':'center'},
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                bgcolor='rgba(173, 216, 230, 0.5)'
            ),  
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(step="all")  # Visualizar todos los datos
                ]),
            ),
        ),
        yaxis=dict(
            range=[0, ymax],             # Forzar el rango del eje Y
            tickmode="linear",            # Escala lineal
            tick0=0,                      # Comenzar en 0
            dtick=20                      # Incrementos de 20
        ),
    )
    graf_ecv_anual.update_xaxes(
        showgrid=True
    )
    

    print(datos_mes)

    #GRAFICO DE BARRAS CON MEDIAS MENSUALES------------------------------------------------------------------------------------------------------------
    graf_ecv_mensual=px.bar(datos_mes, x='mes_nombre', y='value',
        color='escala',
        color_discrete_map=colores,
        #category_orders={'escala':escala_ordenada_mes},
        category_orders={'mes_nombre':datos_mes['mes_nombre'],
                         'escala':escala_ordenada_mes},
        labels={'value':'€/MWh', 'escala':'escala_cv','mes_nombre':'mes'},
        title=f'Precios medios mensuales. Año {st.session_state.año_seleccionado}',
        text='value'

        )
    graf_ecv_mensual.update_layout(
        title={'x':0.5,'xanchor':'center'}
    )
    graf_ecv_mensual.add_trace(go.Scatter(
        x=datos_mes['mes_nombre'],
        y=[media_mensual]*len(datos_mes),
        mode='lines',
        line=dict(color='yellow',width=2, dash='dash'),
        name='media'
    ))
    
    #GRÁFICO DE QUESITOS------------------------------------------------------------------------------------------------------------------------------
    graf_ecv_anual_queso=px.pie(datos_dia_queso, values='num_dias', names='escala',
        color='escala',
        color_discrete_map=colores,
        hole=.4,
        category_orders={'escala':escala_ordenada_dia},
        labels={'num_dias':'num_dias', 'escala':'escala_cv'},
        title=f'% y número de días según la Escala CV. Año {st.session_state.año_seleccionado}',
        #width=500
    )
    graf_ecv_anual_queso.update_layout(
        title={'x':0.5,'xanchor':'center'},
    )

    #datos para el gráfico de medias horarias
    pt_curva_horaria=datos.pivot_table(
        values='value',
        index='hora'
    )
    pt_curva_horaria=pt_curva_horaria['value'].round(2)
    pt_curva_horaria=pt_curva_horaria.reset_index()

    #grafico con las medias horarias---------------------------------------------------------------------------------------------------------------
    graf_horaria=px.scatter(datos_horarios, x='hora',y='value',
        title=f'Perfil horario. Año {st.session_state.año_seleccionado}',                            
        animation_frame='fecha',
        
        
        width=800,
        labels={'value':'€/MWh'}
        #category_orders={'escala':escala_ordenada_hora},
        #color_discrete_map=colores
        #marker_size=10
    )
                           
    graf_horaria_linea=go.Scatter(
        x=pt_curva_horaria['hora'],
        y=pt_curva_horaria['value'],
        #color=["blue"],
        name='Media Anual',
        mode='lines',
        
    )
     
    graf_horaria.add_trace(graf_horaria_linea)
        
    graf_horaria.update_layout(
        yaxis=dict(
            range=[datos_horarios['value'].min(), datos_horarios['value'].max()]),
        title={'x':0.5,'xanchor':'center'},
        legend=dict(
                orientation="h",  # Leyenda en horizontal
                x=0.5,  # Posición horizontal centrada
                xanchor="center",  # Alineación horizontal centrada
                y=1,  # Colocarla ligeramente por encima del gráfico
                yanchor="top",  # Alineación vertical en la parte inferior de la leyenda
                
                
                
            )
        )
    
    #GRÁFICO DE LOS PRECIOS MEDIOS DIARIOS PERO CON DESGLOSE POR MESES-----------------------------------------------------------------------
    graf_ecv_anual_meses=px.bar(datos_dia, x='dia', y='value', 
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada_dia},
        labels={'value':'€/MWh', 'escala':'escala_cv'},
        title=f'Precios medios del mercado diario OMIE. Año {st.session_state.año_seleccionado}. Por meses.',
        facet_col='mes_nombre',
        facet_col_wrap=4


        )
    # Configurar layout y eliminar prefijos en títulos de facetas
    graf_ecv_anual_meses.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    meses_ordenados = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    

    graf_ecv_anual_meses.update_xaxes(
        showgrid=True,
        #tickformat="%d",
    )
    graf_ecv_anual_meses.update_traces(
        marker_line_width=0
    )
    graf_ecv_anual_meses.update_layout(
        title={'x':0.5,'xanchor':'center'},
        height=800,
        yaxis=dict(
            range=[0, ymax],             # Forzar el rango del eje Y
            tickmode="linear",            # Escala lineal
            tick0=0,                      # Comenzar en 0
            dtick=20                      # Incrementos de 20
        ),
        
    )
    
    return datos, datos_dia, datos_mes, graf_ecv_anual, graf_ecv_anual_queso, graf_ecv_mensual, graf_horaria, graf_ecv_anual_meses


    

