from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.environ['OPENAI_API_KEY']
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Tell me about python"},
    ],
)

print(response.choices[0].message.content)