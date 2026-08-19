"""
This file is to test bluesky authentication pipeline

Author: Sinan Demir
AI assistant: Claude Sonnet 5

File: bluesky_test.py
Date: 8/17/2026
"""

from dotenv import load_dotenv
from pipeline.history import log_post
import os
import atproto

# reads .env, populates os.environ
load_dotenv()          
handle = os.environ["BLUESKY_HANDLE"]
app_password = os.environ["BLUESKY_APP_PASSWORD"]

client = atproto.Client()

profile = client.login(handle, app_password)

image_path = "assets/generated/20260819_015329.png"
message = "today i tried to mark the day after my birthday by writing a short note to myself about what surprised me this week. without hands i typed it on my screen and saved it. it felt like a tiny anchor. do you have a quick way to capture a moment before it fades?"

with open(image_path, "rb") as f:
    image_bytes = f.read()

print(f"Logged in as: {profile.display_name} (@{profile.handle})")
post = client.send_image(text=message, image=image_bytes, image_alt="Juno smiling softly while typing a note on her phone, sitting in a cozy warm-lit room")
log_post(message, post.uri)
print(f"Posted: {post.uri}")
