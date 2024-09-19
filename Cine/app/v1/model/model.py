import uuid
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Time, Date


#Obtenido/referenciado de db.py
Base = declarative_base()

#Modelos referentes a la base de datos

# Tabla Película
class Movie(Base):
    __tablename__ = "movies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    genre = Column(String)
    duration_minutes = Column(Integer, nullable=False)

    # Relación con Ticket
    tickets = relationship("Ticket", back_populates="movie")



# Tabla Usuario
class User(Base):
    # Asignamos un nombre a la tabla que se reflejará en la BD al momento de realizar la migración
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    city = Column(String)
    username = Column(String ,unique = True)
    hashed_password = Column(String)

    # Relación con Ticket
    tickets = relationship("Ticket", back_populates="user")

# Tabla Cine
class Cinema(Base):
    __tablename__ = "cinemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=False)

    # Relación con Ticket
    tickets = relationship("Ticket", back_populates="cinema")


# Tabla Ticket
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seat_number = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    # Claves foráneas
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    movie_id = Column(UUID(as_uuid=True), ForeignKey('movies.id'), nullable=False)
    cinema_id = Column(UUID(as_uuid=True), ForeignKey('cinemas.id'), nullable=False)

    #presentation_time = Column(Time, nullable=False)  # Hora de la presentación
    #presentation_day = Column(Date, nullable=False)  # Día de la presentación

    # Relaciones
    user = relationship("User", back_populates="tickets")
    movie = relationship("Movie", back_populates="tickets")
    cinema = relationship("Cinema", back_populates="tickets")



SQLACHEMY_DATABASE_URL = 'postgresql://postgres:123@localhost:5432/DB_Cine'

engine = create_engine(SQLACHEMY_DATABASE_URL)

#Envío de datos a la base de datos
Base.metadata.create_all(bind=engine)