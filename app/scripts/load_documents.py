import os
from pathlib import Path

from app.database.database import SessionLocal, engine
from app.database.schema_utils import ensure_document_chunk_schema
from app.database.models import Base, DocumentChunk
from app.services.embedding_service import (
    EMBEDDING_MODEL,
    generate_embeddings,
    serialize_embedding,
)
from app.services.retrieval_service import normalize_text


DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "60"))
TARGET_CHUNK_CHARS = 420
MAX_LINES_PER_CHUNK = 5


def split_text_into_chunks(text: str) -> list[str]:
    normalized_text = text.replace("\r\n", "\n")

    if "---" in normalized_text:
        chunks = [chunk.strip() for chunk in normalized_text.split("---") if chunk.strip()]
        if chunks:
            return chunks

    paragraphs = [paragraph.strip() for paragraph in normalized_text.split("\n\n") if paragraph.strip()]
    if len(paragraphs) > 1:
        return paragraphs

    lines = [line.strip() for line in normalized_text.split("\n") if line.strip()]
    if len(lines) > 1:
        grouped_chunks = []
        current_lines = []
        current_length = 0

        for line in lines:
            projected_length = current_length + len(line) + (1 if current_lines else 0)
            if current_lines and (
                projected_length > TARGET_CHUNK_CHARS
                or len(current_lines) >= MAX_LINES_PER_CHUNK
            ):
                grouped_chunks.append("\n".join(current_lines))
                current_lines = []
                current_length = 0

            current_lines.append(line)
            current_length += len(line) + (1 if current_lines else 0)

        if current_lines:
            grouped_chunks.append("\n".join(current_lines))

        if grouped_chunks:
            return grouped_chunks

    if paragraphs:
        return paragraphs

    return [normalized_text.strip()] if normalized_text.strip() else []


def load_documents() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_document_chunk_schema(engine)

    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"No existe la carpeta docs: {DOCS_DIR}")

    txt_files = sorted(DOCS_DIR.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No se han encontrado archivos .txt en {DOCS_DIR}")
    current_sources = {file_path.name for file_path in txt_files}

    db = SessionLocal()

    try:
        db.query(DocumentChunk).filter(~DocumentChunk.source.in_(current_sources)).delete(
            synchronize_session=False
        )
        db.commit()

        total_chunks = 0

        for file_path in txt_files:
            source_name = file_path.name
            title = file_path.stem.replace("_", " ").replace("-", " ").strip().title()
            content = file_path.read_text(encoding="utf-8")
            chunks = split_text_into_chunks(content)

            existing_rows = {
                row.chunk_index: row
                for row in db.query(DocumentChunk)
                .filter(DocumentChunk.source == source_name)
                .all()
            }

            for start in range(0, len(chunks), BATCH_SIZE):
                batch_items = []
                batch_indices = []

                for offset, chunk in enumerate(chunks[start:start + BATCH_SIZE], start=start + 1):
                    row = existing_rows.get(offset)
                    normalized_chunk = normalize_text(chunk)
                    needs_refresh = (
                        row is None
                        or row.content != chunk
                        or row.content_normalized != normalized_chunk
                        or not row.embedding
                        or row.embedding_model != EMBEDDING_MODEL
                    )
                    if needs_refresh:
                        batch_items.append(chunk)
                        batch_indices.append(offset)

                if not batch_items:
                    continue

                embeddings = generate_embeddings(batch_items)

                for chunk_index, chunk_text, embedding_values in zip(
                    batch_indices,
                    batch_items,
                    embeddings,
                ):
                    normalized_chunk = normalize_text(chunk_text)
                    row = existing_rows.get(chunk_index)

                    if row is None:
                        row = DocumentChunk(
                            source=source_name,
                            title=title,
                            chunk_index=chunk_index,
                            content=chunk_text,
                            content_normalized=normalized_chunk,
                            embedding=serialize_embedding(embedding_values),
                            embedding_model=EMBEDDING_MODEL,
                        )
                        db.add(row)
                        existing_rows[chunk_index] = row
                    else:
                        row.title = title
                        row.content = chunk_text
                        row.content_normalized = normalized_chunk
                        row.embedding = serialize_embedding(embedding_values)
                        row.embedding_model = EMBEDDING_MODEL

                db.commit()

            db.query(DocumentChunk).filter(
                DocumentChunk.source == source_name,
                DocumentChunk.chunk_index > len(chunks),
            ).delete(synchronize_session=False)
            db.commit()
            total_chunks += len(chunks)

        print(f"Archivos procesados: {len(txt_files)}")
        print(f"Fragmentos guardados: {total_chunks}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_documents()
