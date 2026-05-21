from sqlalchemy.orm import Session
from sqlalchemy import or_
from passlib.context import CryptContext
from app.database.models import User, TokenBlacklist
from jose import JWTError, jwt
from app.core.security import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def normalize_email(email: str) -> str:
    return email.strip().lower()

def normalize_username(username: str) -> str:
    return username.strip()

def create_user(db: Session, email: str, username: str, password: str):
    normalized_email = normalize_email(email)
    normalized_username = normalize_username(username)

    existing_user = db.query(User).filter(
        or_(
            User.email == normalized_email,
            User.username == normalized_username,
        )
    ).first()

    if existing_user:
        return None

    new_user = User(
        email=normalized_email,
        username=normalized_username,
        password_hash=hash_password(password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def change_username(db: Session, user: User, new_username: str):
    normalized_username = normalize_username(new_username)

    if not normalized_username:
        return None, "invalid_username"

    if normalized_username == user.username:
        return user, "unchanged"

    existing_user = db.query(User).filter(User.username == normalized_username).first()
    if existing_user:
        return None, "username_exists"

    user.username = normalized_username
    db.commit()
    db.refresh(user)
    return user, "updated"


def change_password(db: Session, user: User, current_password: str, new_password: str):
    if not verify_password(current_password, user.password_hash):
        return False, "invalid_current_password"

    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return True, "updated"

def authenticate_user(db: Session, email: str, password: str):
    normalized_email = normalize_email(email)
    user = db.query(User).filter(User.email == normalized_email).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user

def blacklist_token(db: Session, token: str):
    blacklisted = TokenBlacklist(token=token)
    db.add(blacklisted)
    db.commit()

def get_user_from_token(db: Session, token: str):

    blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    if blacklisted:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            return None

    except JWTError:
        return None

    return db.query(User).filter(User.email == normalize_email(email)).first()
