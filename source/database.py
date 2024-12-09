import pandas as pd
import time
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Configuración de la base de datos
DATABASE_URL = "postgresql+psycopg2://fernanrod@localhost/ss2_practica1_db"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=False)

# Crear sesionmaker
Session = sessionmaker(bind=engine)

# Declaración base para ORM
Base = declarative_base()

# Definir la tabla Departamento
class Departamento(Base):
    __tablename__ = 'departamento'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False, unique=True)

    # Relación con la tabla Municipio
    municipios = relationship("Municipio", back_populates="departamento")

# Definir la tabla Municipio
class Municipio(Base):
    __tablename__ = 'municipio'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    poblacion = Column(Integer, nullable=False)
    id_departamento = Column(Integer, ForeignKey('departamento.id'), nullable=False)

    # Relación con tablas
    departamento = relationship("Departamento", back_populates="municipios")
    registros = relationship("Registro", back_populates="municipio")

# Definir la tabla Registro
class Registro(Base):
    __tablename__ = 'registro'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    casos = Column(Integer, nullable=False)
    fallecidos = Column(Integer, nullable=False)
    id_municipio = Column(Integer, ForeignKey('municipio.id'), nullable=True)

    # Relación con la tabla Municipio
    municipio = relationship("Municipio", back_populates="registros")

# Crear tablas
def crear_tablas():
    print("Creando tablas")
    Base.metadata.create_all(engine)
    print("Tablas creadas correctamente.")

def drop_registros():
    session = Session()
    try:
        print("Eliminando todos los registros...")

        # Borrar registros en orden de dependencias
        session.query(Registro).delete()
        session.query(Municipio).delete()
        session.query(Departamento).delete()

        # Confirmar cambios
        session.commit()
        print("Todos los registros han sido eliminados correctamente.")

    except Exception as e:
        # Revertir cambios si ocurre un error
        session.rollback()
        print(f"Error al eliminar los registros: {e}")

    finally:
        session.close()

# Insertar datos en la base de datos
def insertar_datos(df):
    session = Session()
    lotes_fallidos = []
    qty_lotes_exitosos = 0
    qty_lotes_fallidos = 0
    try:
        print("INSERTANDO DEPARTAMENTOS")
        # Crear diccionarios para bulk insert
        dfDepartamentos = df[df['codigo_departamento'].notna() & (df['departamento'] != '0')]
        departamentos = dfDepartamentos[['codigo_departamento', 'departamento']].drop_duplicates().rename(
            columns={'codigo_departamento': 'id', 'departamento': 'nombre'}
        ).to_dict('records')
        print(departamentos)

        # Insertar departamentos
        session.bulk_insert_mappings(Departamento, departamentos)
        session.commit()
        print("DEPARTAMENTOS INSERTADOS")

        print("INSERTANDO MUNICIPIOS")
        # Crear lista de municipios
        dfMunicipios = df[df['codigo_municipio'].notna() & (df['municipio'] != '0')]
        municipios = dfMunicipios[['codigo_municipio', 'municipio', 'codigo_departamento', 'poblacion']].drop_duplicates().rename(
            columns={'codigo_municipio': 'id', 'municipio': 'nombre', 'codigo_departamento': 'id_departamento'}
        ).to_dict('records')
        print(municipios)

        # Insertar municipios
        session.bulk_insert_mappings(Municipio, municipios)
        session.commit()
        print("MUNICIPIOS INSERTADOS")

        # Crear lista de registros
        registros = df[['fecha', 'casos', 'fallecidos', 'codigo_municipio']].rename(
            columns={'codigo_municipio': 'id_municipio'}
        )

        # Reemplazar None con NULL explícito
        registros['id_municipio'] = registros['id_municipio'].where(pd.notnull(registros['id_municipio']), None)
        registros = registros.to_dict('records')

        # Insertar registros
        lotes = (len(registros) + 49) // 50
        for i, inicio in enumerate(range(0, len(registros), 50)):
            lote = registros[inicio:inicio+50]

            try:
                session.bulk_insert_mappings(Registro, lote)
                session.commit()
                qty_lotes_exitosos += 1
                print(f"INSERTADO LOTE #{i+1}/#{lotes} DE {len(lote)} REGISTROS")
            except Exception as e:
                session.rollback()
                lotes_fallidos.append((i+1, lote))
                qty_lotes_fallidos += 1
                print(f"FALLIDO LOTE #{i+1}/#{lotes} DE {len(lote)} REGISTROS")

        print("Carga de Datos Inicial Finalizada")
        print(f"{qty_lotes_exitosos}/{lotes} Insertados Correctamente")
        if qty_lotes_fallidos > 0:
            print(f"Hay {qty_lotes_fallidos} registros que no fueron insertados")
            print("Esperando 10 segundos antes de reintentar")
            qty_lotes_fallidos = 0
            time.sleep(10)

            qty_lotes_reinsertados = 0
            for i, batch in lotes_fallidos:
                try:
                    print(f"REINTENTANDO LOTE #{i} DE {len(batch)} REGISTROS")
                    session.bulk_insert_mappings(Registro, batch)
                    session.commit()
                    print(f"INSERTADO LOTE #{i} DE {len(batch)} REGISTROS")
                except Exception as e:
                    session.rollback()
                    print(f"FALLA FINAL DE LOTE #{i} DE {len(lote)} REGISTROS")
                    print(f"ERROR: {e}")

            print(f"{qty_lotes_reinsertados} LOTES FALLIDOS REINSERTADOS")
        else:
            print("TODOS LOS REGISTROS INSERTADOS CORRECTAMENTE")

    except Exception as e:
        session.rollback()
        print(f"Error al insertar los datos: {e}")

    finally:
        session.close()