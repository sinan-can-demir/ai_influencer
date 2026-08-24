
from driver import get_bluesky_account, get_bluesky_client, login
from pipeline.notifications import search_candidate_authors
from pipeline.draft import should_follow_back
from follow_accounts import follow_account

QUERY_TERMS= ["home cooking", "butterfly garden", "indie music", "birdwatching", "improv comedy"]
MAX_NEW_FOLLOWS_PER_RUN = 2

def main():
    client = get_bluesky_client()
    handle, app_password = get_bluesky_account()
    login(client, handle, app_password)

    followed_count = 0
    for query in QUERY_TERMS:
        if followed_count >= MAX_NEW_FOLLOWS_PER_RUN:
            break
        candidates = search_candidate_authors(client, query)
        for author, post_text in candidates:
            if followed_count >= MAX_NEW_FOLLOWS_PER_RUN:
                break
            profile = client.get_profile(author.handle)
            profile_text = f"bio: {profile.description}\npost: {post_text}"
            if should_follow_back(profile_text):
                follow_account(client, author.handle)
                followed_count += 1
            else:
                print(f"Skipped {author.handle}: not a good fit")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occured: Failure {e}")