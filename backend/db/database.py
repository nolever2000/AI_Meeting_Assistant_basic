from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.config import get_settings

Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    source = Column(String(20), nullable=False, index=True)
    original_text = Column(String, nullable=False)
    translated_text = Column(String, nullable=False)


settings = get_settings()
engine = create_engine(settings.database_url, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def db_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def add_history(source: str, original_text: str, translated_text: str, timestamp: datetime) -> Conversation:
    with db_session() as session:
        record = Conversation(
            source=source,
            original_text=original_text,
            translated_text=translated_text,
            timestamp=timestamp,
        )
        session.add(record)
        session.flush()
        session.refresh(record)
        return record


def list_history(source: str | None = None, start: datetime | None = None, end: datetime | None = None) -> list[Conversation]:
    with db_session() as session:
        query = select(Conversation).order_by(Conversation.timestamp.asc())
        if source:
            query = query.where(Conversation.source == source)
        if start:
            query = query.where(Conversation.timestamp >= start)
        if end:
            query = query.where(Conversation.timestamp <= end)
        return list(session.scalars(query).all())
