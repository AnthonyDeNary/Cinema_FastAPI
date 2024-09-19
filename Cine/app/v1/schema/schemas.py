from pydantic import BaseModel
from uuid import UUID
from sqlalchemy import Time, Date
from typing import List

#Sirve como un espejo de models.py
##################### TICKET
class TicketBase(BaseModel):
    seat_number: str
    price: int
    #presentation_time: str
    #presentation_day: Date

class TicketOut(TicketBase):
    id: UUID
    class Config:
        from_attributes = True

class TicketCreate(TicketBase):
    pass


##################### USUARIO
class UserBase(BaseModel):
    first_name : str
    last_name : str
    city : str
    username: str
    hashed_password : str

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id : UUID
    tickets : List[TicketOut] = []
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

############## CINE

class CinemaBase(BaseModel):
    name : str
    city : str
    address : str

class CinemaOut(CinemaBase):
    id : UUID
    class Config:
        from_attributes = True

class CinemaCreate(CinemaBase):
    pass

################## PELÍCULA
class MovieBase(BaseModel):
    title : str
    genre : str
    duration_minutes : int

class MovieOut(MovieBase):
    id : UUID
    class Config:
        from_attributes = True

class MovieCreate(MovieBase):
    pass


