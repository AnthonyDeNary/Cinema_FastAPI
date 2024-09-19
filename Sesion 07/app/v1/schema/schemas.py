from pydantic import BaseModel
from uuid import UUID


#Sirve como un espejo de models.py
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
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str