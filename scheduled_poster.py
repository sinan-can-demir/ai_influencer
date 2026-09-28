
from pipeline.queue import pop_next_draft, peek_next_draft
from pipeline.draft import generate_moltbook_draft
from driver import get_bluesky_account, post_draft, get_bluesky_client, login
from moltbook_driver import get_moltbook_credentials, check_status, post_to_moltbook
import argparse


def post_bluesky(dry_run=False):
    post = peek_next_draft()
    if not post:
        print("Nothing to post")
        return
    if dry_run:
        print(f"[dry run] would post to Bluesky: {post['text']}")
        return
    client = get_bluesky_client()
    handle, app_password = get_bluesky_account()
    login(client, handle, app_password)
    post_draft(client, post["text"], post["image_path"], post["image_alt"])
    pop_next_draft()


def post_moltbook(dry_run=False, submolt="general", topic=None):
    title, body = generate_moltbook_draft(topic=topic)
    if dry_run:
        print(f"[dry run] would post to Moltbook ({submolt}):\nTITLE: {title}\nBODY: {body}")
        return
    api_key, _ = get_moltbook_credentials()
    if not check_status(api_key):
        print("Moltbook agent not claimed — aborting")
        return
    url = post_to_moltbook(api_key, title, body, submolt=submolt)
    print(f"Moltbook post live: {url}")


def main(platform="bluesky", dry_run=False, submolt="general", topic=None):
    if platform == "moltbook":
        post_moltbook(dry_run=dry_run, submolt=submolt, topic=topic)
    else:
        post_bluesky(dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["bluesky", "moltbook"], default="bluesky")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--submolt", default="general")
    parser.add_argument("--topic", default=None)
    args = parser.parse_args()
    try:
        main(platform=args.platform, dry_run=args.dry_run, submolt=args.submolt, topic=args.topic)
    except Exception as e:
        print(f"Error occurred: failure {e}")
