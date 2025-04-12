from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
from utils.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from schemas.token import Token, UserCreate, User as UserSchema
from models.user import User
from database.conexion import get_db

router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=Token)
async def Token_para_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"mensaje": "Usuario o contraseña incorrectos"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"access_token": access_token, "token_type": "bearer"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"mensaje": "Error al procesar la autenticación", "error": str(e)}
        )

@router.post("/users/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def Crear_usuario(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si el nombre de usuario ya existe
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"mensaje": "El nombre de usuario ya está registrado"}
            )
        
        # Verificar si el correo electrónico ya existe
        db_email = db.query(User).filter(User.email == user.email).first()
        if db_email:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"mensaje": "El correo electrónico ya está registrado"}
            )
        
        # Crear el nuevo usuario
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username, 
            email=user.email, 
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
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