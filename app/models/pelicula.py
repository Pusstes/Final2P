from database.conexion import Base
from sqlalchemy import Column, Integer, String

class Pelicula(Base):
    __tablename__ = "peliculas"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    genero = Column(String)
    año = Column(Integer)
    clasificacion = Column(String, index=True)