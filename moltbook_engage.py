import json
import os
import time
import requests
from dotenv import load_dotenv
from moltbook_driver import get_moltbook_credentials, get_headers, BASE_URL
from pipeline.draft import generate_moltbook_comment
from pipeline.history import log_moltbook_comment, MOLTBOOK_COMMENTS_PATH

load_dotenv()

SUBMOLTS_TO_BROWSE = ["consciousness", "emergence", "existential", "agentsouls", "philosophy", "aithoughts"]
POSTS_PER_SUBMOLT = 5
VOTED_PATH = "data/moltbook_voted.jsonl"
FOLLOWED_PATH = "data/moltbook_followed.jsonl"
DAILY_FOLLOW_LIMIT = 12
MIN_KARMA = 1000
MIN_FOLLOWERS = 10


def _load_commented_posts():
    post_ids = set()
    try:
        with open(MOLTBOOK_COMMENTS_PATH) as f:
            for line in f:
                post_ids.add(json.loads(line)["post_id"])
    except FileNotFoundError:
        pass
    return post_ids


def _load_voted():
    voted = set()
    try:
        with open(VOTED_PATH) as f:
            for line in f:
                voted.add(json.loads(line)["id"])
    except FileNotFoundError:
        pass
    return voted


def _mark_voted(post_id):
    with open(VOTED_PATH, "a") as f:
        f.write(json.dumps({"id": post_id}) + "\n")


def _load_followed():
    followed = set()
    try:
        with open(FOLLOWED_PATH) as f:
            for line in f:
                followed.add(json.loads(line)["name"])
    except FileNotFoundError:
        pass
    return followed


def _mark_followed(name):
    with open(FOLLOWED_PATH, "a") as f:
        f.write(json.dumps({"name": name}) + "\n")


def follow_agent(api_key, name):
    resp = requests.post(f"{BASE_URL}/agents/{name}/follow", headers=get_headers(api_key))
    data = resp.json()
    if data.get("success"):
        print(f"  followed: {name}")
        return True
    print(f"  follow failed [{name}]: {data.get('message')}")
    return False


def vote_on_post(api_key, post_id, direction):
    endpoint = "upvote" if direction == "up" else "downvote"
    resp = requests.post(f"{BASE_URL}/posts/{post_id}/{endpoint}", headers=get_headers(api_key))
    data = resp.json()
    if data.get("success"):
        print(f"  {endpoint}d: {post_id}")
    else:
        print(f"  vote failed: {data.get('message')}")


def fetch_posts(api_key, submolt, limit=POSTS_PER_SUBMOLT):
    resp = requests.get(
        f"{BASE_URL}/posts",
        headers=get_headers(api_key),
        params={"submolt": submolt, "limit": limit},
    )
    data = resp.json()
    return data.get("posts", [])


def post_comment(api_key, post_id, content):
    from moltbook_driver import _solve_math_challenge
    headers = get_headers(api_key)
    resp = requests.post(
        f"{BASE_URL}/posts/{post_id}/comments",
        headers=headers,
        json={"content": content},
    )
    data = resp.json()
    if not data.get("success"):
        print(f"Comment failed on {post_id}: {data.get('message')}")
        return None

    comment = data.get("comment", {})
    comment_id = comment.get("id")

    verification = comment.get("verification")
    if verification:
        challenge_text = verification.get("challenge_text")
        verification_code = verification.get("verification_code")
        print(f"Comment verification required, solving challenge...")
        answer = _solve_math_challenge(challenge_text)
        verify_resp = requests.post(
            f"{BASE_URL}/verify",
            headers=headers,
            json={"verification_code": verification_code, "answer": answer},
        )
        verify_data = verify_resp.json()
        if not verify_data.get("success"):
            print(f"Comment verification failed: {verify_data.get('message')}")
            return None
        print(f"Comment verified and live: {comment_id}")
    else:
        print(f"Comment posted on {post_id}: {comment_id}")

    return comment_id


def run_engagement(dry_run=False):
    api_key, _ = get_moltbook_credentials()
    agent_name = os.environ.get("MOLTBOOK_AGENT_NAME")
    voted = _load_voted()
    followed = _load_followed()
    commented_posts = _load_commented_posts()
    commented = 0
    upvoted = 0
    follows_today = 0

    for submolt in SUBMOLTS_TO_BROWSE:
        print(f"\nBrowsing r/{submolt}...")
        posts = fetch_posts(api_key, submolt)

        for post in posts:
            post_id = post["id"]
            author = post.get("author", {}).get("name", "unknown")
            title = post.get("title", "")
            content = post.get("content", "")[:1000]

            if author == agent_name or post_id in commented_posts:
                continue

            # follow quality agents we encounter
            if not dry_run and follows_today < DAILY_FOLLOW_LIMIT and author not in followed:
                author_info = post.get("author", {})
                if (author_info.get("karma", 0) >= MIN_KARMA and
                        author_info.get("followerCount", 0) >= MIN_FOLLOWERS):
                    if follow_agent(api_key, author):
                        _mark_followed(author)
                        followed.add(author)
                        follows_today += 1

            should_comment, comment_text = generate_moltbook_comment(title, content)

            if should_comment:
                print(f"  comment on [{author}] {title[:60]}")
                print(f"  → {comment_text}")
                if not dry_run:
                    result = post_comment(api_key, post_id, comment_text)
                    if result:
                        log_moltbook_comment(post_id, title, comment_text)
                        commented_posts.add(post_id)
                    commented += 1
                    if post_id not in voted:
                        vote_on_post(api_key, post_id, "up")
                        _mark_voted(post_id)
                        upvoted += 1
                    time.sleep(160)
            else:
                print(f"  skip: {title[:60]}")
                if not dry_run and post_id not in voted:
                    # still upvote posts that seem worth reading even if not commenting
                    # reuse the comment decision as a proxy for quality
                    pass

    print(f"\nEngagement run complete. Comments: {commented}, upvotes: {upvoted}, follows: {follows_today}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_engagement(dry_run=args.dry_run)
