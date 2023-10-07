from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class ResponseModel(BaseModel):
    id: int
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    email: EmailStr = Field(max_length=120)
    birthday: date
    description: str | None = None

    class Config:
        from_attributes = True

class ContactModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    email: EmailStr = Field(max_length=120)
    birthday: date
    description: str | None = None

    class Config:
        from_attributes = True

class UserModel(BaseModel): 
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=5, max_length=16)

class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user: UserDb
    detail: str = 'User successfully created'

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RequestEmail(BaseModel):
    email: EmailStr