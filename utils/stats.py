import matplotlib.pyplot as plt
import seaborn as sns

def calcular_cumulativo(df, columna, nombre_acumulada):
    df = df.sort_values('fecha')
    df[nombre_acumulada] = df[columna].cumsum()
    return df

def descripcion_general(df):
    print(df[['casos', 'fallecidos', 'poblacion']].describe())

def graficar_histograma(df, columna):
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)

    # Histograma de Casos
    sns.histplot(data=df, x=columna, bins=10, color='skyblue')
    plt.title(f"Histograma de {columna.capitalize()}", fontsize=12)
    plt.xlabel(f"Número de {columna.capitalize()}", fontsize=10)
    plt.ylabel("Frecuencia", fontsize=10)
    plt.tight_layout()
    plt.show()

def graficar_categoricos(df):
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, y="nombre_departamento", order=df['nombre_departamento'].value_counts().index)
    plt.title("Frecuencia por Departamento")
    plt.show()

    sns.countplot(data=df, y="nombre_municipio", order=df['nombre_municipio'].value_counts().index[:10])
    plt.title("Top 10 Municipios con Más Registros")
    plt.show()

def rango_intercuartilico(df, columna):
    # Calcular cuartiles y rango intercuartílico
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1

    # Calcular límites para detección de outliers
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    print(f"Columna: {columna}")
    print(f"Q1: {Q1}, Q3: {Q3}")
    print(f"IQR: {IQR}")
    print(f"Límite Inferior: {limite_inferior}, Límite Superior: {limite_superior}\n")

    # Identificar outliers
    outliers = df[(df[columna] < limite_inferior) | (df[columna] > limite_superior)]
    print(f"Outliers encontrados en '{columna}': {len(outliers)} registros\n")

    # Graficar Boxplot
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x=columna, color='skyblue')
    plt.title(f"Boxplot para {columna.capitalize()}")
    plt.xlabel(columna.capitalize())
    plt.show()

def eda_monovariable(df, dfNoLoc):
    print("DESCRIPCION GENERAL")
    descripcion_general(df)
    print("HISTOGRAMAS")
    graficar_histograma(df, 'casos')
    graficar_histograma(dfNoLoc, 'fallecidos')
    graficar_histograma(dfNoLoc, 'fallecidos_acumulado')
    graficar_histograma(df, 'poblacion')
    print("Boxplots, Rango Intercuartilico, Outliers")
    rango_intercuartilico(dfNoLoc, 'casos')
    rango_intercuartilico(dfNoLoc, 'fallecidos')
    rango_intercuartilico(dfNoLoc, 'fallecidos_acumulado')
    rango_intercuartilico(df, 'poblacion')
    print("Categoricos")
    graficar_categoricos(df)

def eda_multivariable(df, dfNoLoc, dfMerge):
    print("Graficas de Dispersion")
    grafica_dispersion(dfNoLoc, 'fallecidos', 'fallecidos_acumulado')
    grafica_dispersion(df, 'casos', 'poblacion')
    grafica_dispersion(df, 'casos_acumulado', 'poblacion')
    print("Graficas Comparativas")
    graficas_comparacion(dfMerge)
    calcular_correlaciones(dfNoLoc)

