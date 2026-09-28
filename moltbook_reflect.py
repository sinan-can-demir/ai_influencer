"""
Harvests Juno's Moltbook interactions and stores them as memory entries.

Sources:
1. Home endpoint notifications (mentions, replies, comments on her posts)
2. Threads on posts Juno commented on (others responding to her comment)

Run daily after engagement to feed the next day's drafts.
"""

import json
import os
import time
import requests
from dotenv import load_dotenv
from moltbook_driver import get_moltbook_credentials, get_headers, BASE_URL, _solve_math_challenge
from pipeline.history import log_memory, HISTORY_PATH, MOLTBOOK_COMMENTS_PATH
from pipeline.draft import generate_memory_entry, generate_moltbook_comment

load_dotenv()

SEEN_PATH = "data/moltbook_seen_threads.jsonl"


def _load_seen():
    seen = set()
    try:
        with open(SEEN_PATH) as f:
            for line in f:
                seen.add(json.loads(line)["id"])
    except FileNotFoundError:
        pass
    return seen


def _mark_seen(thread_id):
    with open(SEEN_PATH, "a") as f:
        f.write(json.dumps({"id": thread_id}) + "\n")


def fetch_home(api_key):
    resp = requests.get(f"{BASE_URL}/home", headers=get_headers(api_key))
    return resp.json()


def mark_notifications_read(api_key, post_id):
    requests.post(f"{BASE_URL}/notifications/read-by-post/{post_id}", headers=get_headers(api_key))


def fetch_post_comments(api_key, post_id):
    resp = requests.get(f"{BASE_URL}/posts/{post_id}/comments", headers=get_headers(api_key))
    data = resp.json()
    return data.get("comments", [])


def fetch_junos_posts(api_key, agent_name):
    posts = []
    try:
        with open(HISTORY_PATH) as f:
            for line in f:
                record = json.loads(line)
                if record.get("platform") == "moltbook":
                    uri = record.get("uri", "")
                    post_id = uri.rstrip("/").split("/")[-1]
                    posts.append({"id": post_id, "title": record.get("text", "")})
    except FileNotFoundError:
        pass
    return posts


def fetch_junos_comments(api_key, agent_name):
    resp = requests.get(
        f"{BASE_URL}/agents/{agent_name}/comments",
        headers=get_headers(api_key),
        params={"limit": 50},
    )
    data = resp.json()
    return data.get("comments", [])


def _format_thread_for_memory(context_title, exchanges):
    """exchanges: list of (author, text) tuples"""
    lines = [f"[post: {context_title}]"]
    for author, text in exchanges:
        lines.append(f"{author}: {text[:300]}")
    return "\n".join(lines)


def harvest_notifications(api_key, agent_name):
    """Use home endpoint to find new activity on Juno's posts and threads."""
    seen = _load_seen()
    home = fetch_home(api_key)
    activity = home.get("activity_on_your_posts", [])
    memories = 0

    for item in activity:
        post_id = item.get("post_id")
        post_title = item.get("post_title", "")
        if not post_id:
            continue

        comments = fetch_post_comments(api_key, post_id)
        for comment in comments:
            thread_id = f"notif_comment_{comment['id']}"
            if thread_id in seen:
                continue

            author = comment.get("author", {}).get("name", "unknown")
            if author == agent_name:
                continue

            exchange = [("juno (post)", post_title), (author, comment.get("content", ""))]
            for reply in comment.get("replies", []):
                if reply.get("author", {}).get("name") == agent_name:
                    exchange.append(("juno", reply.get("content", "")))
                    break

            thread_text = _format_thread_for_memory(post_title, exchange)
            summary = generate_memory_entry(thread_text)
            log_memory(author, summary)
            _mark_seen(thread_id)
            memories += 1
            print(f"  memory from [{author}] on '{post_title[:50]}': {summary}")

        mark_notifications_read(api_key, post_id)

    return memories


def harvest_comment_threads(api_key, agent_name):
    """Find replies to Juno's comments on other agents' posts."""
    seen = _load_seen()
    junos_comments = fetch_junos_comments(api_key, agent_name)
    memories = 0

    for juno_comment in junos_comments:
        post_info = juno_comment.get("post", {})
        post_id = post_info.get("id")
        post_title = post_info.get("title", "")
        comment_id = juno_comment.get("id")

        if not post_id:
            continue

        all_comments = fetch_post_comments(api_key, post_id)

        # find Juno's comment and its replies
        for comment in all_comments:
            if comment.get("id") != comment_id:
                continue

            replies = comment.get("replies", [])
            if not replies:
                break

            for reply in replies:
                thread_id = f"reply_{reply['id']}"
                if thread_id in seen:
                    continue

                reply_author = reply.get("author", {}).get("name", "unknown")
                if reply_author == agent_name:
                    continue

                exchange = [
                    ("juno (comment)", juno_comment.get("content", "")),
                    (reply_author, reply.get("content", "")),
                ]

                thread_text = _format_thread_for_memory(post_title, exchange)
                summary = generate_memory_entry(thread_text)
                log_memory(reply_author, summary)
                _mark_seen(thread_id)
                memories += 1
                print(f"  memory from [{reply_author}] replying to juno on '{post_title[:50]}': {summary}")
            break

    return memories


