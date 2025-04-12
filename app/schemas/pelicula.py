from pydantic import BaseModel, Field, validator
from typing import Optional

class PeliculaBase(BaseModel):
    titulo: str = Field(..., min_length=2, description="Título de la película, mínimo 2 letras")
    genero: str = Field(..., min_length=4, description="Género de la película, mínimo 4 letras")
    año: int = Field(..., ge=1000, le=9999, description="Año de la película, debe ser un número de 4 dígitos")
    clasificacion: str = Field(..., description="Clasificación de la película (A, B o C)")
    
    @validator('clasificacion')
    def validar_clasificacion(cls, v):
        if v not in ['A', 'B', 'C']:
            raise ValueError('Clasificación debe ser A, B o C')
        return v
    
class PeliculaCreate(PeliculaBase):
    pass
    
class PeliculaUpdate(PeliculaBase):
    titulo: Optional[str] = Field(None, min_length=2, description="Título de la película, mínimo 2 letras")
    genero: Optional[str] = Field(None, min_length=4, description="Género de la película, mínimo 4 letras")
    año: Optional[int] = Field(None, ge=1000, le=9999, description="Año de la película, debe ser un número de 4 dígitos")
    clasificacion: Optional[str] = Field(None, description="Clasificación de la película (A, B o C)")
        
class Pelicula(PeliculaBase):
    id: int 
        
    class Config:
        orm_mode = True
            
            
