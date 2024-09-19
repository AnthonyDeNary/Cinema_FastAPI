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
from six import string_types
from sqlalchemy.orm import Session

from app.v1.model.model import Ticket
from app.v1.schema.schemas import TicketOut, TicketCreate
from app.v1.utils.db import get_current_user
from app.v1.utils.db import create_access_token
from app.v1.utils.db import get_db,authenticate_user,get_password_hash #Importación de la función get_db(hecha para la conección)

from app.v1.schema.schemas import UserBase, UserCreate, UserOut, Token, CinemaBase, CinemaOut, CinemaCreate
from app.v1.model.model import User, Cinema,Movie

from app.v1.schema.schemas import MovieOut, MovieCreate

from fastapi.security import OAuth2PasswordRequestForm

from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer

from datetime import datetime

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
# Esta función nos ayudará a autenticar a un usuario mediante su usuario y contraseña
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o password incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": form_data.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

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
""" PARTE DE LAS APIS """
""" PARTE DE LAS APIS """
""" APIS DE USUARIO"""
# CREACIÓN DE NUEVO USUARIO
@app.post("/new_user/",response_model = UserOut)  # API con conexión a la DB -> Cine
def create_new_user(user:UserCreate, db:Session = Depends(get_db)): #Crear un nuevo usuario
    hashed_password = get_password_hash(user.hashed_password)
    new_user = User(first_name = user.first_name, last_name = user.last_name,city = user.city
                    , username = user.username,hashed_password = hashed_password )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# OBTENCIÓN DE TODOS LOS USUARIOS
@app.get("/all_users",response_model=List[UserOut], dependencies = [Depends(get_current_user)])
def list_users(session : Session = Depends(get_db)):
    list_user = session.query(User).all()
    return list_user



# BÚSQUEDA DE USUARIO A PARTIR DE SU ID
@app.get("/user/{id}", response_model = UserOut, dependencies = [Depends(get_current_user)])
def read_user(id:UUID, session : Session = Depends(get_db)):
    user = session.query(User).get(id)

    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con id {id} no se encuentra en la DB")

    return user



# ACTUALIZAR USUARIOS
@app.put("/user/{id}", response_model = UserOut, dependencies = [Depends(get_current_user)])
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


#ELIMINAR USUARIO USANDO SU ID
@app.delete("/user/{id}",status_code=status.HTTP_204_NO_CONTENT) #Eliminar usuario por ID
def delete_user(id:UUID,session : Session = Depends(get_db)):
    user = session.query(User).get(id)

    if user:
        session.delete(user)
        session.commit()
    if not user:
        raise HTTPException(status_code=404, detail=f"No existe el usuario con el id {id}")

    return user

""" APIS DE LOS CINES """
# CREACIÓN DE NUEVO CINE
@app.post("/new_cinema/",response_model = CinemaOut)  # API con conexión a la DB -> Cine
def create_new_cinema(user:CinemaCreate, db:Session = Depends(get_db)): #Crear un nuevo usuario
    new_cinema = Cinema(name = user.name, city = user.city, address = user.address)
    db.add(new_cinema)
    db.commit()
    db.refresh(new_cinema)
    return new_cinema

# OBTENCIÓN DE TODOS LOS CINES
@app.get("/all_cinemas",response_model=List[CinemaOut], dependencies = [Depends(get_current_user)])
def list_cinemas(session : Session = Depends(get_db)):
    list_cinemas = session.query(Cinema).all()
    return list_cinemas

# BÚSQUEDA DE CINE A PARTIR DE SU ID
@app.get("/cinema/{id}", response_model = CinemaOut, dependencies = [Depends(get_current_user)])
def read_cinema(id:UUID, session : Session = Depends(get_db)):
    cinema = session.query(Cinema).get(id)

    if not cinema:
        raise HTTPException(status_code=404, detail=f"CINE con id {id} no se encuentra en la DB")

    return cinema


# ACTUALIZAR CINE
@app.put("/cine/{id}", response_model = CinemaOut, dependencies = [Depends(get_current_user)])
def update_cinema(id:UUID,cinema_update : CinemaCreate, session : Session = Depends(get_db)):
    cinema = session.query(Cinema).get(id) #Obtner el cine de la DB

    if cinema:
        cinema.name = cinema_update.name
        cinema.city = cinema_update.city
        cinema.address = cinema_update.address
        session.commit()

    if not cinema:
        raise HTTPException(status_code=404, detail=f"Cine con id {id} no fue encontrado para la actualziación")

    return cinema

""" APIS DE LAS PELÍCULAS """
# CREACIÓN DE NUEVA PELÍCULA
@app.post("/new_movie/",response_model = MovieOut)  # API con conexión a la DB -> Cine
def create_new_movie(user:MovieCreate, db:Session = Depends(get_db)): #Crear un nuevo usuario
    new_movie = Movie(title = user.title, genre = user.genre, duration_minutes = user.duration_minutes)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

# OBTENCIÓN DE TODAS LAS PELÍCULAS
@app.get("/all_movies",response_model=List[MovieOut])
def list_movies(session : Session = Depends(get_db)):
    list_movies = session.query(Movie).all()
    return list_movies

# OBTENCIÓN DE PELÍCULAS CON DURACIÓN MENOR A UN VALOR DADO
@app.get("/movies_by_max_duration/{max_duration}", response_model=List[MovieOut])
def list_movies_by_max_duration(max_duration: int, session: Session = Depends(get_db)):
    movies = session.query(Movie).filter(Movie.duration_minutes < max_duration).all()
    return movies

# ELMINACIÓN DE PELÍCULA A PARTIR DE SU ID
@app.delete("/movie/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(id: UUID, session: Session = Depends(get_db)):
    movie = session.query(Movie).get(id)

    if movie:
        session.delete(movie)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No existe la película con el id {id}")

    return movie

""" APIS DE LOS TICKETS """
# CREACIÓN DE UN NUEVO TICKET
@app.post("/new_ticket/",response_model = TicketOut)
def create_new_ticket(user_id:UUID,movie_id:UUID,cinema_id:UUID, ticket:TicketCreate, db:Session = Depends(get_db)): #Crear un nuevo ticket
    ticket = Ticket(**ticket.dict(), user_id=user_id,movie_id = movie_id,cinema_id = cinema_id )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


