from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Float
from sqlalchemy.orm import declarative_base

# Configuración de la base de datos
DATABASE_URL = "postgresql+psycopg2://fernanrod@localhost/ss2_practica1_db"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Declaración base para ORM
Base = declarative_base()

# Definir la tabla Departamento
class Departamento(Base):
    __tablename__ = 'departamento'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, unique=True)

    # Relación con la tabla Municipio
    municipios = relationship("Municipio", back_populates="departamento")

# Definir la tabla Municipio
class Municipio(Base):
    __tablename__ = 'municipio'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
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
    id_municipio = Column(Integer, ForeignKey('municipio.id'), nullable=False)

    # Relación con la tabla Municipio
    municipio = relationship("Municipio", back_populates="registros")

# Crear tablas
def crear_tablas():
    print("Creando tablas")
    Base.metadata.create_all(engine)
    print("Tablas creadas correctamente.")

# Función para obtener la conexión
def obtener_conexion():
    return engine.connect()
