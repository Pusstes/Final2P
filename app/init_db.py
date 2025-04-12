"""
Script para inicializar la base de datos con datos de prueba.
"""
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.conexion import engine, Session
from models.pelicula import Pelicula
from models.user import User
from utils.auth import get_password_hash

# Crear las tablas
from models.pelicula import Base as PeliculaBase
from models.user import Base as UserBase

PeliculaBase.metadata.create_all(bind=engine)
UserBase.metadata.create_all(bind=engine)

# Crear una sesión
db = Session()

# Verificar si ya hay datos
existing_movies = db.query(Pelicula).count()
existing_users = db.query(User).count()

# Crear usuario para pruebas si no existe
if existing_users == 0:
    print("Creando usuario de prueba...")
    test_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123")
    )
    db.add(test_user)
    db.commit()
    print("Usuario creado: admin / admin123")

# Crear películas de ejemplo si no existen
if existing_movies == 0:
    print("Creando películas de ejemplo...")
    
    movies_data = [
        {"titulo": "Matrix", "genero": "Ciencia Ficción", "año": 1999, "clasificacion": "B"},
        {"titulo": "El Padrino", "genero": "Drama", "año": 1972, "clasificacion": "C"},
        {"titulo": "Interestelar", "genero": "Ciencia Ficción", "año": 2014, "clasificacion": "B"},
        {"titulo": "Titanic", "genero": "Romance", "año": 1997, "clasificacion": "A"},
        {"titulo": "Avatar", "genero": "Aventura", "año": 2009, "clasificacion": "A"}
    ]
    
    for movie_data in movies_data:
        new_movie = Pelicula(**movie_data)
        db.add(new_movie)
    
    db.commit()
    print(f"Se crearon {len(movies_data)} películas de ejemplo")

else:
    print(f"Ya existen {existing_movies} películas en la base de datos")

# Cerrar la sesión
db.close()

print("\nInicialización completada. La aplicación está lista para la demostración.")