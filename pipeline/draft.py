

from groq import Groq
from pipeline.persona import SYSTEM_PROMPT, IMAGE_SYSTEM_PROMPT
from pipeline.history import get_recent_posts
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()
DRAFT_MODEL="openai/gpt-oss-120b"

def groq_client() -> Groq:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    print("Groq client initialized.")
    return client

def generate_text(system_prompt, user_content):
    client = groq_client()
    response = client.chat.completions.create(
        model=DRAFT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
            ],
    )
    return response.choices[0].message.content

def generate_draft():
    day = date.today()
    recent_posts = get_recent_posts()
    recent_text = "\n".join(recent_posts)
    content = generate_text(SYSTEM_PROMPT, f"today is {day}. here's what you posted recently:\n{recent_text}\nwrite today's post")
    return content

def generate_image_prompt(post_text):
    content = generate_text(IMAGE_SYSTEM_PROMPT, post_text)
    return content

if __name__ == "__main__":
    print(generate_draft())