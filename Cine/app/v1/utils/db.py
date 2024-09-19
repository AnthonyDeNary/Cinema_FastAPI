from hashlib import algorithms_available
from mmap import ACCESS_COPY
from os import times

from jose.constants import ALGORITHMS, Algorithms
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from typing import Optional
from datetime import timedelta, datetime

#Para la conidficación jwt
from jose import jwt, JWTError

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from.config import settings #Derivado de .env -> Config(url en cadena)
from ..model.model import User


# Configuración para Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar de OAUTH2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#Configuración de JWT
SECRET_KEY = "secretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


#SQLACHEMY_DATABASE_URL = 'postgresql://postgres:123@localhost:5432/Cine'
SQLACHEMY_DATABASE_URL = settings.db_url
engine = create_engine(SQLACHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit= False, autoflush=False, bind=engine)
Base = declarative_base()


#Activar y finalizar la conección a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Esta función nos va a crear un token de acceso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt

# Esta función nos sirve para encriptar o hashear las contraseñas antes de almacenarlos en la B.D.
def get_password_hash(password):
    return pwd_context.hash(password)

#Obtenener usuario por el Username
def get_user_by_username(session: Session, username: str):
    return session.query(User).filter(User.username == username).first()

# Esta función nos va a ayudar a autenticar a un usuario
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    # La siguiente condicional 'pwd_context.verify' nos verificará si la contraseña ingresada
    # en texto plano coincide con el hash
    # de la contraseña almanecado en la B.D.
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# Esta función nos ayudará a obtener el usuario actual a partir del token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No pueden ser validadas las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
