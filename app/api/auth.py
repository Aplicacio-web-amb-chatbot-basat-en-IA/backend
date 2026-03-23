from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.schemas.user_schema import UserRegister
from app.database.database import get_db
from app.services.auth_service import create_user, authenticate_user, get_user_from_token
from app.core.security import create_access_token
from app.services.auth_service import blacklist_token

from pydantic import BaseModel

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#login
class UserLogin(BaseModel):
    username: str
    password: str

#registrarse
@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):

    new_user = create_user(db, user.username, user.password)

    if not new_user:
        return {"error": "User already exists"}

    return {
        "message": "User created",
        "username": new_user.username
    }

#tornem el token
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": db_user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

#usuari q esta loggin (token)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_user_from_token(db, token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

#logout
@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    blacklist_token(db, token)

    return {"message": "Logged out"}