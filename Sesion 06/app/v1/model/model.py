import uuid
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID



#Obtenido/referenciado de db.py
Base = declarative_base()

#Modelos referentes a la base de datos

class Pelicula(Base):
    __tablename__ = "peliculas"

    # Definición de la tabla "peliculas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String, nullable=False)
    genero = Column(String, nullable=False)
    director = Column(String)
    duracion = Column(Integer)  # Duración en minutos


class User(Base):
    # Asignamos un nombre a la tabla que se reflejará en la BD al momento de realizar la migración
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    city = Column(String)
    username = Column(String ,unique = True)
    hashed_password = Column(String)


    """
    username = Column(String, unique=True)
    hashed_password = Column(String)
    """

SQLACHEMY_DATABASE_URL = 'postgresql://postgres:123@localhost:5432/Cine'
engine = create_engine(SQLACHEMY_DATABASE_URL)

#Envío de datos a la base de datos
Base.metadata.create_all(bind=engine)