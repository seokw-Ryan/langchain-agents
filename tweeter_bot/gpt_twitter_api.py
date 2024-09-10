from openai import OpenAI

import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.environ['OPENAI_API_KEY']

client = OpenAI()

def make_tweet():
    request = "I am a student who is specializing in AI hardware and Quantum Computing. Write my first Twitter post that introduces me to the public and helps me to gain fame."

    tweet1 = ""

    content = request + tweet1

    response = client.chat.completions.create(
        model = "gpt-4o-mini-2024-07-18",
        messages = [
            {"role": "user", "content": content},
            
        ],
    
    )

    return response.choices[0].message.content