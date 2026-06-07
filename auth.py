from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from pwdlib import PasswordHash
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from sqlalchemy import select
import models
from typing import Annotated
import hashlib
import secrets

password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

def hash_password(password:str)->str:
    return password_hasher.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return password_hasher.verify(plain_password,hashed_password)

def create_access_token(data:dict,expires_delta :timedelta|None = None) -> str:
    """ Create A JWT Access TOKEN"""
    to_encode=data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.acess_token_expire_minutes)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,settings.secret_key.get_secret_value(),algorithm=settings.algorithm)
    return encoded_jwt

def verify_access_token(token:str)->str|None:
    try:
        payload = jwt.decode(token,settings.secret_key.get_secret_value(),algorithms=[settings.algorithm],options={"required":["exp","sub"]})
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:Annotated[AsyncSession,Depends(get_db)])-> models.User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired Token",headers={"WWW-Authenticate":"Bearer"}) 
    #VALIDATE USER ID against Integer -> defense against malformed JWT
    try:
        user_id_int = int(user_id)
    except(ValueError,TypeError):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired Token",headers={"WWW-Authenticate":"Bearer"}) 
    result = await db.execute(select(models.User).where(models.User.id == user_id_int))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "user not found",headers={"WWW-Authenticate":"Bearer"})
    return user    

CurrentUser = Annotated[models.User,Depends(get_current_user)]  

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def hash_reset_token(token:str )-> str:
    return hashlib.sha256(token.encode()).hexdigest()


