

from groq import Groq
from persona import SYSTEM_PROMPT, IMAGE_SYSTEM_PROMPT
from history import get_recent_posts
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
    recent_posts = get_recent_posts()
    recent_text = "\n".join(recent_posts)
    response = client.chat.completions.create(
        model=DRAFT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"today is {today}. here's what you posted recently:\n{recent_text}\nwrite today's post"}
            ],
    )
    return response.choices[0].message.content

def generate_image_prompt(post_text):
    client = groq_client()
    response = client.chat.completions.create(
        model=DRAFT_MODEL,
        messages=[
            {"role": "system", "content": IMAGE_SYSTEM_PROMPT},
            {"role": "user", "content": post_text}
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(generate_draft())