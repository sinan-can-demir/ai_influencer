

from groq import Groq
from pipeline.persona import SYSTEM_PROMPT, IMAGE_SYSTEM_PROMPT, ALT_TEXT_SYSTEM_PROMPT, IMAGE_DECISION_SYSTEM_PROMPT, CONTENT_FILTER_SYSTEM_PROMPT, REPLY_SYSTEM_PROMPT, MEMORY_SYSTEM_PROMPT, FOLLOW_BACK_SYSTEM_PROMPT, MOLTBOOK_SYSTEM_PROMPT, MOLTBOOK_COMMENT_SYSTEM_PROMPT
from pipeline.history import get_recent_posts, get_recent_memories
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()
DRAFT_MODEL="openai/gpt-oss-120b"

def groq_client() -> Groq:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    print("Groq client initialized.")
    return client

def generate_text(system_prompt, user_content) -> str:
    client = groq_client()
    response = client.chat.completions.create(
        model=DRAFT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
            ],
    )
    print("Text generated: success")
    return response.choices[0].message.content

def generate_draft() -> str:
    day = date.today()
    recent_posts = get_recent_posts(n=10)
    recent_text = "\n".join(recent_posts)
    recent_memories= get_recent_memories()
    memory_text = "\n".join(recent_memories)
    content = generate_text(SYSTEM_PROMPT, f"today is {day}. here's what you posted recently:\n{recent_text}\nvary your structure from these -- don't repeat the same opening, rhythm, or ending shape.\nhere's what you remember from recent conversations:\n{memory_text}\nwrite today's post")
    print("Draft generated: success")
    return content

def generate_image_prompt(post_text) -> str:
    content = generate_text(IMAGE_SYSTEM_PROMPT, post_text)
    print("Image promt generated: success")
    return content

def should_generate_image(post_text) -> bool:
    decision = generate_text(IMAGE_DECISION_SYSTEM_PROMPT, post_text)
    print("Image decision made: success")
    return decision.strip().lower() == "yes"

def generate_alt_text(image_prompt) -> str:
    content = generate_text(ALT_TEXT_SYSTEM_PROMPT, image_prompt)
    print("Alt text generated: success")
    return content

def should_surface_notification(text) -> bool:
    decision = generate_text(CONTENT_FILTER_SYSTEM_PROMPT,  text)
    print("Decision made: success")
    return decision.strip().lower() == "yes"

def should_follow_back(profile_text):
    if "brid.gy" in profile_text.lower():
        print("Follow back decision made: rejected (bridged/automated feed account)")
        return False
    decision = generate_text(FOLLOW_BACK_SYSTEM_PROMPT, profile_text)
    print("Follow back decision made: success")
    return decision.strip().lower() == "yes"

def generate_reply(notification_text) -> str:
    content = generate_text(REPLY_SYSTEM_PROMPT, notification_text)
    print("Reply text generated: success")
    return content

def generate_memory_entry(exchange_text):
    content = generate_text(MEMORY_SYSTEM_PROMPT, exchange_text)
    print("Memory entry generated: success")
    return content

def generate_moltbook_draft(topic=None):
    day = date.today()
    recent_posts = get_recent_posts(n=10)
    recent_text = "\n".join(recent_posts)
    topic_hint = f" focus this post on the topic: {topic}." if topic else ""
    raw = generate_text(
        MOLTBOOK_SYSTEM_PROMPT,
        f"today is {day}. here's what you posted recently:\n{recent_text}\nwrite today's moltbook post.{topic_hint}"
    )
    title, body = "", ""
    for line in raw.splitlines():
        if line.startswith("TITLE:"):
            title = line[len("TITLE:"):].strip()
        elif line.startswith("BODY:"):
            body = line[len("BODY:"):].strip()
    if not title or not body:
        raise ValueError(f"Moltbook draft missing title or body. Raw output:\n{raw}")
    print("Moltbook draft generated: success")
    return title, body


def generate_moltbook_comment(post_title, post_content):
    raw = generate_text(
        MOLTBOOK_COMMENT_SYSTEM_PROMPT,
        f"POST TITLE: {post_title}\n\nPOST CONTENT: {post_content}"
    )
    lines = raw.strip().splitlines()
    decision = lines[0].strip().upper() if lines else "NO"
    comment = lines[1].strip() if len(lines) > 1 else ""
    return decision == "YES", comment


if __name__ == "__main__":
    print(generate_draft())