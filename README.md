# Practica 1 - Seminario de Sistemas 2
### Por: Fernando Rodriguez - 202030542 - 3696417440901
## Descripción General

Este proyecto consiste en la limpieza, procesamiento y carga de datos en una base de datos PostgreSQL utilizando SQLAlchemy y Pandas. El propósito principal es manejar datos relacionados con registros de casos de municipios en Guatemala, asegurando la integridad de los datos mediante validaciones y manejo de errores durante el proceso de inserción.
## Tecnologías Utilizadas

    Python 3.9+
    PostgreSQL
    SQLAlchemy
    Pandas

## Proceso de Limpieza de Datos

Durante el proceso de limpieza de datos, se siguieron los siguientes pasos para asegurar la calidad de la información antes de su inserción en la base de datos:

- Conversión de Tipos de Datos:
        Las columnas críticas se convirtieron a tipos int64, string y datetime.
        Las filas con errores de conversión se eliminaron automáticamente para evitar inconsistencias.

- Eliminación de Valores Inválidos:
        Se eliminaron registros donde codigo_departamento, codigo_municipio, casos, o fallecidos fueran None, 0, o estuvieran vacíos.

- Corrección de IDs Inconsistentes:
        Los IDs duplicados de departamentos y municipios se corrigieron utilizando el primer ID válido encontrado.

- Eliminación de Filas Nulas:
        Se eliminaron filas donde cualquier columna crítica tuviera valores nulos después de la conversión.

## Inserción de Datos

Se implementó un sistema de inserción en paquetes de 50 registros para mejorar el rendimiento y la confiabilidad, con las siguientes características:

- Inserción por Lotes:
        Los registros se insertan en paquetes de 50 para evitar errores de inserción masiva.

- Manejo de Errores:
        Si un lote falla durante la inserción, se registra y se intenta insertar nuevamente después de completar todos los lotes restantes.

- Reintento de Lotes Fallidos:
        Los lotes fallidos se reintentan después de una pausa de 10 segundos, lo que permite manejar fallas temporales en la base de datos.

## Modelo de Datos

El modelo de datos está compuesto por tres tablas principales:

- Tabla departamento
        id (INTEGER, clave primaria): Identificador único del departamento.
        nombre (STRING, único y no nulo): Nombre del departamento.

- Tabla municipio
        id (INTEGER, clave primaria): Identificador único del municipio.
        nombre (STRING, no nulo): Nombre del municipio.
        poblacion (INTEGER, no nulo): Población del municipio.
        id_departamento (INTEGER, clave foránea): Relación con la tabla departamento.

- Tabla registro
        id (INTEGER, clave primaria): Identificador único del registro.
        fecha (DATE, no nulo): Fecha del registro.
        casos (INTEGER, no nulo): Número de casos reportados.
        fallecidos (INTEGER, no nulo): Número de fallecidos reportados.
        id_municipio (INTEGER, clave foránea, puede ser NULL): Relación con la tabla municipio.

## Configuración del Proyecto

1. Clona este repositorio:

    git clone https://github.com/FernandoJRR/Practica1SS2

2. Instala las dependencias:

    pip install -r requirements.txt

3. Configura la conexión a PostgreSQL en database.py:

    DATABASE_URL = "postgresql+psycopg2://<usuario>@localhost/<nombre_bd>"

4. Ejecuta la creación de tablas:

    from database import crear_tablas
    crear_tablas()

5. Carga y limpia datos con Pandas:

    from database import insertar_datos
    insertar_datos(df)
