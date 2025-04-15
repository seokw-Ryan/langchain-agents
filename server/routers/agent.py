# AI Agent endpoints for research and guidance
# This file defines API routes for interacting with the LangChain-powered AI agent

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from models.db import get_db
from models.user import User, get_user_by_username
from models.document import Document, create_document
from services.langchain_service import (
    DocumentProcessor,
    VectorStoreService,
    RetrievalService,
    ConversationService,
    AgentService
)
from routers.auth import get_current_user, get_optional_current_user
from uuid import uuid4

from models.user import create_user_with_username

router = APIRouter()

# Setup logging
logger = logging.getLogger("uvicorn")

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    username: Optional[str] = None  # Add username field for direct access

class QueryResponse(BaseModel):
    response: str
    sources: List[str] = []
    conversation_id: Optional[str] = None

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[dict]

# Helper function to get user by username for public endpoints
async def get_user_by_username_param(username: str, db: Session):
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is required"
        )
        
    user = get_user_by_username(username, db)
    if not user:
        # Create user if they don't exist
        user = create_user_with_username(username, db)
        
    return user

@router.post("/research", response_model=QueryResponse)
async def research(
    query_request: QueryRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Perform document retrieval and answer questions"""
    # Get user either from token or username param
    user = current_user
    if not user and query_request.username:
        user = await get_user_by_username_param(query_request.username, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Initialize the retrieval chain
    retrieval_service = RetrievalService()
    retrieval_chain = retrieval_service.get_retrieval_chain(user_id=user.id)
    
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Provide personalized life guidance"""
    # Get user either from token or username param
    user = current_user
    if not user and query_request.username:
        user = await get_user_by_username_param(query_request.username, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Initialize the guidance chain
    agent_service = AgentService()
    guidance_chain = agent_service.get_guidance_chain(user_id=user.id)
    
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
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Handle multi-turn conversations with context"""
    logger.info(f"DEBUG-CHAT-ROUTE: Received chat request with query: {query_request.query}")
    # Get user either from token or username param
    user = current_user
    if not user and query_request.username:
        user = await get_user_by_username_param(query_request.username, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    logger.info(f"DEBUG-CHAT-ROUTE: Authenticated user id: {user.id}")    
    # Initialize the conversation service
    conversation_service = ConversationService()
    
    # Get or create conversation chain
    conversation_id = query_request.conversation_id or str(uuid4())
    logger.info(f"DEBUG-CHAT-ROUTE: Using conversation_id: {conversation_id}")
    
    conversation_chain = conversation_service.get_conversation_chain(
        user_id=user.id,
        conversation_id=conversation_id
    )
    
    logger.info(f"DEBUG-CHAT-ROUTE: Got conversation chain, about to process query")
    
    try:
        # Process the query
        result = conversation_chain({"input": query_request.query})
        logger.info(f"DEBUG-CHAT-ROUTE: Query processed successfully, result: {result}")
        
        # Extract the output and create response object
        if "output" not in result:
            logger.error(f"DEBUG-CHAT-ROUTE: Missing 'output' key in result: {result}")
            raise ValueError(f"Missing 'output' key in result: {result}")
            
        # Format the response
        response = QueryResponse(
            response=result["output"],  # Map output to response
            conversation_id=conversation_id
        )
        
        logger.info(f"DEBUG-CHAT-ROUTE: Returning response: {response}")
        return response
    except Exception as e:
        logger.error(f"DEBUG-CHAT-ROUTE: ERROR processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/history", response_model=List[ConversationHistory])
async def get_history(
    username: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve conversation history"""
    user = current_user
    if not user and username:
        user = await get_user_by_username_param(username, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    conversation_service = ConversationService()
    histories = conversation_service.get_user_conversations(user_id=user.id)
    
    return histories

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    username: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and process a document for the knowledge base"""
    # Get user either from token or username param
    user = current_user
    if not user and username:
        user = await get_user_by_username_param(username, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Read file content
    content = await file.read()
    
    # Process document
    processor = DocumentProcessor()
    text_content = processor.extract_text(content, file.filename)
    
    # Create document record
    document = create_document(
        title=title,
        content=text_content,
        filename=file.filename,
        user_id=user.id,
        db=db
    )
    
    # Process and embed document
    processor.process_document(document)
    
    return {"message": "Document uploaded and processed successfully"} 