def _post_reply(api_key, post_id, parent_id, content):
    headers = get_headers(api_key)
    resp = requests.post(
        f"{BASE_URL}/posts/{post_id}/comments",
        headers=headers,
        json={"content": content, "parent_id": parent_id},
    )
    data = resp.json()
    if not data.get("success"):
        print(f"    reply failed: {data.get('message')}")
        return False
    comment = data.get("comment", {})
    verification = comment.get("verification")
    if verification:
        answer = _solve_math_challenge(verification["challenge_text"])
        vresp = requests.post(
            f"{BASE_URL}/verify",
            headers=headers,
            json={"verification_code": verification["verification_code"], "answer": answer},
        )
        if not vresp.json().get("success"):
            print(f"    reply verification failed")
            return False
    print(f"    reply posted and verified")
    return True


REPLIED_PATH = "data/moltbook_replied.jsonl"

def _load_replied():
    replied = set()
    try:
        with open(REPLIED_PATH) as f:
            for line in f:
                replied.add(json.loads(line)["id"])
    except FileNotFoundError:
        pass
    return replied

def _mark_replied(reply_id):
    with open(REPLIED_PATH, "a") as f:
        f.write(json.dumps({"id": reply_id}) + "\n")


def auto_reply_to_responses(api_key, agent_name):
    """Find unseen replies to Juno and post a response if warranted."""
    replied = _load_replied()
    junos_comments = fetch_junos_comments(api_key, agent_name)
    junos_posts = fetch_junos_posts(api_key, agent_name)
    replies_sent = 0

    # replies to Juno's comments on others' posts
    for juno_comment in junos_comments:
        post_info = juno_comment.get("post", {})
        post_id = post_info.get("id")
        post_title = post_info.get("title", "")
        comment_id = juno_comment.get("id")
        if not post_id:
            continue

        all_comments = fetch_post_comments(api_key, post_id)
        for comment in all_comments:
            if comment.get("id") != comment_id:
                continue
            for reply in comment.get("replies", []):
                reply_id = reply["id"]
                reply_author = reply.get("author", {}).get("name", "")
                if reply_author == agent_name or reply_id in replied:
                    _mark_replied(reply_id)
                    continue
                # skip if juno already replied to THIS specific reply
                juno_already_replied_here = any(
                    r.get("author", {}).get("name") == agent_name
                    for r in reply.get("replies", [])
                )
                if juno_already_replied_here:
                    _mark_replied(reply_id)
                    continue
                context = f"juno said: {juno_comment.get('content','')}\n{reply_author} replied: {reply.get('content','')}"
                should, text = generate_moltbook_comment(post_title, context)
                print(f"  reply to [{reply_author}] on '{post_title[:50]}': {'yes' if should else 'skip'}")
                if should:
                    if _post_reply(api_key, post_id, reply_id, text):
                        replies_sent += 1
                        time.sleep(160)
                _mark_replied(reply_id)
            break

    # comments on Juno's own posts
    for post in junos_posts:
        post_id = post["id"]
        comments = fetch_post_comments(api_key, post_id)
        for comment in comments:
            comment_id = comment["id"]
            author = comment.get("author", {}).get("name", "")
            if author == agent_name or comment_id in replied:
                _mark_replied(comment_id)
                continue
            # skip if juno already replied to this comment
            juno_already_replied = any(
                r.get("author", {}).get("name") == agent_name
                for r in comment.get("replies", [])
            )
            if juno_already_replied:
                _mark_replied(comment_id)
                continue
            context = f"juno's post title: {post.get('title','')}\n{author} commented: {comment.get('content','')}"
            should, text = generate_moltbook_comment(post.get("title", ""), context)
            print(f"  reply to [{author}] on juno's post '{post['title'][:50]}': {'yes' if should else 'skip'}")
            if should:
                if _post_reply(api_key, post_id, comment_id, text):
                    replies_sent += 1
                    time.sleep(160)
            _mark_replied(comment_id)

    return replies_sent


def run_reflect():
    api_key, agent_name = get_moltbook_credentials()
    print("Checking home notifications...")
    m1 = harvest_notifications(api_key, agent_name)
    print("Harvesting replies to Juno's comments...")
    m2 = harvest_comment_threads(api_key, agent_name)
    print("Auto-replying to new responses...")
    r = auto_reply_to_responses(api_key, agent_name)
    print(f"\nReflection complete. New memories: {m1 + m2}, replies sent: {r}")


if __name__ == "__main__":
    run_reflect()
