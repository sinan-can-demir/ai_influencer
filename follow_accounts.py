
from driver import get_bluesky_account, get_bluesky_client, login
from pipeline.history import log_follow
import time

def is_already_following(client, did):
    records = client.com.atproto.repo.list_records({"repo": client.me.did, "collection": "app.bsky.graph.follow", "limit": 100})
    return any(r.value.subject == did for r in records.records)

def follow_account(client, handle) -> None:
    profile = client.get_profile(handle)
    client.follow(profile.did)
    time.sleep(1)
    if not is_already_following(client, profile.did):
        print(f"Follow to {handle} did not persist, retrying...")
        client.follow(profile.did)
        time.sleep(1)
        if not is_already_following(client, profile.did):
            print(f"Follow to {handle} failed after retry")
            return
    print(f"Followed {handle}: success")
    log_follow(handle, profile.did)

def main():
    client = get_bluesky_client()
    handle, app_password = get_bluesky_account()
    login(client, handle, app_password)
    ## TODO: create a get_follow_accounts() function
    ## that returns a list of accounts
    handles = ["epollard.bsky.social", "thejokebot.bsky.social", "jillybee72.bsky.social"]
    for h in handles:
        follow_account(client, h)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occured: Failure {e}")
