from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username : str = Field(min_length = 1, max_length = 50, description = 'Name of the author')
    email : EmailStr=Field(max_lenth = 120)


class UserCreate(UserBase):
    password: str  = Field(min_length = 8)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    username : str = Field(min_length = 1, max_length = 50)
    id : int 
    image_file: str | None
    image_path: str

class UserPrivate(UserPublic):
    email : EmailStr=Field(max_lenth = 120)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    username : Optional[str] = Field(default=None,min_length = 1, max_length = 50, description = 'Name of the author')
    email : Optional[EmailStr] = Field(default=None,max_lenth = 120)

class PostBase(BaseModel):
    title: str = Field(min_length = 1, max_length = 100, description = 'Title with min 1 char and max 100 char')
    content: str=Field(min_lenth = 1)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(default = None,min_length = 1, max_length = 100, description = 'Title with min 1 char and max 100 char')
    content: Optional[str]=Field(default = None,min_lenth = 1)


class PostCreate(PostBase):
    pass 

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes = True)

    id : int 
    date_posted : datetime
    author: UserPublic

class PaginatedPostResponse(BaseModel):
    posts: List[PostResponse]
    total : int 
    skip : int
    limit: int
    has_more: bool

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)