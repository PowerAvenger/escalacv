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

# %%
datos_dia=datos.resample('D').mean()
datos_dia

# %%
datos_dia['value']=datos_dia['value'].round(2)
datos_dia

# %%
valor_minimo_diario=datos_dia['value'].min()
valor_maximo_diario=datos_dia['value'].max()
valor_minimo_diario,valor_maximo_diario

# %%
def graf_año():
    graf_año=px.line(datos_dia, x='fecha', y='value')
    return graf_año

# %%
graf_año()

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
colores = {
    'muy bajo': 'dark green',
    'bajo': 'green',
    'medio': 'blue',
    'alto': 'orange',
    'muy alto': 'red',
    'chungo': 'purple'
}

# %%
datos_dia['color']=datos_dia['escala'].map(colores)
datos_dia

# %%
escala_ordenada= ['muy bajo', 'bajo','medio','alto','muy alto','chungo']
datos_dia['escala']=pd.Categorical(datos_dia['escala'],categories=escala_ordenada, ordered=True)
datos_dia

# %%
def graf_ecv_anual():
    graf_ecv_anual=px.bar(datos_dia, x='fecha', y='value', 
        color='escala',
        color_discrete_map=colores,
        category_orders={'escala':escala_ordenada},
        labels={'value':'precio medio diario €/MWh', 'escala':'escala_cv'},
        title="Precios medios del mercado diario OMIE. Año 2024")
    graf_ecv_anual.update_xaxes(
        #tickmode='array',
        #tickvals=pd.date_range(start='2024-01-01', periods=20, freq='MS'),  # Marcas mensuales
        #ticktext=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        showgrid=True
    )
    graf_ecv_anual.update_traces(
        marker_line_width=0
    )

    return graf_ecv_anual

# %%
graf_ecv_anual()

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



