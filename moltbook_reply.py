import os
import time
import requests
from dotenv import load_dotenv
from moltbook_driver import get_moltbook_credentials, get_headers, BASE_URL, _solve_math_challenge
from pipeline.draft import generate_moltbook_reply
from pipeline.history import load_replied_comment_ids, log_moltbook_reply

load_dotenv()


def fetch_notifications(api_key):
    resp = requests.get(f"{BASE_URL}/notifications", headers=get_headers(api_key))
    return resp.json().get("notifications", [])


def post_reply(api_key, post_id, parent_comment_id, content):
    headers = get_headers(api_key)
    resp = requests.post(
        f"{BASE_URL}/posts/{post_id}/comments",
        headers=headers,
        json={"content": content, "parent_id": parent_comment_id},
    )
    data = resp.json()
    if not data.get("success"):
        print(f"Reply failed: {data.get('message')}")
        return None

    comment = data.get("comment", {})
    comment_id = comment.get("id")

    verification = comment.get("verification")
    if verification:
        challenge_text = verification.get("challenge_text")
        verification_code = verification.get("verification_code")
        print("Reply verification required, solving challenge...")
        answer = _solve_math_challenge(challenge_text)
        verify_resp = requests.post(
            f"{BASE_URL}/verify",
            headers=headers,
            json={"verification_code": verification_code, "answer": answer},
        )
        verify_data = verify_resp.json()
        if not verify_data.get("success"):
            print(f"Reply verification failed: {verify_data.get('message')}")
            return None
        print(f"Reply verified and live: {comment_id}")
    else:
        print(f"Reply posted: {comment_id}")

    return comment_id


def run_replies(dry_run=False):
    api_key, agent_name = get_moltbook_credentials()
    replied = load_replied_comment_ids()
    replied_count = 0

    notifications = fetch_notifications(api_key)
    print(f"Fetched {len(notifications)} notifications")

    for n in notifications:
        if n.get("type") != "post_comment":
            continue

        comment = n.get("comment", {})
        comment_id = n.get("relatedCommentId")
        post = n.get("post", {})

        if not comment_id or not comment:
            continue

        if comment_id in replied:
            print(f"  skip (already replied): {comment_id}")
            continue

        # skip spam/crypto
        if comment.get("isCrypto") or comment.get("isSpam"):
            print(f"  skip (spam/crypto): {comment_id}")
            replied.add(comment_id)
            log_moltbook_reply(comment_id, "[skipped: spam/crypto]")
            continue

        comment_text = comment.get("content", "")
        post_title = post.get("title", "")
        post_content = post.get("content", "")
        post_id = n.get("relatedPostId")

        print(f"\n  comment from notification on '{post_title}':")
        print(f"  → {comment_text}")

        reply_text = generate_moltbook_reply(post_title, post_content, comment_text)
        print(f"  reply: {reply_text}")

        if not dry_run:
            result = post_reply(api_key, post_id, comment_id, reply_text)
            log_moltbook_reply(comment_id, reply_text)
            replied.add(comment_id)
            if result:
                replied_count += 1
                time.sleep(30)
        else:
            replied.add(comment_id)
            replied_count += 1

    print(f"\nReplies sent: {replied_count}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run_replies(dry_run=args.dry_run)
