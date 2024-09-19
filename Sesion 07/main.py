"""
Para reiniciar el servicio de Uvicorn:
    1. Usar tasklist /FI "IMAGENAME eq python.exe"
    2. Usar: taskkill /PID 3964  /F (Cambiar el número)
    3. Usar uvicorn main:app --reload
"""
import time
from idlelib.rpc import response_queue
from time import process_time

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.openapi.models import OAuth2
from fastapi.params import Depends
from pydantic import BaseModel
from typing import List, Optional  # Para tipificar la lista(user, admin)
from uuid import  UUID, uuid4
from enum import Enum

from requests import session
from sqlalchemy.orm import Session

from app.v1.utils.db import create_access_token
from app.v1.utils.db import get_db,authenticate_user,get_password_hash #Importación de la función get_db(hecha para la conección)

from app.v1.schema.schemas import UserBase, UserCreate, UserOut,Token
from app.v1.model.model import User

from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer


app = FastAPI()



class Post(BaseModel):
    author  : str
    title   : str
    content : str

class Role(str, Enum):
    admin = "admin"
    user = "user"

class Userv2(BaseModel):
    id          : Optional[UUID] = uuid4()
    first_name  : str
    last_name   : str
    city        : str
    roles        : List[Role]


class UpdateUserv2(BaseModel):
    first_name  : Optional[str]
    last_name   : Optional[str]
    roles        : Optional[List[Role]]


""" ACCESO A LAS APIS"""
@app.post("/token",response_model=Token)
def login_for_acces_token(form_data :OAuth2AuthorizationCodeBearer = Depends(), db:Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "usuario o password incorrecta",
            headers = {"WWW_Authenticate": "Bearer"}
        )
    access_token = create_access_token(data = {"sub":user.username})
    return {"acess_token": access_token,"token_type":"Bearer"}
""""MIDDLEWARE"""
""""MIDDLEWARE"""
@app.middleware("http")
async def add_custom_header(request:Request,call_next):
    response = await call_next(Request)
    response.headers["X-hi-name"] = "Hi Panadol, welcome!"
    return response



@app.middleware("http")
async def add_process_time_header(request:Request, call_next):
    start_time = time.time()
    #Se ejecutará "add_process_time_header" en el middleware y la API se ejecutará en la cuta coincidente
    response = await call_next(request)

    process_time = time.time() - start_time
    #Añadir el tiempo a la cabecera
    response.headers["X-process-Time"] = str(process_time)
    print("Tiempo de procedimiento: {}".format(process_time))

    return response



""" PARTE DE LAS APIS """
@app.post("/new_user/",response_model = UserOut)  # API con conexión a la DB -> Cine
def create_new_user(user:UserCreate, db:Session = Depends(get_db)): #Crear un nuevo usuario
    hashed_password = get_password_hash(user.hashed_password)
    new_user = User(first_name = user.first_name, last_name = user.last_name,city = user.city
                    , username = user.username,hashed_password = hashed_password )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@app.get("/all_users",response_model=List[UserOut]) #Obtener todos los usuarios
def list_users(session : Session = Depends(get_db)):
    list_user = session.query(User).all()
    return list_user




@app.get("/user/{id}", response_model = UserOut) #Obtener usuario a partir de ID
def read_user(id:UUID, session : Session = Depends(get_db)):
    user = session.query(User).get(id)

    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con id {id} no se encuentra en la DB")

    return user




@app.put("/user/{id}", response_model = UserOut) #Añadir usuario
def update_user(id:UUID,user_update : UserCreate, session : Session = Depends(get_db)):
    user = session.query(User).get(id) #Obtner el usuario de la DB

    if user:
        user.first_name = user_update.first_name
        user.last_name = user_update.last_name
        user.city = user_update.city
        session.commit()

    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con id {id} no fue encontrado para la actualziación")

    return user



@app.delete("/user/{id}",status_code=status.HTTP_204_NO_CONTENT) #Eliminar usuario por ID
def delete_user(id:UUID,session : Session = Depends(get_db)):
    user = session.query(User).get(id)

    if user:
        session.delete(user)
        session.commit()
    if not user:
        raise HTTPException(status_code=404, detail=f"No existe el usuario con el id {id}")

    return user