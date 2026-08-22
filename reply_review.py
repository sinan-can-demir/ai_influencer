
from pipeline.notifications import build_reply_ref, get_notifications
from pipeline.history import log_post, log_memory
from driver import get_bluesky_account, get_bluesky_client, login
from pipeline.draft import should_surface_notification, generate_reply, generate_memory_entry



def post_reply(client, reply_text, notification) -> None:
    reply_to = build_reply_ref(notification)
    post = client.send_post(text=reply_text, reply_to=reply_to)
    print(f"Reply posted: success \n {post.uri}")
    log_post(reply_text, post.uri)
    exchange_text = f"they said: {notification.record.text}\ni replied: {reply_text}"
    memory_summary = generate_memory_entry(exchange_text)
    log_memory(notification.author.handle, memory_summary)

def main():
    client = get_bluesky_client()
    handle, app_password = get_bluesky_account()
    login(client, handle, app_password)
    notifications = get_notifications(client)

    for n in notifications:
        if not should_surface_notification(n.record.text):
            continue
        reply_text = generate_reply(n.record.text)
        print(f"From {n.author.handle}: {n.record.text}")
        print(f"Juno's reply: {reply_text}")
        choice = input("Post this reply? (y/n): ")
        if choice.lower() == "y":
            post_reply(client, reply_text, n)
        else:
            print("Reply skipped: success")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occured: Failure {e}")