from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database.models import User, TokenBlacklist
from jose import JWTError, jwt
from app.core.security import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, username: str, password: str):

    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
        return None

    new_user = User(
        username=username,
        password_hash=hash_password(password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

#lggggin
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user

#token a blacklist
def blacklist_token(db: Session, token: str):
    blacklisted = TokenBlacklist(token=token)
    db.add(blacklisted)
    db.commit()

#token amb user
def get_user_from_token(db: Session, token: str):

    blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    if blacklisted:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            return None

    except JWTError:
        return None

    return db.query(User).filter(User.username == username).first()