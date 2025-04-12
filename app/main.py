from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes import peliculas, auth
from database.conexion import engine
from models import pelicula, user as user

# Crear las tablas en la base de datos
pelicula.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Películas",
    description="API para el registro y gestión de películas",
    version="1.0.0",
)

# Configurar CORS para permitir solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador de excepciones para errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_msg = {
            "campo": error["loc"][-1],
            "mensaje": error["msg"],
            "tipo": error["type"]
        }
        errors.append(error_msg)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "mensaje": "Error de validación de datos",
            "errores": errors
        }
    )

# Manejador de excepciones para errores de base de datos
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "mensaje": "Error en la base de datos",
            "error": str(exc)
        }
    )

# Manejador de excepciones para errores generales
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "mensaje": "Error interno del servidor",
            "error": str(exc)
        }
    )

# Incluir los routers
app.include_router(auth.router)
app.include_router(peliculas.router)

# Ruta raíz
@app.get("/")
async def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"mensaje": "Bienvenido a la API de Películas"}
    )

# Iniciar el servidor si se ejecuta este archivo directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)