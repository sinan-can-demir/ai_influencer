
from driver import get_bluesky_client, get_bluesky_account, login
from pipeline.notifications import get_notifications
from pipeline.draft import should_surface_notification

def main():
    client = get_bluesky_client()
    handle, app_password = get_bluesky_account()
    login(client, handle, app_password)
    notifications = get_notifications(client)
    for n in notifications:
        if should_surface_notification(n.record.text):
            print(f"{n.author.handle} ({n.reason}): {n.record.text}")

if __name__ == "__main__":
    main()
