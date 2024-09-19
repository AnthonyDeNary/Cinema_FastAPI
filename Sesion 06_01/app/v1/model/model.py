import uuid
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()


class User(Base):
    # Asignamos un nombre a la tabla que se reflejará en la BD al momento de realizar la migración
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    city = Column(String)
    username = Column(String, unique=True)
    hashed_password = Column(String)


# Para esta siguiente variable se pondrá el usuario, contraseña, hostname, puerto y nombre de la B.D.
SQLACHEMY_DATABASE_URL = 'postgresql://postgres:admin@localhost:5433/inka_company'
engine = create_engine(SQLACHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)
