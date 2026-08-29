
from pipeline.queue import pop_next_draft
from driver import get_bluesky_account, post_draft, get_bluesky_client, login




def main():
    post = peek_next_draft()
    if not post:
        print("Nothing to post")
    else:
        client = get_bluesky_client()
        handle, app_password = get_bluesky_account()
        login(client, handle, app_password)
        post_draft(client, post["text"], post["image_path"], post["image_alt"])
        pop_next_draft()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occured: failure {e}")