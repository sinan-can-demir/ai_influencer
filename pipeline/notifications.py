
from atproto_client import models

def get_notifications(client):
    response = client.app.bsky.notification.list_notifications(params={"reasons": ["mention", "reply"]})
    print("Get notifications: success")
    return response.notifications

def build_reply_ref(notification):
    parent = models.ComAtprotoRepoStrongRef.Main(uri=notification.uri, cid=notification.cid)
    root = notification.record.reply.root if notification.record.reply else parent
    print("Build reply ref: success")
    return models.AppBskyFeedPost.ReplyRef(root=root, parent=parent)