from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import ChatMessage, ChatSession


DEFAULT_CHAT_TITLE = "Nuevo chat"


def _normalize_title(title: str | None) -> str:
    cleaned = (title or "").strip()
    return cleaned or DEFAULT_CHAT_TITLE


def build_chat_title_from_message(message: str) -> str:
    cleaned = " ".join(message.strip().split())
    if not cleaned:
        return DEFAULT_CHAT_TITLE
    if len(cleaned) <= 60:
        return cleaned
    return cleaned[:57].rstrip() + "..."


def create_chat_session(db: Session, user_id: int, title: str | None = None) -> ChatSession:
    chat = ChatSession(
        user_id=user_id,
        title=_normalize_title(title),
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chat_session_for_user(db: Session, user_id: int, chat_id: int) -> ChatSession | None:
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == chat_id, ChatSession.user_id == user_id)
        .first()
    )


def list_chat_sessions_for_user(db: Session, user_id: int) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
        .all()
    )


def list_chat_messages(db: Session, chat_id: int) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )


def count_chat_messages(db: Session, chat_id: int) -> int:
    return db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).count()


def get_last_chat_message(db: Session, chat_id: int) -> ChatMessage | None:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .first()
    )


def update_chat_title(db: Session, chat: ChatSession, title: str) -> ChatSession:
    chat.title = _normalize_title(title)
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(chat)
    return chat


def save_chat_message(db: Session, chat: ChatSession, role: str, content: str) -> ChatMessage:
    message = ChatMessage(
        chat_id=chat.id,
        role=role,
        content=content.strip(),
    )
    db.add(message)
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(message)
    db.refresh(chat)
    return message


def delete_chat_session(db: Session, chat: ChatSession) -> None:
    db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).delete()
    db.delete(chat)
    db.commit()

