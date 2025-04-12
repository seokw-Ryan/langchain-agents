# AI Agent endpoints for research and guidance
# This file defines API routes for interacting with the LangChain-powered AI agent

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid

from server.models.db import get_db
from server.models.user import User
from server.models.document import Document, create_document
from server.services.langchain_service import (
    DocumentProcessor, 
    RetrievalService, 
    ConversationService,
    AgentService
)
from server.routers.auth import get_current_user

router = APIRouter()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    conversation_id: Optional[str] = None

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[dict]

@router.post("/research", response_model=QueryResponse)
async def research(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform document retrieval and answer questions"""
    # Initialize the retrieval chain
    retrieval_service = RetrievalService()
    retrieval_chain = retrieval_service.get_retrieval_chain(user_id=current_user.id)
    
    # Process the query
    result = retrieval_chain({"query": query_request.query})
    
    # Format the response
    response = QueryResponse(
        response=result["result"],
        sources=result.get("source_documents", [])
    )
    
    return response

@router.post("/guidance", response_model=QueryResponse)
async def guidance(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Provide personalized life guidance"""
    # Initialize the guidance chain
    agent_service = AgentService()
    guidance_chain = agent_service.get_guidance_chain(user_id=current_user.id)
    
    # Process the query
    result = guidance_chain({"query": query_request.query})
    
    # Format the response
    response = QueryResponse(
        response=result["result"]
    )
    
    return response

@router.post("/chat", response_model=QueryResponse)
async def chat(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle multi-turn conversations with context"""
    # Initialize the conversation service
    conversation_service = ConversationService()
    
    # Get or create conversation chain
    conversation_id = query_request.conversation_id or str(uuid.uuid4())
    conversation_chain = conversation_service.get_conversation_chain(
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    
    # Process the query
    result = conversation_chain({"input": query_request.query})
    
    # Format the response
    response = QueryResponse(
        response=result["output"],
        conversation_id=conversation_id
    )
    
    return response

@router.get("/history", response_model=List[ConversationHistory])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve conversation history"""
    conversation_service = ConversationService()
    histories = conversation_service.get_user_conversations(user_id=current_user.id)
    
    return histories

@router.post("/document", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    source: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process new documents for the knowledge base"""
    # Process the document
    document_processor = DocumentProcessor()
    content = await file.read()
    
    # Extract text from the document
    text = document_processor.extract_text(content, file.filename)
    
    # Create document in database
    document = create_document(
        title=title,
        source=source or file.filename,
        content=text,
        user_id=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process and create embeddings
    document_processor.process_document(document)
    
    return {"message": "Document uploaded and processed successfully", "document_id": document.id} 