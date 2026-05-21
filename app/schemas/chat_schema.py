from datetime import datetime

from pydantic import BaseModel


class ChatCreateRequest(BaseModel):
    title: str | None = None


class ChatMessageCreateRequest(BaseModel):
    message: str


class ChatSendRequest(BaseModel):
    chat_id: int
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime | None = None


class ChatSummaryResponse(BaseModel):
    id: int
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    message_count: int
    last_message_preview: str | None = None


class ChatDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    messages: list[ChatMessageResponse]


class ChatSendResponse(BaseModel):
    chat_id: int
    reply: str
    response_time: float
    user_message_id: int
    assistant_message_id: int
