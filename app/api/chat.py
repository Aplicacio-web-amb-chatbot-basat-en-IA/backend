from fastapi import APIRouter, Depends
from pydantic import BaseModel
import time
import logging

from app.api.auth import get_current_user
from app.services.ai_service import generate_response

router = APIRouter()

# Configurar logs
logging.basicConfig(level=logging.INFO)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(request: ChatRequest, user=Depends(get_current_user)):

    start_time = time.time()  # ⏱️ INICI

    prompt = f"""
    Eres un experto en Minecraft Vanilla.

    Reglas:
    - No inventes información.
    - No hables de mods.
    - Responde claro y breve (máx 3 frases).
    - Si no sabes algo, dilo.

    Pregunta:
    {request.message}
    """

    reply = generate_response(prompt)

    end_time = time.time()  # ⏱️ FINAL
    response_time = end_time - start_time

    # Log per terminal (important pel TFG)
    logging.info(
        f"User={user.username} | Time={response_time:.3f}s | Question={request.message}"
    )

    return {
        "reply": reply,
        "response_time": round(response_time, 3)  # 👈 enviat al frontend
    }