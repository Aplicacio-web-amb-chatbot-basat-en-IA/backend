from sqlalchemy import text


def ensure_user_schema(engine) -> None:
    with engine.begin() as connection:
        user_columns = connection.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'users'
                """
            )
        ).scalars().all()

        if user_columns and "email" not in user_columns:
            connection.execute(text("DROP TABLE IF EXISTS token_blacklist"))
            connection.execute(text("DROP TABLE IF EXISTS users"))


def ensure_document_chunk_schema(engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE document_chunks
                ADD COLUMN IF NOT EXISTS embedding TEXT
                """
            )
        )
        connection.execute(
            text(
                """
                ALTER TABLE document_chunks
                ADD COLUMN IF NOT EXISTS embedding_model VARCHAR
                """
            )
        )
