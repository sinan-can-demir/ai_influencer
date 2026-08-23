
from driver import get_bluesky_account, get_bluesky_client, login
from pipeline.history import log_follow

def follow_account(client, handle) -> None:
    profile = client.get_profile(handle)
    client.follow(profile.did)
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
