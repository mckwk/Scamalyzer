from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

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
    bert_label = Column(String, nullable=True)
    bert_confidence = Column(Float, nullable=True)
    bilstm_label = Column(String, nullable=True)
    bilstm_confidence = Column(Float, nullable=True)
    xgboost_label = Column(String, nullable=True)
    xgboost_confidence = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)