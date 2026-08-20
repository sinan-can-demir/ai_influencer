
from pipeline.draft import generate_draft, should_generate_image
from pipeline.image import image_pipeline
from pipeline.history import log_post

from dotenv import load_dotenv
import atproto
import os

load_dotenv()

def get_bluesky_client() -> atproto.Client:
    client = atproto.Client()
    print("Atproto client initialized: success")
    return client

def get_bluesky_account():
    handle = os.environ["BLUESKY_HANDLE"]
    app_password = os.environ["BLUESKY_APP_PASSWORD"]
    print("Get bluesky account: success")
    return (handle,app_password)

def login(client, handle, app_password) -> None:
    profile = client.login(handle, app_password)
    print(f"Logged in as: {profile.display_name} (@{profile.handle})")

def post_draft(client, post_text, image_path, image_alt):
    if image_path:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        post = client.send_image(text=post_text, image=image_bytes, image_alt=image_alt)
    else:
        post = client.send_post(text=post_text)
    print(f"Draft posted: success \n {post.uri}")
    log_post(post_text, post.uri)

def main():
    post_text = generate_draft()
    print(post_text)
    image_path = None
    image_alt = None

    image_choice = should_generate_image(post_text)
    if image_choice:
        image_path, image_alt = image_pipeline(post_text)
        if image_path:
            print("Driver completed with image: success")
        else:
            print("Driver completed: partial failure (image generation failed)")
    
    post_choice = input("Post this? (y/n): ")
    if post_choice.lower() == "y":
        client = get_bluesky_client()
        handle, app_password = get_bluesky_account()
        login(client, handle, app_password)
        post_draft(client, post_text, image_path, image_alt)
    else:
        print("Driver completed without any post: success")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occured: Failure {e}")