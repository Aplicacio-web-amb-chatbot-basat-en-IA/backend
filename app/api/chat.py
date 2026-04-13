from fastapi import APIRouter,
from pydantic import BaseModel

from app.api.auth import get_current_user
from app.services.ai_service import generate_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(request: ChatRequest, user=(get_current_user)):

    prompt = f"""
    Eres un NPC experto en Minecraft.

    IMPORTANTE:
    - Responde siempre en español
    - Da solo información real y correcta de Minecraft
    - No inventes objetos ni mecánicas inexistentes
    - Responde de forma clara, corta y útil
    - Utiliza un máximo de 3 frases
    - Si es posible, explica los pasos de forma simple
    - No hace falta que respongas el nombre del usuario que hace la pregunta
    Usuario: {user.username}
    Pregunta: {request.message}
    """

    reply = generate_response(prompt)

    return {
        "reply": reply
    }