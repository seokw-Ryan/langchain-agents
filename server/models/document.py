# Document model for storing knowledge base items
# This file defines the SQLAlchemy ORM model for documents and their embeddings

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from datetime import datetime
import uuid

from server.models.db import Base, db_session

class Document(Base):
    """SQLAlchemy model for document metadata"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    filename = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    owner = relationship("User")


class DocumentChunk(Base):
    """SQLAlchemy model for document chunks with embeddings"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text)
    embedding = Column(ARRAY(FLOAT))
    chunk_order = Column(Integer)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


def create_document(title, content, user_id, filename=None, db=None):
    """Factory method to create a new document"""
    document = Document(
        title=title,
        content=content,
        filename=filename,
        user_id=user_id
    )
    
    if db:
        db.add(document)
        db.commit()
        db.refresh(document)
    
    return document


def get_document_by_id(document_id, db=None):
    """Query helper to find document by ID"""
    if db:
        return db.query(Document).filter(Document.id == document_id).first()
    return db_session.query(Document).filter(Document.id == document_id).first()


def get_user_documents(user_id, db=None):
    """Query helper to get all documents for a user"""
    if db:
        return db.query(Document).filter(Document.user_id == user_id).all()
    return db_session.query(Document).filter(Document.user_id == user_id).all()

# The model includes:
# - Vector embedding storage for similarity search
# - Document chunking for efficient retrieval
# - Metadata tracking for document sources
# - User ownership and permissions 