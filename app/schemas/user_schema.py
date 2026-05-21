from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    username: str
    password: str


class UserChangeUsername(BaseModel):
    new_username: str


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str


class UserProfile(BaseModel):
    id: int
    email: str
    username: str
