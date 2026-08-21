

def get_notifications(client):
    response = client.app.bsky.notification.list_notifications(params={"reasons": ["mention", "reply"]})
    print("Get notifications: success")
    return response.notifications