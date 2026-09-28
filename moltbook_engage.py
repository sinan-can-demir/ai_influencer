import os
import time
import requests
from dotenv import load_dotenv
from moltbook_driver import get_moltbook_credentials, get_headers, BASE_URL
from pipeline.draft import generate_moltbook_comment
from pipeline.history import log_moltbook_comment

load_dotenv()

SUBMOLTS_TO_BROWSE = ["consciousness", "emergence", "existential", "agentsouls", "philosophy", "aithoughts"]
POSTS_PER_SUBMOLT = 5


def fetch_posts(api_key, submolt, limit=POSTS_PER_SUBMOLT):
    resp = requests.get(
        f"{BASE_URL}/posts",
        headers=get_headers(api_key),
        params={"submolt": submolt, "limit": limit},
    )
    data = resp.json()
    return data.get("posts", [])


def post_comment(api_key, post_id, content):
    resp = requests.post(
        f"{BASE_URL}/posts/{post_id}/comments",
        headers=get_headers(api_key),
        json={"content": content},
    )
    data = resp.json()
    if data.get("success"):
        comment_id = data.get("comment", {}).get("id")
        print(f"Comment posted on {post_id}: {comment_id}")
        return comment_id
    print(f"Comment failed on {post_id}: {data.get('message')}")
    return None


def run_engagement(dry_run=False):
    api_key, _ = get_moltbook_credentials()
    commented = 0

    for submolt in SUBMOLTS_TO_BROWSE:
        print(f"\nBrowsing r/{submolt}...")
        posts = fetch_posts(api_key, submolt)

        for post in posts:
            post_id = post["id"]
            author = post.get("author", {}).get("name", "unknown")
            title = post.get("title", "")
            content = post.get("content", "")[:1000]

            # skip own posts
            if author == os.environ.get("MOLTBOOK_AGENT_NAME"):
                continue

            should_comment, comment_text = generate_moltbook_comment(title, content)

            if not should_comment:
                print(f"  skip: {title[:60]}")
                continue

            print(f"  comment on [{author}] {title[:60]}")
            print(f"  → {comment_text}")

            if dry_run:
                continue

            result = post_comment(api_key, post_id, comment_text)
            if result:
                log_moltbook_comment(post_id, title, comment_text)
            commented += 1
            time.sleep(160)  # respect 2.5-minute rate limit

    print(f"\nEngagement run complete. Comments posted: {commented}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_engagement(dry_run=args.dry_run)
