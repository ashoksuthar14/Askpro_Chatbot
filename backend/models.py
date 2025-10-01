import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///askme_pro.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
	Base.metadata.create_all(bind=engine)


class Session(Base):
	__tablename__ = "sessions"
	id = Column(String, primary_key=True)
	created_at = Column(DateTime, default=datetime.utcnow)
	messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
	__tablename__ = "messages"
	id = Column(Integer, primary_key=True)
	session_id = Column(String, ForeignKey("sessions.id"))
	role = Column(String)
	text = Column(Text)
	timestamp = Column(DateTime, default=datetime.utcnow)
	session = relationship("Session", back_populates="messages")


class Document(Base):
	__tablename__ = "documents"
	id = Column(String, primary_key=True)
	title = Column(String)
	path = Column(String)
	text = Column(Text)
	created_at = Column(DateTime, default=datetime.utcnow)
	chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
	__tablename__ = "chunks"
	id = Column(String, primary_key=True)
	document_id = Column(String, ForeignKey("documents.id"))
	text = Column(Text)
	start = Column(Integer)
	end = Column(Integer)
	created_at = Column(DateTime, default=datetime.utcnow)
	document = relationship("Document", back_populates="chunks")
