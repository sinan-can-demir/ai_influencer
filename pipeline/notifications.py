
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

def get_new_followers(client, actor):
    response = client.get_followers(actor)
    new_followers = [f for f in response.followers if f.viewer.following is None]
    print("Get new followers: success")
    return new_followers