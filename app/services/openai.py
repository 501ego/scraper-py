from app.config import openai_key
from openai import OpenAI

client = OpenAI(api_key=openai_key)

response = client.chat.completions.create(
    model='o3-mini',
    messages=[
        {
            'role': 'system',
            'content': 'You are a helpful assistant.'
        }
    ]
)