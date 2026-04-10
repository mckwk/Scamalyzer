import os
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Float, Integer, String,
                        create_engine, inspect, text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

os.makedirs("database", exist_ok=True)

# SQLite database setup
DATABASE_URL = "sqlite:///database/scamalyzer.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    language = Column(String, nullable=False, default="en", index=True)
    bert_label = Column(String, nullable=True)
    bert_confidence = Column(Float, nullable=True)
    bilstm_label = Column(String, nullable=True)
    bilstm_confidence = Column(Float, nullable=True)
    xgboost_label = Column(String, nullable=True)
    xgboost_confidence = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)  # manual verification
    used_for_training = Column(Boolean, default=False)  # retraining usage


Base.metadata.create_all(bind=engine)


def ensure_schema():
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("messages")}

    if "language" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE messages ADD COLUMN language VARCHAR DEFAULT 'en'"))
            connection.execute(
                text("UPDATE messages SET language = 'en' WHERE language IS NULL"))


ensure_schema()
