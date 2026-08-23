
from driver import get_bluesky_client, get_bluesky_account, login
from pipeline.notifications import get_new_followers
from pipeline.draft import should_follow_back
from follow_accounts import follow_account

def build_profile_text(client, follower):
    feed = client.get_author_feed(actor=follower.handle, limit=5)
    posts = [item.post.record.text for item in feed.feed]
    posts_text = "\n".join(posts)
    return f"bio: {follower.description}\nrecent posts:\n{posts_text}"

def main():
    client = get_bluesky_client()
    handle, app_password = get_bluesky_account()
    login(client, handle, app_password)

    new_followers = get_new_followers(client, handle)
    for follower in new_followers:
        profile_text = build_profile_text(client, follower)
        if should_follow_back(profile_text):
            follow_account(client, follower.handle)
        else:
            print(f"Skipped follow-back for {follower.handle}: not a good fit")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occured: Failure {e}")