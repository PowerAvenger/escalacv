# %%
import requests
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# %%
def download_esios_id(id,fecha_ini,fecha_fin,agrupacion):
                       token = '496b263791ef0dcaf80b803b47b332a13b01f2c2352e018b624c7a36a0eaffc0'
                       cab = dict()
                       cab ['x-api-key']= token
                       url_id = 'https://api.esios.ree.es/indicators'
                       url=f'{url_id}/{id}?geo_ids[]=3&start_date={fecha_ini}T00:00:00&end_date={fecha_fin}T23:59:59&time_trunc={agrupacion}'
                       print(url)
                       response = requests.get(url, headers=cab).json()
                       

                       return response
                       

# %%
id='600'
fecha_ini='2024-01-01'
fecha_fin='2024-12-31'
agrupacion='hour'

# %%
datos_origen =download_esios_id(id,fecha_ini,fecha_fin,agrupacion)


# %%
datos=pd.DataFrame(datos_origen['indicator']['values'])
datos

# %%
datos = (datos
         .assign(datetime=lambda vh_: pd #formateamos campo fecha, desde un str con diferencia horaria a un naive
                      .to_datetime(vh_['datetime'],utc=True)  # con la fecha local
                      .dt
                      .tz_convert('Europe/Madrid')
                      .dt
                      .tz_localize(None)
                ) 
             #.drop(['datetime','datetime_utc','tz_time','geo_id','geo_name'],
             #      axis=1) #eliminamos campos
             
             .loc[:,['datetime','value']]
             )

datos

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

# %%
datos['fecha']=datos['datetime'].dt.strftime('%d/%m/%Y')
datos['fecha']=pd.to_datetime(datos['fecha'],format='%d/%m/%Y')
datos['hora']=datos['datetime'].dt.hour
datos['dia']=datos['datetime'].dt.day
datos['mes']=datos['datetime'].dt.month
datos['año']=datos['datetime'].dt.year
#datos['mes_nombre']=datos['datetime'].dt.month_name()
#datos['mes_nombre'] = datos['mes_nombre'].map(meses)

datos.set_index('datetime', inplace=True)
datos

# %% [markdown]
# ### Agrupación por días

# %%
datos_dia=datos.resample('D').mean()
datos_dia['value']=datos_dia['value'].round(2)
datos_dia=datos_dia.drop(columns=['hora'])
datos_dia[['dia','mes','año']]=datos_dia[['dia','mes','año']].astype(int)
datos_dia

# %%
valor_minimo_diario=datos_dia['value'].min()
valor_maximo_diario=datos_dia['value'].max()
valor_minimo_diario,valor_maximo_diario

# %% [markdown]
# ### Agrupación por meses

# %%
datos_mes=datos.resample('M').mean()
datos_mes['value']=datos_mes['value'].round(2)
datos_mes=datos_mes.drop(columns=['fecha','hora', 'dia'])
datos_mes[['mes','año']]=datos_mes[['mes','año']].astype(int)
datos_mes

# %% [markdown]
# def graf_año():
#     graf_año=px.line(datos_dia, x='fecha', y='value')
#     return graf_año

# %% [markdown]
# ### Definimos la escala y sus límites

# %%
datos_limites = {
    'rango': [-10,20,40,60,80,100,120],
    'valor_asignado': ['muy bajo', 'bajo','medio','alto','muy alto','chungo','xtrem'],
}

# %%
df_limites=pd.DataFrame(datos_limites)
df_limites

# %%
etiquetas = df_limites['valor_asignado'][:-1]

# %%
datos_dia['escala']=pd.cut(datos_dia['value'],bins=df_limites['rango'],labels=etiquetas,right=False)
datos_dia

# %%
datos_mes['escala']=pd.cut(datos_mes['value'],bins=df_limites['rango'],labels=etiquetas,right=False)
datos_mes

# %% [markdown]
# ### Definimos los colores según la escala

# %%
colores = {
    'muy bajo': 'lightgreen',
    'bajo': 'green',
    'medio': 'blue',
    'alto': 'orange',
    'muy alto': 'red',
    'chungo': 'purple'
}

# %%
datos_dia['color']=datos_dia['escala'].map(colores)
datos_dia

# %% [markdown]
# ### Obtenemos la escala ordenada al reves para el gráfico diario

# %%
escala_dia=datos_dia['escala'].unique()
escala_dia