def graficar_mapa_calor(correlacion, nombre_correlacion):
    # Gráfico de mapa de calor
    plt.figure(figsize=(10, 6))
    sns.heatmap(correlacion, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(f"Mapa de Calor - Correlación de {nombre_correlacion}")
    plt.show()

def calcular_correlaciones(df):
    df = df.select_dtypes(include=['int64', 'float64'])

    print("### Matriz de Correlación de Pearson ###")
    pearson_corr = df.corr(method='pearson')
    print(pearson_corr)

    print("\n### Matriz de Correlación de Spearman ###")
    spearman_corr = df.corr(method='spearman')
    print(spearman_corr)

    #print("\n### Matriz de Correlación de Kendall ###")
    #kendall_corr = df.corr(method='kendall')
    #print(kendall_corr)

    # Gráfico de mapa de calor
    graficar_mapa_calor(pearson_corr, 'Pearson')
    graficar_mapa_calor(spearman_corr, 'Spearman')

def graficas_comparacion(df):
    plt.figure(figsize=(18, 12))

    # 1. Municipios vs cantidad de nuevas muertes
    plt.subplot(3, 2, 1)
    df_agrupado = df.groupby('nombre_municipio')['fallecidos'].sum().sort_values(ascending=False).head(10)
    df_agrupado.plot(kind='bar', color='skyblue')
    plt.title("Top 10 Municipios vs Cantidad de Nuevas Muertes")
    plt.ylabel("Cantidad de Nuevas Muertes")

    # 2. Departamentos vs cantidad de nuevas muertes
    plt.subplot(3, 2, 2)
    df_agrupado = df.groupby('nombre_departamento')['fallecidos'].sum().sort_values(ascending=False)
    df_agrupado.plot(kind='bar', color='orange')
    plt.title("Departamentos vs Cantidad de Nuevas Muertes")
    plt.ylabel("Cantidad de Nuevas Muertes")

    # 3. Municipio vs población
    plt.subplot(3, 2, 3)
    df_agrupado = df.groupby('nombre_municipio')['poblacion'].mean().sort_values(ascending=False).head(10)
    df_agrupado.plot(kind='bar', color='green')
    plt.title("Top 10 Municipios vs Población")
    plt.ylabel("Población")

    # 4. Departamento vs población
    plt.subplot(3, 2, 4)
    df_agrupado = df.groupby('nombre_departamento')['poblacion'].mean().sort_values(ascending=False)
    df_agrupado.plot(kind='bar', color='purple')
    plt.title("Departamentos vs Población")
    plt.ylabel("Población")

    # 5. Municipios vs cantidad de muertes acumuladas
    plt.subplot(3, 2, 5)
    df_agrupado = df.groupby('nombre_municipio')['fallecidos_acumulado'].sum().sort_values(ascending=False).head(10)
    df_agrupado.plot(kind='bar', color='red')
    plt.title("Top 10 Municipios vs Cantidad de Muertes Acumuladas")
    plt.ylabel("Cantidad de Muertes Acumuladas")

    # 6. Departamentos vs cantidad de muertes acumuladas
    plt.subplot(3, 2, 6)
    df_agrupado = df.groupby('nombre_departamento')['fallecidos_acumulado'].sum().sort_values(ascending=False)
    df_agrupado.plot(kind='bar', color='brown')
    plt.title("Departamentos vs Cantidad de Muertes Acumuladas")
    plt.ylabel("Cantidad de Muertes Acumuladas")

    plt.tight_layout()
    plt.show()


def grafica_dispersion(df, columna_x, columna_y):
    plt.figure(figsize=(15, 5))

    # Gráfica 1: Nuevas muertes vs Muertes acumuladas
    plt.subplot(1, 3, 1)
    sns.scatterplot(data=df, x=columna_x, y=columna_y, color='blue')
    plt.title(f"{columna_x} vs {columna_y}")
    plt.xlabel(f"Cantidad de {columna_x}")
    plt.ylabel(f"Cantidad de {columna_y}")
    plt.tight_layout()
    plt.show()

def graficas_dispersion(df):
    plt.figure(figsize=(15, 5))

    # Gráfica 1: Nuevas muertes vs Muertes acumuladas
    plt.subplot(1, 3, 1)
    sns.scatterplot(data=df, x='nuevas_muertes', y='muertes_acumuladas', color='blue')
    plt.title("Nuevas Muertes vs Muertes Acumuladas")
    plt.xlabel("Cantidad de Nuevas Muertes")
    plt.ylabel("Cantidad de Muertes Acumuladas")

    # Gráfica 2: Nuevas muertes vs Población
    plt.subplot(1, 3, 2)
    sns.scatterplot(data=df, x='nuevas_muertes', y='poblacion', color='green')
    plt.title("Nuevas Muertes vs Población")
    plt.xlabel("Cantidad de Nuevas Muertes")
    plt.ylabel("Población de Municipios")

    # Gráfica 3: Muertes acumuladas vs Población
    plt.subplot(1, 3, 3)
    sns.scatterplot(data=df, x='muertes_acumuladas', y='poblacion', color='orange')
    plt.title("Muertes Acumuladas vs Población")
    plt.xlabel("Cantidad de Muertes Acumuladas")
    plt.ylabel("Población de Municipios")

    plt.tight_layout()
    plt.show()

def eda_monovariable_e(df, dfNoLoc):
    # Histograma de Fallecidos
    sns.histplot(data=dfNoLoc, x='fallecidos', bins=30, color='orange', ax=axes[1])
    axes[1].set_title("Histograma de Fallecidos", fontsize=12)
    axes[1].set_xlabel("Número de Fallecidos", fontsize=10)
    axes[1].set_ylabel("Frecuencia", fontsize=10)

    # Histograma de Población
    sns.histplot(data=df, x='poblacion', bins=10, color='green', ax=axes[2])
    axes[2].set_title("Histograma de Población", fontsize=12)
    axes[2].set_xlabel("Tamaño de la Población", fontsize=10)
    axes[2].set_ylabel("Frecuencia", fontsize=10)

    plt.tight_layout()
    plt.show()

    # Diagramas de Caja
    for col in ['casos', 'poblacion']:
        sns.boxplot(data=df, x=col)
        plt.title(f"Diagrama de Caja para {col.capitalize()}")
        plt.show()

    for col in ['fallecidos']:
        sns.boxplot(data=dfNoLoc, x=col)
        plt.title(f"Diagrama de Caja para {col.capitalize()}")
        plt.show()

def histograma_casos(df):
    plt.figure(figsize=(24, 6))

    # Histograma de casos por municipio
    plt.subplot(1, 2, 1)
    sns.histplot(data=df, x='nombre_municipio', weights='casos',
                 multiple='stack', shrink=0.8, color='skyblue')
    plt.xticks(rotation=90, fontsize=4)
    plt.title("Histograma de Casos por Municipio")
    plt.xlabel("Municipio")
    plt.ylabel("Número de Casos")

    # Histograma de casos por departamento
    plt.subplot(1, 2, 2)
    sns.histplot(data=df, x='nombre_departamento', weights='casos',
                 multiple='stack', shrink=0.8, color='orange')
    plt.xticks(rotation=90)
    plt.title("Histograma de Casos por Departamento")
    plt.xlabel("Departamento")
    plt.ylabel("Número de Casos")

    #plt.tight_layout()
    plt.show()
