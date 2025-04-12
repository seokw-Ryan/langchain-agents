# AI Agent tests for the LangChain integration
# This file contains tests for the AI agent endpoints and LangChain processes

# Test cases:
# - test_research_endpoint(): Tests the research API response format
# - test_guidance_endpoint(): Tests the guidance API functionality
# - test_chat_endpoint(): Tests conversation history and context management
# - test_document_upload(): Tests document processing and embedding
# - test_retrieval_accuracy(): Tests retrieval precision with test documents
# - test_conversation_memory(): Tests memory persistence across requests
# - test_agent_chain_integration(): Tests full agent workflow with chained steps

# Fixtures:
# - mock_language_model(): Mock LLM for deterministic testing
# - test_documents(): Sample documents for retrieval testing
# - vector_store(): Test vector store with sample embeddings
# - mock_chain(): LangChain test chain with controlled responses 