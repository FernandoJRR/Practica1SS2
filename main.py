import pandas as pd
import os
from utils.downloader import download_csv_from_url
from source.database import crear_tablas, insertar_datos, drop_registros

url_casos_globales = "https://drive.google.com/uc?export=download&id=1V-vFNkkYiSPQClASZeKx-cTvwlE5tOFD"
path_casos_locales = os.path.join(os.path.dirname(__file__), 'data', 'municipio.csv')
anio = 2020

def validar_tipos_columnas(df, tipos):
    for columna, tipo in tipos.items():
        if columna in df.columns:
            df = df[df[columna].apply(lambda x: isinstance(x, tipo))]
    return df

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

    #Se eliminan los municipios no registrados
    dfLocal = dfLocal[dfLocal['codigo_municipio'] != 0]

    # Crear un diccionario con el primer ID encontrado para cada departamento
    id_departamentos_unicos = dfLocal.groupby('departamento')['codigo_departamento'].first().to_dict()
    # Actualizar el DataFrame con el ID correcto
    dfLocal['codigo_departamento'] = dfLocal['departamento'].map(id_departamentos_unicos)

    # Reestructurar el datalocal para adaptarlo a las necesidades del modelo de datos
    dfLocal = dfLocal.melt(
        id_vars=['departamento', 'codigo_departamento', 'municipio', 'codigo_municipio', 'poblacion'],
        var_name='fecha', value_name='casos'
    )

    #Las fechas XX se convierten a 20XX
    dfLocal['fecha'] = dfLocal['fecha'].apply(lambda x: x if len(x.split('/')[-1]) == 4 else x[:-2] + '20' + x[-2:])
    dfLocal['fecha'] = pd.to_datetime(dfLocal['fecha'], format='%m/%d/%Y', errors='coerce')
    dfLocal['fallecidos'] = 0

    print("Unificando Dataframes")
    dfCombinado = pd.concat([dfLocal, dfGlobal], ignore_index=True)
    dfCombinado['casos'] = pd.to_numeric(dfCombinado['casos'], errors='coerce').astype('Int64')
    dfCombinado['fallecidos'] = pd.to_numeric(dfCombinado['fallecidos'], errors='coerce').astype('Int64')
    dfCombinado = dfCombinado[dfCombinado['casos'].notnull()]
    dfCombinado = dfCombinado[dfCombinado['fallecidos'].notnull()]
    dfCombinado.dropna()
    print(dfCombinado.info())

    print(dfCombinado.tail(10))
    print("Se prepara la base de datos")
    print("Se crean las tablas si no existen")
    crear_tablas()
    print("Drop a todos los registros")
    drop_registros()
    print("Insertando registros")
    insertar_datos(dfCombinado)