from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from database.conexion import get_db
from models.pelicula import Pelicula
from schemas.pelicula import Pelicula as PeliculaSchema, PeliculaCreate, PeliculaUpdate
from utils.auth import get_current_user

router = APIRouter(tags=["Películas"])

# Endpoint para consultar todas las películas
@router.get("/peliculas/", response_model=List[PeliculaSchema])
def ConsultarTodasLasPeliculas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        peliculas = db.query(Pelicula).offset(skip).limit(limit).all()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[{
                "id": pelicula.id,
                "titulo": pelicula.titulo,
                "genero": pelicula.genero,
                "año": pelicula.año,
                "clasificacion": pelicula.clasificacion
            } for pelicula in peliculas]
        )
    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error al consultar la base de datos", "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error interno del servidor", "error": str(e)}
        )

# Endpoint para consultar una película específica
@router.get("/peliculas/{pelicula_id}", response_model=PeliculaSchema)
def Pelicula_id(pelicula_id: int, db: Session = Depends(get_db)):
    try:
        pelicula = db.query(Pelicula).filter(Pelicula.id == pelicula_id).first()
        if pelicula is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"mensaje": f"Película con id {pelicula_id} no encontrada"}
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "id": pelicula.id,
                "titulo": pelicula.titulo,
                "genero": pelicula.genero,
                "año": pelicula.año,
                "clasificacion": pelicula.clasificacion
            }
        )
    except SQLAlchemyError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error al consultar la base de datos", "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error interno del servidor", "error": str(e)}
        )

# Endpoint para guardar una película
@router.post("/peliculas/", response_model=PeliculaSchema, status_code=status.HTTP_201_CREATED)
def Agregar_pelicula(pelicula: PeliculaCreate, db: Session = Depends(get_db)):
    try:
        db_pelicula = Pelicula(
            titulo=pelicula.titulo,
            genero=pelicula.genero,
            año=pelicula.año,
            clasificacion=pelicula.clasificacion
        )
        db.add(db_pelicula)
        db.commit()
        db.refresh(db_pelicula)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "id": db_pelicula.id,
                "titulo": db_pelicula.titulo,
                "genero": db_pelicula.genero,
                "año": db_pelicula.año,
                "clasificacion": db_pelicula.clasificacion
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error al guardar en la base de datos", "error": str(e)}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error interno del servidor", "error": str(e)}
        )

# Endpoint para editar una película
@router.put("/peliculas/{pelicula_id}", response_model=PeliculaSchema)
def Actualizar_pelicula(pelicula_id: int, pelicula: PeliculaUpdate, db: Session = Depends(get_db)):
    try:
        db_pelicula = db.query(Pelicula).filter(Pelicula.id == pelicula_id).first()
        if db_pelicula is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"mensaje": f"Película con id {pelicula_id} no encontrada"}
            )
        
        # Actualizar solo los campos proporcionados
        pelicula_data = pelicula.dict(exclude_unset=True)
        for key, value in pelicula_data.items():
            setattr(db_pelicula, key, value)
        
        db.commit()
        db.refresh(db_pelicula)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "id": db_pelicula.id,
                "titulo": db_pelicula.titulo,
                "genero": db_pelicula.genero,
                "año": db_pelicula.año,
                "clasificacion": db_pelicula.clasificacion
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error al actualizar en la base de datos", "error": str(e)}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error interno del servidor", "error": str(e)}
        )

# Endpoint para eliminar una película (protegido con JWT)
@router.delete("/peliculas/{pelicula_id}", status_code=status.HTTP_204_NO_CONTENT)
def Borrar_pelicula(
    pelicula_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    try:
        db_pelicula = db.query(Pelicula).filter(Pelicula.id == pelicula_id).first()
        if db_pelicula is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"mensaje": f"Película con id {pelicula_id} no encontrada"}
            )
        
        db.delete(db_pelicula)
        db.commit()
        return JSONResponse(
            content={"mensaje": f"Película con id {pelicula_id} eliminada correctamente"}
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error al eliminar de la base de datos", "error": str(e)}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error interno del servidor", "error": str(e)}
        )