# LangChain service for retrieval and generation
# This file integrates LangChain components for document processing, retrieval, and text generation

from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import PGVector
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory, PostgresChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType, Tool
import os
from typing import List, Optional
import tempfile
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PGVECTOR_CONNECTION_STRING = os.getenv("PGVECTOR_CONNECTION_STRING", "postgresql://postgres:postgres@localhost:5432/langchain_agents")

class DocumentProcessor:
    """Handles document loading and chunking"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
    def extract_text(self, content: bytes, filename: str) -> str:
        """Extracts text from uploaded document content"""
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(content)
            temp_path = temp.name
        
        try:
            if filename.lower().endswith('.pdf'):
                loader = PyPDFLoader(temp_path)
                docs = loader.load()
                text = "\n\n".join([doc.page_content for doc in docs])
            else:
                # Assume text file
                loader = TextLoader(temp_path)
                docs = loader.load()
                text = docs[0].page_content
                
            return text
        finally:
            # Clean up temp file
            os.unlink(temp_path)
    
    def process_document(self, document):
        """Process document and create embeddings"""
        # Split text into chunks
        texts = self.text_splitter.split_text(document.content)
        
        # Create embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Create vector store
        vectorstore = PGVector.from_texts(
            texts=texts,
            embedding=embeddings,
            connection_string=PGVECTOR_CONNECTION_STRING,
            collection_name=f"user_{document.user_id}_docs"
        )
        
        return vectorstore


class EmbeddingService:
    """Generates vector embeddings for text"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    def get_embeddings(self, texts: List[str]):
        """Generate embeddings for a list of texts"""
        return self.embeddings.embed_documents(texts)
    
    def get_query_embedding(self, query: str):
        """Generate embedding for a query string"""
        return self.embeddings.embed_query(query)


class VectorStoreService:
    """Manages vector database operations"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    def get_vectorstore_for_user(self, user_id: int):
        """Get vector store for a specific user"""
        return PGVector(
            connection_string=PGVECTOR_CONNECTION_STRING,
            embedding_function=self.embeddings,
            collection_name=f"user_{user_id}_docs"
        )
    
    def similarity_search(self, query: str, user_id: int, k: int = 4):
        """Perform similarity search for a query"""
        vectorstore = self.get_vectorstore_for_user(user_id)
        return vectorstore.similarity_search(query, k=k)


class RetrievalService:
    """Implements retrieval augmented generation"""
    
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4o-mini",
            openai_api_key=OPENAI_API_KEY
        )
    
    def get_retrieval_chain(self, user_id: int):
        """Initialize RetrievalQAChain with documents"""
        vectorstore = self.vector_store_service.get_vectorstore_for_user(user_id)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        
        # Create the retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        return qa_chain


class ConversationService:
    """Manages conversational context and memory"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4o-mini",
            openai_api_key=OPENAI_API_KEY
        )
    
    def get_conversation_chain(self, user_id: int, conversation_id: str):
        """Initialize chain for stateful conversations"""
        # Create or get conversation memory
        message_history = PostgresChatMessageHistory(
            connection_string=PGVECTOR_CONNECTION_STRING,
            session_id=conversation_id,
            table_name="conversation_history"
        )
        
        memory = ConversationBufferMemory(
            chat_memory=message_history,
            return_messages=True
        )
        
        # Create the conversation chain
        conversation = ConversationChain(
            llm=self.llm,
            memory=memory,
            verbose=True
        )
        
        return conversation
    
    def get_user_conversations(self, user_id: int):
        """Retrieve conversation history for a user"""
        # This would query the database for all conversation history
        # associated with the user
        # Simplified implementation:
        return []


class LanguageModelService:
    """Provides interface to underlying LLM APIs"""
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.7):
        self.llm = ChatOpenAI(
            temperature=temperature,
            model_name=model_name,
            openai_api_key=OPENAI_API_KEY
        )
    
    def generate_response(self, prompt: str):
        """Generate response from the language model"""
        return self.llm.predict(prompt)
    
    def generate_structured_output(self, prompt: str, output_schema: dict):
        """Generate structured output based on schema"""
        # This would use function calling or other techniques
        # to generate structured output
        return self.llm.predict(prompt)


class AgentService:
    """Combines tools and chains into goal-directed agents"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4.1",
            openai_api_key=OPENAI_API_KEY
        )
        self.retrieval_service = RetrievalService()
        self.vector_store_service = VectorStoreService()
    
    def get_guidance_chain(self, user_id: int):
        """Initialize chain for personalized guidance"""
        # Create tools
        search_tool = Tool(
            name="DocumentSearch",
            func=lambda q: self.vector_store_service.similarity_search(q, user_id),
            description="Search the user's documents for relevant information"
        )
        
        # Create agent
        agent = initialize_agent(
            tools=[search_tool],
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True
        )
        
        return agent
    
    def get_agent_with_tools(self, user_id: int, tools: List[Tool]):
        """Create an agent with specified tools"""
        agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True
        )
        
        return agent 