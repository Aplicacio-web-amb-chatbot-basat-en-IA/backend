from sqlalchemy import Column, Integer, String
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    content_normalized = Column(String, nullable=False)
