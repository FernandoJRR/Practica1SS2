import pandas as pd
import os
from utils.downloader import download_csv_from_url
from source.database import obtener_conexion

url_casos_globales = "https://drive.google.com/uc?export=download&id=1V-vFNkkYiSPQClASZeKx-cTvwlE5tOFD"
path_casos_locales = os.path.join(os.path.dirname(__file__), 'data', 'municipio.csv')
anio = 2020

if __name__ == "__main__":
    #Se obtiene el archivo global
    print("Descargando archivo CSV Global")
    csv_file = download_csv_from_url(url_casos_globales)
    print("Archivo descargado")
    print("Leyendo archivo CSV Global")
    dfGlobal = pd.read_csv(csv_file)

    #Se limpia el archivo global
    print("Limpiando archivo CSV Global")
    #Se quitan las columnas innecesarias
    dfGlobal = dfGlobal.drop(columns=["Country", "WHO_region", "Cumulative_cases", "Cumulative_deaths"])

    #Se filtra para dejar solo los reigstros de Guatemala
    dfGlobal = dfGlobal[dfGlobal['Country_code'] == 'GT']

    #Se quita la columna despues de filtrar
    dfGlobal = dfGlobal.drop(columns=["Country_code"])

    #Se quitan los duplicados
    dfGlobal = dfGlobal.drop_duplicates()

    print("Transformando archivo CSV Global")
    #Se convierten las fechas a su tipo adecuado
    #Las fechas XX se convierten a 20XX
    dfGlobal['Date_reported'] = dfGlobal['Date_reported'].apply(lambda x: x if len(x.split('/')[-1]) == 4 else x[:-2] + '20' + x[-2:])
    dfGlobal['Date_reported'] = pd.to_datetime(dfGlobal['Date_reported'], format='%m/%d/%Y', errors='coerce')
    #Se quitan las filas que tienen NaT
    dfGlobal = dfGlobal[dfGlobal['Date_reported'].notna()]

    #Se filtran los resultados solo para el anio que se quiera
    dfGlobal = dfGlobal[dfGlobal['Date_reported'].dt.year == anio]

    dfGlobal = pd.DataFrame({
        'fecha': dfGlobal['Date_reported'],
        'casos': dfGlobal['New_cases'],
        'fallecidos': dfGlobal['New_deaths'],
        'codigo_municipio': None,
        'municipio': None,
        'codigo_departamento': None,
        'departamento': None,
        'poblacion': None
    })

    print("Obteniendo y leyendo archivo CSV Local")
    #Se obtiene el archivo local
    dfLocal = pd.read_csv(path_casos_locales)

    print("Limpiando y transformando archivo CSV Local")
    #Se eliminan los duplicados
    dfLocal = dfLocal.drop_duplicates()

    # Reestructurar el datalocal para adaptarlo a las necesidades del modelo de datos
    dfLocal = dfLocal.melt(
        id_vars=['departamento', 'codigo_departamento', 'municipio', 'codigo_municipio', 'poblacion'],
        var_name='fecha', value_name='casos'
    )

    dfLocal['fecha'] = pd.to_datetime(dfLocal['fecha'], format='%m/%d/%Y', errors='coerce')
    dfLocal['fallecidos'] = 0

    print("Unificando Dataframes")
    dfCombinado = pd.concat([dfLocal, dfGlobal], ignore_index=True)


    print(dfGlobal.head())
    print(dfLocal.head(10))
    print(dfCombinado.head(20))
    print(dfCombinado.shape)