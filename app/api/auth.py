from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.schemas.user_schema import UserRegister, UserChangePassword, UserChangeUsername, UserProfile
from app.database.database import get_db
from app.services.auth_service import create_user, authenticate_user, get_user_from_token
from app.core.security import create_access_token
from app.services.auth_service import blacklist_token, change_password, change_username

from pydantic import BaseModel

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):

    new_user = create_user(db, user.email, user.username, user.password)

    if not new_user:
        raise HTTPException(status_code=400, detail="Email or username already exists")

    return {
        "message": "User created",
        "email": new_user.email,
        "username": new_user.username
    }

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": db_user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_user_from_token(db, token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user


@router.get("/me", response_model=UserProfile)
def get_me(current_user=Depends(get_current_user)):
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
    )


@router.post("/change-username")
def update_username(
    payload: UserChangeUsername,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user, status = change_username(db, current_user, payload.new_username)

    if status == "invalid_username":
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    if status == "username_exists":
        raise HTTPException(status_code=400, detail="Username already exists")

    return {
        "message": "Username updated" if status == "updated" else "Username unchanged",
        "username": updated_user.username,
    }


@router.post("/change-password")
def update_password(
    payload: UserChangePassword,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated, status = change_password(
        db,
        current_user,
        payload.current_password,
        payload.new_password,
    )

    if not updated and status == "invalid_current_password":
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    return {"message": "Password updated"}

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    blacklist_token(db, token)

    return {"message": "Logged out"}
