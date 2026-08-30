
from pipeline.queue import pop_next_draft, peek_next_draft
from driver import get_bluesky_account, post_draft, get_bluesky_client, login
import argparse


def main(dry_run=False):
    post = peek_next_draft()
    if not post:
        print("Nothing to post")
    elif dry_run:
        print(f"[dry run] would post: {post['text']}")
    else:
        client = get_bluesky_client()
        handle, app_password = get_bluesky_account()
        login(client, handle, app_password)
        post_draft(client, post["text"], post["image_path"], post["image_alt"])
        pop_next_draft()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        main(dry_run=args.dry_run)
    except Exception as e:
        print(f"Error occured: failure {e}")