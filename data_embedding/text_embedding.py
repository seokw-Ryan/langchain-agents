import pandas as pd  
import tiktoken 
from openai import OpenAI  
from typing import List  
import os  
from dotenv import load_dotenv 
from pathlib import Path  

# Load environment variables from the specified .env file
dotenv_path = Path('../.env')  # Path to the .env file
load_dotenv(dotenv_path=dotenv_path)  # Load the .env file

# Get the OpenAI API key from the environment variables
openai_api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client
client = OpenAI()

# Define the embedding model and encoding settings
embedding_model = "text-embedding-3-small"  # The OpenAI model to use for embeddings
embedding_encoding = "cl100k_base"  # Encoding name for tokenization
max_tokens = 1500  # Maximum number of tokens for processing

# Read the scraped data from the CSV file
df = pd.read_csv("scraped.csv")
df.columns = ['title', 'text']  # Rename columns for clarity

# Initialize the tokenizer with the specified encoding
tokenizer = tiktoken.get_encoding(embedding_encoding)

# Drop rows where the 'text' column has NaN values
df = df.dropna(subset=['text'])

# Calculate the number of tokens for each row in the 'text' column
df['n_tokens'] = df['text'].apply(lambda x: len(tokenizer.encode(x)) if isinstance(x, str) else 0)

def split_into_many(text: str, max_tokens: int = 500) -> List[str]:
    """
    Splits the input text into smaller chunks of a maximum number of tokens.
    
    Parameters:
    - text: The input text to be split.
    - max_tokens: The maximum number of tokens allowed in each chunk.
    
    Returns:
    - List of text chunks with each chunk not exceeding the max_tokens limit.
    """
    # Split the text into sentences based on periods
    sentences = text.split('.')
    
    # Calculate the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

    chunks = []  # List to store the resulting text chunks
    tokens_so_far = 0  # Counter for the number of tokens in the current chunk
    chunk = []  # List to accumulate sentences for the current chunk

    # Iterate over sentences and their corresponding token counts
    for sentence, token in zip(sentences, n_tokens):
        
        # If adding the current sentence would exceed the max token limit, start a new chunk
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")  # Join accumulated sentences and add to chunks
            chunk = []  # Reset the chunk
            tokens_so_far = 0  # Reset the token counter

        # Skip sentences that exceed the max token limit by themselves
        if token > max_tokens:
            continue

        # Add the current sentence to the chunk
        chunk.append(sentence)
        tokens_so_far += token + 1  # Update the token count

    # Add the last chunk if it has any content
    if chunk:
        chunks.append(". ".join(chunk) + ".")

    return chunks  # Return the list of text chunks

# List to store the processed text chunks
shortened = []

# Iterate over the DataFrame rows
for _, row in df.iterrows():
    # Skip rows with None in the 'text' field
    if row['text'] is None:
        continue

    # If the number of tokens in the text exceeds the max token limit, split the text
    if row['n_tokens'] > max_tokens:
        shortened += split_into_many(row['text'])
    else:
        # If the text is within the token limit, add it to the list as is
        shortened.append(row['text'])

# Create a new DataFrame with the processed text chunks
df = pd.DataFrame(shortened, columns=['text'])

# Recalculate the number of tokens for each chunk in the new DataFrame
df['n_tokens'] = df['text'].apply(lambda x: len(tokenizer.encode(x)))

def get_embedding(text: str, model: str) -> List[float]:
    """
    Retrieves the embedding for the given text using the specified model.
    
    Parameters:
    - text: The input text to be embedded.
    - model: The model name to use for generating the embedding.
    
    Returns:
    - A list representing the embedding vector for the input text.
    """
    text = text.replace("\n", " ")  # Replace newline characters with spaces for cleaner input
    return client.embeddings.create(input=[text], model=model).data[0].embedding  # Retrieve the embedding

# Calculate embeddings for each text chunk and add as a new column to the DataFrame
df["embeddings"] = df['text'].apply(lambda x: get_embedding(x, model=embedding_model))

# Save the DataFrame with embeddings to a CSV file
df.to_csv('embeddings.csv')