# %%
valor_asignado_a_rango = {row['valor_asignado']: row['rango'] for _, row in df_limites.iterrows()}

# %%
escala_ordenada_dia = sorted(escala_dia, key=lambda x: valor_asignado_a_rango[x], reverse=True)
escala_ordenada_dia

# %%
datos_mes['color']=datos_mes['escala'].map(colores)
datos_mes

# %% [markdown]
# ### Obtenemos la escala ordenada al reves para el gráfico mensual

# %%
escala_mes= datos_mes['escala'].unique()
escala_mes

# %%
escala_ordenada_mes = sorted(escala_mes, key=lambda x: valor_asignado_a_rango[x], reverse=True)
escala_ordenada_mes

# %% [markdown]
# ### Esta tabla se usa para el gráfico grande de barras diario

# %%

datos_dia['escala']=pd.Categorical(datos_dia['escala'],categories=escala_ordenada_dia, ordered=True)
datos_dia

# %% [markdown]
# ### Estos datos se usan para el grafico de barras mensual

# %%
datos_mes['escala']=pd.Categorical(datos_mes['escala'],categories=escala_ordenada_mes, ordered=True)
datos_mes

# %% [markdown]
# ### Estos datos se usan para el quesito

# %%
datos_dia_queso=datos_dia.groupby(['escala'])['escala'].count()
datos_dia_queso=datos_dia_queso.reset_index(name='num_dias')
datos_dia_queso


# %% [markdown]
# ### Gráfico de barras principal

# %%
def graf_ecv_anual():
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

    return graf_ecv_anual

# %%
graf_ecv_anual()

# %%
def graf_ecv_mensual():
    graf_ecv_mensual=px.bar(datos_mes, x='mes', y='value',
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada_mes},
        labels={'value':'precio medio mensual €/MWh', 'escala':'escala_cv'},
        title="Precios medios mensuales. Año 2024"
        )
    #graf_ecv_mensual.update_xaxes(
    #    showgrid=True
    
    #graf_ecv_mensual.update_traces(
    #   marker_line_width=0
    #)

    return graf_ecv_mensual

# %%
graf_ecv_mensual()

# %% [markdown]
# ### Gráfico de queso

# %%
def graf_ecv_anual_queso():
    graf_ecv_anual_queso=px.pie(datos_dia_queso, values='num_dias', names='escala',
        color='escala',
        color_discrete_map=colores,
        #marker=dict(colors=colores),
        category_orders={'escala':escala_ordenada_dia},
        labels={'num_dias':'num_dias', 'escala':'escala_cv'},
        title="% y número de días según la Escala CV. Año 2024",
        width=500
        )
    #graf_ecv_anual_queso.update_traces(hoverlabel=dict(font_color='white', bgcolor='blue'))
    #graf_ecv_anual.update_xaxes(
        #tickmode='array',
        #tickvals=pd.date_range(start='2024-01-01', periods=20, freq='MS'),  # Marcas mensuales
        #ticktext=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    #    showgrid=True
    #)
    #graf_ecv_anual.update_traces(
    #    marker_line_width=0
    #)

    return graf_ecv_anual_queso

# %%
graf_ecv_anual_queso()

# %% [markdown]
# ### Gráfica horaria anual

# %%
datos

# %%
pt_curva_horaria=datos.pivot_table(
    values='value',
    index='hora'
)
pt_curva_horaria=pt_curva_horaria['value'].round(2)
pt_curva_horaria=pt_curva_horaria.reset_index()


# %%
pt_curva_horaria

# %%
def graf_horaria():
    graf_horaria=px.line(pt_curva_horaria,x='hora',y='value',
                     title="Precios medios horarios",
                     labels={'value': '€/MWh'},
                     width=800
    )
    return graf_horaria
graf_horaria()

# %%
mes=1
filtro_mes=datos['mes']==mes
datos_filtrados=datos[filtro_mes]
filtro_mes

# %%
datos_filtrados

# %%
#datos_filtrados.set_index('datetime', inplace=True)
#datos_filtrados

# %%
datos_filtrados.dtypes

# %%
datos_filtrados_dia=datos_filtrados.resample('D').mean()
datos_filtrados_dia

# %%


# %%


# %%
def graf_dia():
    graf_dia=px.line(datos_filtrados_dia,x='fecha',y='value')
    
    return graf_dia

# %%
graf_dia()

# %%



