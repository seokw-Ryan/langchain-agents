from openai import OpenAI

import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.environ['OPENAI_API_KEY']

client = OpenAI()

def make_tweet():
    request = "Be simple and concise. I am a student who is specializing in AI hardware and Quantum Computing. I am going to be Michael Jordan of engineering and science. Write my first Twitter post that introduces me to the public and helps me to gain fame. I am going to talk about what I learn and share my journey daily. No emojis. Have two hashtags. Write the twitter post in less than 200 characters."

    tweet1 = ""

    content = request + tweet1

    response = client.chat.completions.create(
        model = "gpt-4o-mini-2024-07-18",
        messages = [
            {"role": "user", "content": content},
            
        ],
    
    )

    return response.choices[0].message.content