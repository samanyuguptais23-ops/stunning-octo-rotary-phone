from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import uuid

engine = create_engine("sqlite:///pulselink.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, default="general")  # general / sos / resource / voice
    priority = Column(Integer, default=4)     # 1=SOS, 2=urgent, 3=resource, 4=general
    content = Column(Text, default="")
    sender = Column(String, default="unknown")
    sender_name = Column(String, default="Anonymous")
    audio_url = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()