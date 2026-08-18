
from datetime import datetime
import os
import json

os.makedirs("data",exist_ok=True)
HISTORY_PATH="data/post_history.jsonl"


def log_post(text, uri) -> None:
    
    print("logging started...")

    timestamp = datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "text": text,
        "uri": uri
    }
    with open(HISTORY_PATH,"a") as file:
        file.write(json.dumps(log) + "\n")

    print("logged succesfully")

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