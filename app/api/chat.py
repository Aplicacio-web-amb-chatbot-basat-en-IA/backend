import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.database.models import ChatSession
from app.schemas.chat_schema import (
    ChatCreateRequest,
    ChatDetailResponse,
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSendRequest,
    ChatSendResponse,
    ChatSummaryResponse,
)
from app.services.chat_session_service import (
    DEFAULT_CHAT_TITLE,
    build_chat_title_from_message,
    count_chat_messages,
    create_chat_session,
    delete_chat_session,
    get_chat_session_for_user,
    get_last_chat_message,
    list_chat_messages,
    list_chat_sessions_for_user,
    save_chat_message,
    update_chat_title,
)
from app.services.retrieval_service import (
    build_document_response,
    find_top_document_chunks,
)
from app.services.translation_service import detect_input_language

router = APIRouter()

logging.basicConfig(level=logging.INFO)


def _generate_reply(db: Session, message: str) -> tuple[str, float]:
    start_time = time.time()
    document_chunks = find_top_document_chunks(db, message, limit=5)

    if document_chunks:
        reply = build_document_response(document_chunks, message)
    else:
        reply = (
            "No he encontrado informacion relacionada en la base de datos. "
            "Prueba con otras palabras o anade mas documentos en docs."
        )

    response_time = time.time() - start_time
    return reply, response_time


def _serialize_message(message) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


def _serialize_chat_summary(db: Session, chat: ChatSession) -> ChatSummaryResponse:
    message_count = count_chat_messages(db, chat.id)
    last_message = get_last_chat_message(db, chat.id)
    return ChatSummaryResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        message_count=message_count,
        last_message_preview=(last_message.content[:100] if last_message else None),
    )


def _serialize_chat_detail(db: Session, chat: ChatSession) -> ChatDetailResponse:
    messages = list_chat_messages(db, chat.id)
    return ChatDetailResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[_serialize_message(message) for message in messages],
    )


def _send_message_to_chat(
    db: Session,
    chat: ChatSession,
    user,
    message_text: str,
) -> ChatSendResponse:
    normalized_message = message_text.strip()
    if not normalized_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if detect_input_language(normalized_message) != "es":
        raise HTTPException(
            status_code=400,
            detail="Only Spanish questions are supported right now",
        )

    existing_count = count_chat_messages(db, chat.id)
    if existing_count == 0 and chat.title == DEFAULT_CHAT_TITLE:
        chat = update_chat_title(db, chat, build_chat_title_from_message(normalized_message))

    user_message = save_chat_message(db, chat, "user", normalized_message)
    reply, response_time = _generate_reply(db, normalized_message)
    assistant_message = save_chat_message(db, chat, "assistant", reply)

    logging.info(
        f"User={user.username} | Chat={chat.id} | Lang=es | Time={response_time:.3f}s | Question={normalized_message}"
    )

    return ChatSendResponse(
        chat_id=chat.id,
        reply=reply,
        response_time=round(response_time, 3),
        user_message_id=user_message.id,
        assistant_message_id=assistant_message.id,
    )


@router.get("/chats", response_model=list[ChatSummaryResponse])
def list_user_chats(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chats = list_chat_sessions_for_user(db, user.id)
    return [_serialize_chat_summary(db, chat) for chat in chats]


@router.post("/chats", response_model=ChatSummaryResponse)
def create_chat(
    payload: ChatCreateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = create_chat_session(db, user.id, payload.title)
    return _serialize_chat_summary(db, chat)


@router.get("/chats/{chat_id}", response_model=ChatDetailResponse)
def get_chat_detail(
    chat_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = get_chat_session_for_user(db, user.id, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return _serialize_chat_detail(db, chat)


@router.delete("/chats/{chat_id}")
def delete_chat(
    chat_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = get_chat_session_for_user(db, user.id, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    delete_chat_session(db, chat)
    return {"message": "Chat deleted"}


@router.post("/chats/{chat_id}/messages", response_model=ChatSendResponse)
def send_message_to_existing_chat(
    chat_id: int,
    payload: ChatMessageCreateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat = get_chat_session_for_user(db, user.id, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return _send_message_to_chat(db, chat, user, payload.message)


@router.post("/chat", response_model=ChatSendResponse)
def chat(
    request: ChatSendRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    chat_session = get_chat_session_for_user(db, user.id, request.chat_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat not found")

    return _send_message_to_chat(db, chat_session, user, request.message)
