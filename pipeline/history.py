
from datetime import datetime
import os
import json

os.makedirs("data",exist_ok=True)
HISTORY_PATH="data/post_history.jsonl"
IMAGE_HISTORY_PATH="data/image_history.jsonl"
MEMORY_PATH="data/memory.jsonl"
FOLLOW_PATH="data/follows.jsonl"

def log_post(text, uri, platform="bluesky") -> None:

    print("Post logging started...")

    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "platform": platform,
        "text": text,
        "uri": uri
    }
    with open(HISTORY_PATH,"a") as file:
        file.write(json.dumps(log) + "\n")

    print("Post logged: success")

def get_recent_posts(n=5) -> list:
    results = []

    try:
        with open(HISTORY_PATH, "r") as file:
            recent_lines = file.readlines()[-n:]
    except FileNotFoundError:
        print("No History File found")
        return []
    
    for line in recent_lines:
        record = json.loads(line)
        results.append(record["text"])

    return results

def log_image(prompt, reference_images, seed, output_path) -> None:
    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "prompt": prompt,
        "reference_images": reference_images,
        "seed": seed,
        "output_path": output_path
    }

    with open(IMAGE_HISTORY_PATH,"a") as file:
        file.write(json.dumps(log) + "\n")
    print("Image logged: success")

def log_memory(person, summary) -> None:
    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "person": person,
        "summary": summary
    }
    with open(MEMORY_PATH,"a") as file:
        file.write(json.dumps(log) + "\n")
    print("Memory logged: success")

def get_recent_memories(n=5) -> list:
    memory= []

    try:
        with open(MEMORY_PATH, "r") as file:
            recent_lines = file.readlines()[-n:]
    except FileNotFoundError:
        print("No History File found")
        return []

    for line in recent_lines:
        record = json.loads(line)
        memory.append(f"talked with {record['person']} about: {record['summary']}")
    print("Memory created: success")
    return memory

MOLTBOOK_COMMENTS_PATH = "data/moltbook_comments.jsonl"
MOLTBOOK_REPLIED_PATH = "data/moltbook_replied.jsonl"

def log_moltbook_comment(post_id, post_title, comment_text) -> None:
    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "post_id": post_id,
        "post_title": post_title,
        "comment": comment_text,
    }
    with open(MOLTBOOK_COMMENTS_PATH, "a") as f:
        f.write(json.dumps(log) + "\n")
    print("Moltbook comment logged: success")


def load_replied_comment_ids() -> set:
    ids = set()
    try:
        with open(MOLTBOOK_REPLIED_PATH) as f:
            for line in f:
                ids.add(json.loads(line)["id"])
    except FileNotFoundError:
        pass
    return ids


def log_moltbook_reply(comment_id, reply_text) -> None:
    timestamp = datetime.now().isoformat()
    log = {"timestamp": timestamp, "id": comment_id, "reply": reply_text}
    with open(MOLTBOOK_REPLIED_PATH, "a") as f:
        f.write(json.dumps(log) + "\n")
    print("Moltbook reply logged: success")


def log_follow(handle, did) -> None:
    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "handle": handle,
        "did": did
    }
    with open(FOLLOW_PATH, "a") as file:
        file.write(json.dumps(log) + "\n")
    print("Follow logged: success")