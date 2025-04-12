from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# nombre de la base de datos
dbName = 'Peliculas.db'
# ruta donde se guardará la base de datos
base_dir = os.path.dirname(os.path.realpath(__file__))
# cadena de conexión a la base de datos SQLite
DATABASE_URL = f"sqlite:///{os.path.join(base_dir, dbName)}"

# Crear el motor de base de datos
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

# Crear una sesión local para operaciones con la base de datos
Session = sessionmaker(bind=engine)

# Base para modelos declarativos
Base = declarative_base()

# Función para obtener la sesión de base de datos
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()