from pydantic import BaseModel


from uuid import UUID


# Creamos el esquema en base a los campos del modelo de User
class UserBase(BaseModel):
    first_name: str
    last_name: str
    city: str
    username: str
    hashed_password: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID    # Debe ser tipo UUID ya que es el tipo de dato con el que se creo en la BD y que viene desde el Modelo

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
