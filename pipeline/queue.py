

from datetime import datetime
import os
import json

os.makedirs("data",exist_ok=True)
QUEUE_PATH="data/approved_queue.jsonl"

def enqueue_draft(text, image_path, image_alt) -> None:

    print("Queuing posts...")

    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "text": text,
        "image_path": image_path,
        "image_alt": image_alt
    }
    with open(QUEUE_PATH,"a") as file:
        file.write(json.dumps(log) + "\n")

    print("Queue logged: success")

def pop_next_draft() -> dict:
    results = []
    try:
        with open(QUEUE_PATH, "r") as file:
            queue_lines = file.readlines()
    except FileNotFoundError:
        print("No queue file found")
        return None

    for line in queue_lines:
        record = json.loads(line)
        results.append(record)

    if not results: return None
    # Type: dict post variable
    post = results.pop(0)

    with open(QUEUE_PATH, "w") as file:
        for result in results:
            file.write(json.dumps(result) + "\n")
    print("Pop next draft: success")
    return post