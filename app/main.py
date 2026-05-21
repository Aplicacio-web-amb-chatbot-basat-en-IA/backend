from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine
from app.database.schema_utils import ensure_document_chunk_schema, ensure_user_schema
from app.database.models import Base
from app.api import auth, builds, chat

load_dotenv()

app = FastAPI()

ensure_user_schema(engine)
Base.metadata.create_all(bind=engine)
ensure_document_chunk_schema(engine)

app.include_router(auth.router, prefix="/auth")
app.include_router(chat.router, prefix="/ai")
app.include_router(builds.router, prefix="/builds")

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
