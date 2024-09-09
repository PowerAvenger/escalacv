# %%
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import streamlit as st
from datetime import datetime

# %%
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
    
    datos_dia=datos.copy()
    datos_dia=datos.reset_index()
    datos_dia=datos.drop(columns=['hora'])
    datos_dia['fecha']=pd.to_datetime(datos['fecha'],format='%d/%m/%Y')
    datos_dia=datos_dia.resample('D').mean()
    datos_dia['value']=datos_dia['value'].round(2)
    datos_dia[['dia','mes','año']]=datos_dia[['dia','mes','año']].astype(int)

    
    datos_mes=datos.copy()
    datos_mes=datos.drop(columns=['fecha','hora', 'dia'])
    datos_mes=datos_mes.resample('M').mean()
    datos_mes['value']=datos_mes['value'].round(2)
    datos_mes[['mes','año']]=datos_mes[['mes','año']].astype(int)


    datos_limites = {
        'rango': [-10,20.01,40.01,60.01,80.01,100.01,10000],
        'valor_asignado': ['muy bajo', 'bajo','medio','alto','muy alto','chungo','xtrem'],
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
        'medio': 'blue',
        'alto': 'orange',
        'muy alto': 'red',
        'chungo': 'purple',
        'xtrem':'black'
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

    datos_dia_queso=datos_dia.groupby(['escala'])['escala'].count()
    datos_dia_queso=datos_dia_queso.reset_index(name='num_dias')

    #grafico principal con los valores diarios
    graf_ecv_anual=px.bar(datos_dia, x='fecha', y='value', 
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada_dia},
        labels={'value':'precio medio diario €/MWh', 'escala':'escala_cv'},
        title="Precios medios del mercado diario OMIE. Año 2024")
    graf_ecv_anual.update_xaxes(
        showgrid=True
    )
    graf_ecv_anual.update_traces(
        marker_line_width=0
    )
    graf_ecv_anual.update_layout(
        title={'x':0.5,'xanchor':'center'}
    )

    #gráfico resumen de medias mensuales
    graf_ecv_mensual=px.bar(datos_mes, x='mes', y='value',
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada_mes},
        labels={'value':'precio medio mensual €/MWh', 'escala':'escala_cv'},
        title="Precios medios mensuales. Año 2024"
        )
    graf_ecv_mensual.update_layout(
        title={'x':0.5,'xanchor':'center'}
    )
    
    graf_ecv_anual_queso=px.pie(datos_dia_queso, values='num_dias', names='escala',
        color='escala',
        color_discrete_map=colores,
        #marker=dict(colors=colores),
        category_orders={'escala':escala_ordenada_dia},
        labels={'num_dias':'num_dias', 'escala':'escala_cv'},
        title="% y número de días según la Escala CV. Año 2024",
        #width=500
        )
    graf_ecv_anual_queso.update_layout(
        title={'x':0.5,'xanchor':'center'}
    )

    #datos para el gráfico de medias horarias
    pt_curva_horaria=datos.pivot_table(
        values='value',
        index='hora'
    )
    pt_curva_horaria=pt_curva_horaria['value'].round(2)
    pt_curva_horaria=pt_curva_horaria.reset_index()

    #grafico con las medias horarias
    graf_horaria=px.scatter(datos_horarios, x='hora',y='value',
        title='Perfil horario. Año 2024',                            
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
        title={'x':0.5,'xanchor':'center'}
    )
    

    
    return datos, datos_dia, datos_mes, graf_ecv_anual, graf_ecv_anual_queso, graf_ecv_mensual, graf_horaria
                       

# %% [markdown]
# ### Gráfico de barras principal

# %% [markdown]
# def graf_ecv_anual():
#     graf_ecv_anual=px.bar(datos_dia, x='fecha', y='value', 
#         color='escala',
#         color_discrete_map=colores,
#         category_orders={'escala':escala_ordenada_dia},
#         labels={'value':'precio medio diario €/MWh', 'escala':'escala_cv'},
#         title="Precios medios del mercado diario OMIE. Año 2024")
#     graf_ecv_anual.update_xaxes(
#         showgrid=True
#     )
#     graf_ecv_anual.update_traces(
#         marker_line_width=0
#     )
# 
#     return graf_ecv_anual

# %% [markdown]
# def graf_ecv_mensual():
#     graf_ecv_mensual=px.bar(datos_mes, x='mes', y='value',
#         color='escala',
#         color_discrete_map=colores,
#         category_orders={'escala':escala_ordenada_mes},
#         labels={'value':'precio medio mensual €/MWh', 'escala':'escala_cv'},
#         title="Precios medios mensuales. Año 2024"
#         )
#     
#     return graf_ecv_mensual

# %% [markdown]
# ### Gráfico de queso

# %% [markdown]
# def graf_ecv_anual_queso():
#     graf_ecv_anual_queso=px.pie(datos_dia_queso, values='num_dias', names='escala',
#         color='escala',
#         color_discrete_map=colores,
#         #marker=dict(colors=colores),
#         category_orders={'escala':escala_ordenada_dia},
#         labels={'num_dias':'num_dias', 'escala':'escala_cv'},
#         title="% y número de días según la Escala CV. Año 2024",
#         #width=500
#         )
#     
#     return graf_ecv_anual_queso

# %% [markdown]
# graf_ecv_anual_queso()

# %% [markdown]
# ### Gráfica horaria anual

# %% [markdown]
# def graf_horaria():
#     graf_horaria=px.scatter(datos_horarios, x='hora',y='value',
#         title='Perfil horario. Año 2024',                            
#         animation_frame='fecha',
#         
#         
#         width=800,
#         labels={'value':'€/MWh'}
#         #category_orders={'escala':escala_ordenada_hora},
#         #color_discrete_map=colores
#         #marker_size=10
#     )
#                            
#     graf_horaria_linea=go.Scatter(
#         x=pt_curva_horaria['hora'],
#         y=pt_curva_horaria['value'],
#         #color=["blue"],
#         name='Media Anual',
#         mode='lines',
#         
#     )
#      
#     graf_horaria.add_trace(graf_horaria_linea)
#         
#     graf_horaria.update_layout(
#         yaxis=dict(
#             range=[datos_horarios['value'].min(), datos_horarios['value'].max()]),
#            
#         
#     )
#     
#     return graf_horaria
# graf_horaria()

# %% [markdown]
# datos_horarios['value'].min()

# %%


# %%
meses = {
        'January': 'Enero',
        'February': 'Febrero',
        'March': 'Marzo',
        'April': 'Abril',
        'May': 'Mayo',
        'June': 'Junio',
        'July': 'Julio',
        'August': 'Agosto',
        'September': 'Septiembre',
        'October': 'Octubre',
        'November': 'Noviembre',
        'December': 'Diciembre'
    }


