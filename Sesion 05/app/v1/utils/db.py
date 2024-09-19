from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLACHEMY_DATABASE_URL = "postgresql://postgres:123@localhost:5432/Api_python"
engine = create_engine(SQLACHEMY_DATABASE_URL)

SessionLocal= sessionmaker(autocommit=False, autoflush = False, bind = engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


