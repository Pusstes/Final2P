from pydantic import BaseModel, EmailStr, Field
from  typing import Optional

class Token(BaseModel):
    acces_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: Optional[str] = None
    
class UserBase(BaseModel):
    username: str
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña de mínimo 6 caracteres")  
    
class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True
    
