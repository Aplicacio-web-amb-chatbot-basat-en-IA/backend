from fastapi import APIRouter, Depends
from pydantic import BaseModel
import time
import logging

from app.api.auth import get_current_user
from app.services.ai_service import generate_response

router = APIRouter()

logging.basicConfig(level=logging.INFO)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest, user=Depends(get_current_user)):
    start_time = time.time()

    reply = generate_response(request.message)

    end_time = time.time()
    response_time = end_time - start_time

    logging.info(
        f"User={user.username} | Time={response_time:.3f}s | Question={request.message}"
    )

    return {
        "reply": reply,
        "response_time": round(response_time, 3)
    }
