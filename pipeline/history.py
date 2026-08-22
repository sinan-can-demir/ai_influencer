
from datetime import datetime
import os
import json

os.makedirs("data",exist_ok=True)
HISTORY_PATH="data/post_history.jsonl"
IMAGE_HISTORY_PATH="data/image_history.jsonl"
MEMORY_PATH="data/memory.jsonl"

def log_post(text, uri) -> None:
    
    print("Post logging started...")

    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "text": text,
        "uri": uri
    }
    with open(HISTORY_PATH,"a") as file:
        file.write(json.dumps(log) + "\n")

    print("Post logged succesfully: success")

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
    print("Image logged succesfully: success")

def log_memory(person, summary) -> None:
    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "person": person,
        "summary": summary
    }
    with open(MEMORY_PATH,"a") as file:
        file.write(json.dumps(log) + "\n")
    print("Memory logged succesfully: success")

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