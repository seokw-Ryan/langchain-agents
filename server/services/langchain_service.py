# LangChain service for retrieval and generation
# This file integrates LangChain components for document processing, retrieval, and text generation

from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import PGVector
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationChain as LangChainConversationChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory, PostgresChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType, Tool
import os
from typing import List, Optional, Dict, Any
import tempfile
import uuid
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Setup logging
logger = logging.getLogger("uvicorn")

# Load environment variables
logger.info("DEBUG-STARTUP: Loading environment variables")
load_dotenv()

# Initialize OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PGVECTOR_CONNECTION_STRING = os.getenv("PGVECTOR_CONNECTION_STRING", "postgresql://postgres:postgres@postgres:5432/langchain_agents")

# Debug environment
logger.info(f"DEBUG-STARTUP: OPENAI_API_KEY is {'set' if OPENAI_API_KEY else 'NOT SET'}")
if OPENAI_API_KEY:
    logger.info(f"DEBUG-STARTUP: OPENAI_API_KEY starts with {OPENAI_API_KEY[:5]} and ends with {OPENAI_API_KEY[-4:]}")
logger.info(f"DEBUG-STARTUP: PGVECTOR_CONNECTION_STRING is {'set' if PGVECTOR_CONNECTION_STRING else 'NOT SET'}")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Custom ConversationChain that uses OpenAI API directly
class ConversationChain(LangChainConversationChain):
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        logger.info(f"DEBUG-CHAIN: ConversationChain _call with inputs: {inputs}")
        try:
            # Get all unique memory variables used in prompt
            memory_keys = self.memory.memory_variables

            # Load memory variables
            memory_values = self.memory.load_memory_variables({})
            logger.info(f"DEBUG-CHAIN: Loaded memory variables: {memory_values}")
            
            # Prepare messages for OpenAI API
            messages = [{"role": "system", "content": "You are a helpful assistant."}]
            
            # Add history if available
            if 'history' in memory_values and memory_values['history']:
                # Convert LangChain message format to OpenAI format if needed
                for message in memory_values['history']:
                    if hasattr(message, 'type') and hasattr(message, 'content'):
                        role = "assistant" if message.type == "ai" else "user"
                        messages.append({"role": role, "content": message.content})
            
            # Add current user input
            messages.append({"role": "user", "content": inputs.get('input', '')})
            
            logger.info(f"DEBUG-CHAIN: Prepared messages for OpenAI API: {messages}")
            logger.info("DEBUG-CHAIN: About to call OpenAI API")
            
            # Call OpenAI API directly using the client
            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",  # Use the model specified in your ConversationService
                    messages=messages,
                    temperature=0.7
                )
                assistant_response = response.choices[0].message.content
                logger.info(f"DEBUG-CHAIN: Got response from OpenAI API: {assistant_response[:50]}...")
            except Exception as e:
                logger.error(f"DEBUG-CHAIN: ERROR in OpenAI API call: {str(e)}")
                raise
            
            # Save context - use only output key as expected by LangChain
            outputs = {"output": assistant_response}
            # Save the new message to memory
            self.memory.save_context(inputs, outputs)
            
            return outputs
        except Exception as e:
            logger.error(f"DEBUG-CHAIN: Unexpected error in conversation chain: {str(e)}")
            raise

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
            model_name="gpt-4.1-mini",
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
        logger.info("DEBUG-CONV-SERVICE: Initializing ConversationService")
        try:
            # We'll keep the LLM instance for compatibility with other code
            self.llm = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-4.1-mini",
                openai_api_key=OPENAI_API_KEY
            )
            logger.info(f"DEBUG-CONV-SERVICE: ChatOpenAI initialized with API key: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'None'}")
        except Exception as e:
            logger.error(f"DEBUG-CONV-SERVICE: ERROR initializing ChatOpenAI: {str(e)}")
            raise
    
    def get_conversation_chain(self, user_id: int, conversation_id: str):
        """Initialize chain for stateful conversations"""
        logger.info(f"DEBUG-CONV-SERVICE: get_conversation_chain called for user_id: {user_id}, conversation_id: {conversation_id}")
        try:
            # Uncomment and fix the PostgresChatMessageHistory if you want to use it
            # message_history = PostgresChatMessageHistory(
            #     connection_string=PGVECTOR_CONNECTION_STRING,
            #     session_id=conversation_id,
            #     table_name="conversation_history"
            # )
            
            # Use a regular memory buffer instead of PostgreSQL
            memory = ConversationBufferMemory(
                # chat_memory=message_history,
                return_messages=True
            )
            logger.info("DEBUG-CONV-SERVICE: Created ConversationBufferMemory")
            
            # Create the conversation chain
            conversation = ConversationChain(
                llm=self.llm,  # This will be ignored in our implementation
                memory=memory,
                verbose=True
            )
            logger.info("DEBUG-CONV-SERVICE: Created ConversationChain")
            
            return conversation
        except Exception as e:
            logger.error(f"DEBUG-CONV-SERVICE: ERROR in get_conversation_chain: {str(e)}")
            raise
    
    def get_user_conversations(self, user_id: int):
        """Retrieve conversation history for a user"""
        # This would query the database for all conversation history
        # associated with the user
        # Simplified implementation:
        return []


class LanguageModelService:
    """Provides interface to underlying LLM APIs"""
    
    def __init__(self, model_name: str = "gpt-4.1-mini", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
    
    def generate_response(self, prompt: str):
        """Generate response from the language model"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature
        )
        return response.choices[0].message.content
    
    def generate_structured_output(self, prompt: str, output_schema: dict):
        """Generate structured output based on schema"""
        # This would use function calling or other techniques
        # to generate structured output
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides structured output."},
            {"role": "user", "content": prompt}
        ]
        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature
        )
        return response.choices[0].message.content


class AgentService:
    """Combines tools and chains into goal-directed agents"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4.1-mini",
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