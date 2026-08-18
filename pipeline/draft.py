

from groq import Groq
from persona import SYSTEM_PROMPT
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()
DRAFT_MODEL="openai/gpt-oss-120b"

def groq_client() -> Groq:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    print("Groq client initialized.")
    return client

def generate_draft():
    client = groq_client()
    today = date.today()
    response = client.chat.completions.create(
        model=DRAFT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"today is {today}, write today's post"},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(generate_draft())