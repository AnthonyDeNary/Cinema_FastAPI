import time
from fastapi import FastAPI, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy.orm import Session
from app.v1.utils.db import get_db, authenticate_user, create_access_token, get_password_hash, get_current_user
from app.v1.model.model import User
from app.v1.schema.schemas import UserCreate, UserOut, Token

from fastapi.security import OAuth2PasswordRequestForm


# Instanciamos la clase FastAPI
app = FastAPI()


# Modelos que se usarán para interactuar para la B.D. en memoria
class Post(BaseModel):
    author: str
    title: str
    content: str
    tags: str


class Role(str, Enum):
    admin = "admin"
    user = "user"


class UserA(BaseModel):
    id: Optional[UUID] = uuid4()
    first_name: str
    last_name: str
    city: str
    roles: List[Role]


class UpdateUser(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    roles: Optional[List[Role]]


# Creamos APIs que afectarán a la BD en memoria que tenemos líneas abajo (db_m)
@app.get("/")
async def root():
    return {"name": "Carolina Gutierrez", "city": "Lima", "age": 24}


@app.get('/posts/{id}')
def getPost(id):
    return {"data": id}


@app.post('/posts')
def addPost(post: Post):
    return {"message": f"The post {post.title} has been added"}


@app.get("/api/v1/users")
def get_users():
    return db_m


@app.post("/api/v1/users")
def create_user(user: UserA):
    db_m.append(user)
    return {"id": user.id}


@app.delete("/api/v1/users/{id}")
def delete_user(id: UUID):
    for user in db_m:
        if user.id == id:
            db_m.remove(user)
            return


@app.put("/api/v1/user/{id}")
def update_user(id: UUID, user_update: UpdateUser):
    for user in db_m:
        if user.id == id:
            if user_update.first_name is not None:
                user.first_name = user_update.first_name
            if user_update.last_name is not None:
                user.last_name = user_update.last_name
            if user_update.roles is not None:
                user.roles = user_update.roles
        return user.id


# Middleware que agregará un campo personalizado a la cabecerá de las peticiones de las APIs
@app.middleware("http")
async def add_custom_header(request: Request, call_next):
    response = await call_next(Request)
    response.headers["X-hi-name"] = "Hi Carol welcome!"

    return response


# Middleware que nos dará el tiempo de ejecución de las APIs y se estará agregando en el header
# con el nombre de "X-process-Time"
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):

    start_time = time.time()
    # Se ejecutará "add_process_time_header" en el middleware y la API se ejecutará con la ruta coincidente
    response = await call_next(request)

    process_time = time.time() - start_time
    # Añadimos el tiempo en la cabecera de la respuesta
    response.headers["X-process-Time"] = str(process_time)
    print("Tiempo de procedimiento: {}".format(process_time))
    return response


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


@app.post("/new_user/", response_model=UserOut)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.hashed_password)
    new_user = User(first_name=user.first_name, last_name=user.last_name, city=user.city,
                    username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# API protegida por el token
@app.get("/all_users", response_model=List[UserOut], dependencies=[Depends(get_current_user)])
def list_users(session: Session = Depends(get_db)):
    list_user = session.query(User).all()   # Obtenemos todos los usuarios de la tabla en la BD
    return list_user


# API protegida por el token
@app.get("/user/{id}", response_model=UserOut, dependencies=[Depends(get_current_user)])
def read_user(id: UUID, session: Session = Depends(get_db)):
    user = session.query(User).get(id)
    # Verificar si el id existe. Si no, devolver respuesta 404 Not found
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con id {id} no se encuentra en la BD")
    return user


@app.put("/user/{id}", response_model=UserOut)
def update_user(id: UUID, user_update: UserCreate, session: Session = Depends(get_db)):
    user = session.query(User).get(id)  # Obtenemos el usuario de la BD
    if user:
        user.first_name = user_update.first_name
        user.last_name = user_update.last_name
        user.city = user_update.city
        session.commit()
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con id {id} no fue encontrado para poder actualizarlo")
    return user


@app.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: UUID, session: Session = Depends(get_db)):

    user = session.query(User).get(id)  # Obtenemos el usuario de la BD
    if user:
        session.delete(user)
        session.commit()
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario con el id {id} no fue encontrado")
    return user


"""
Configuración personalizada de OpenAPI:
- Sacar los comentarios del siguiente código en el caso de querer que 
para ciertas APIs necesiten el ingreso de Token Bearer luego que la obtenemos del API
'/token' que se ha creado líneas arriba.
"""

"""
from fastapi.openapi.utils import get_openapi
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="API description",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Descomentar la siguiente línea en caso que se quiera aplicar el uso de Token Bearer para todas las APIs
    # Dejar el for y su contenido comentado
    #openapi_schema["security"] = [{"bearerAuth": []}]
    for route in openapi_schema["paths"]:
        if "/all_users" in route:
            openapi_schema["paths"][route]["get"]["security"] = [{"bearerAuth": []}]
        if "/user/{id}" in route:
            openapi_schema["paths"][route]["get"]["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
"""

#Creamos una Base de Datos en memoria
db_m: List[UserA] = [
    UserA(
        id=uuid4(),
        first_name="Freddy",
        last_name="Nolasco",
        city="Lima",
        roles=[Role.user],
    ),
    UserA(
        id=uuid4(),
        first_name="Juana",
        last_name="Falcón",
        city="Trujillo",
        roles=[Role.admin],
    ),
    UserA(
        id=uuid4(),
        first_name="Noelia",
        last_name="Perez",
        city="Lima",
        roles=[Role.user],
    ),
    UserA(
        id=uuid4(),
        first_name="Edwin",
        last_name="Deza",
        city="Cusco",
        roles=[Role.admin, Role.user],
    ),
]


