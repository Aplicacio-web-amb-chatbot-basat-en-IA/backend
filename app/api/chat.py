from fastapi import APIRouter, Depends
from pydantic import BaseModel
import time
import logging
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.services.retrieval_service import (
    build_document_response,
    find_top_document_chunks,
)

router = APIRouter()

logging.basicConfig(level=logging.INFO)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(
    request: ChatRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start_time = time.time()

    document_chunks = find_top_document_chunks(db, request.message)

    if document_chunks:
        reply = build_document_response(document_chunks)
    else:
        reply = (
            "No he encontrado informacion relacionada en la base de datos. "
            "Prueba con otras palabras o anade mas documentos en docs."
        )

    end_time = time.time()
    response_time = end_time - start_time

    logging.info(
        f"User={user.username} | Time={response_time:.3f}s | Question={request.message}"
    )

    return {
        "reply": reply,
        "response_time": round(response_time, 3)
    }
