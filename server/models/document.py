# Document model for storing knowledge base items
# This file defines the SQLAlchemy ORM model for documents and their embeddings

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from datetime import datetime
import uuid

from server.models.db import Base, db_session
from server.models.user import User

class Document(Base):
    """SQLAlchemy model for document metadata"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    owner = relationship("User")


class DocumentChunk(Base):
    """SQLAlchemy model for document chunks"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text, nullable=False)
    embedding_vector = Column(ARRAY(FLOAT))  # Vector embeddings 
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


def create_document(title, source, content, user_id):
    """Factory method to create new document with metadata"""
    document = Document(
        title=title,
        source=source,
        content=content,
        user_id=user_id
    )
    return document


def chunk_document(document, chunk_size=1000, overlap=200):
    """Divides document into chunks for embedding"""
    content = document.content
    chunks = []
    
    # Simple chunking by character count
    for i in range(0, len(content), chunk_size - overlap):
        chunk_content = content[i:i + chunk_size]
        if len(chunk_content) < 50:  # Skip very small chunks
            continue
            
        chunk = DocumentChunk(
            document_id=document.id,
            content=chunk_content
        )
        chunks.append(chunk)
    
    return chunks


def search_similar(query_embedding, limit=5):
    """Finds similar document chunks using vector similarity"""
    # Using PostgreSQL's vector similarity search with dot product
    # This requires the pgvector extension
    chunks = db_session.execute(
        "SELECT id, content, document_id FROM document_chunks "
        "ORDER BY embedding_vector <=> :query_embedding LIMIT :limit",
        {"query_embedding": query_embedding, "limit": limit}
    ).fetchall()
    
    return chunks


def get_documents_by_user(user_id):
    """Query helper to find documents by user ID"""
    return db_session.query(Document).filter(Document.user_id == user_id).all()

# The model includes:
# - Vector embedding storage for similarity search
# - Document chunking for efficient retrieval
# - Metadata tracking for document sources
# - User ownership and permissions 