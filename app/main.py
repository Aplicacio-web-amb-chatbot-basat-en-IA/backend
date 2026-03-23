from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine
from app.database.models import Base
from app.api import auth
from app.api.auth import get_current_user

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Backend running"}

#nomes el chat pot fer loggin
@app.post("/chat")
def chat(request: ChatRequest, user=Depends(get_current_user)):
    user_message = request.message

    reply = f"{user.username} diu: {user_message}"

    return {
        "reply": reply
    }