from time import sleep
import time
from atproto import Client
import json

# the first time login with login and password
USERNAME = 'zubaplants.bsky.social'
PASSWORD = 
TARGET_HANDLE = "gettoknownature.bsky.social"
#TARGET_HANDLE = "ashonee.bsky.social"




FOLLOWERS_FILE = "followers.json"

def save_followers_to_disk(followers, filepath):
    """Save followers to a JSON file."""
    print(followers[0])
    print("***************")
    print(dir(followers[0]))
    followers_json=[]


    for follower in followers:
      as_json=follower.json()
      followers_json.append(as_json)

    with open(filepath, 'w') as file:
        json.dump(followers_json, file, indent=4)
    print(f"Saved {len(followers)} followers to {filepath}")

def load_followers_from_disk(filepath):
    """Load followers from a JSON file."""
    with open(filepath, 'r') as file:
        return json.load(file)
    print("loaded followers.json")

def get_followers(client, target_did):
    """Fetch all followers for the given DID."""
    followers = []
    cursor = None
    while True:
        sleep(.15)
        response = client.app.bsky.graph.get_followers(params={"actor":target_did, "cursor":cursor })
        #print(dir(response))
        followers.extend(response.followers)
        cursor = response.cursor
        if not cursor:
            break
    return followers

def my_followers(client):
    resolved = client.com.atproto.identity.resolve_handle(params={"handle": USERNAME})
    my_did = resolved['did']
    print(f"Resolved myhandle to DID: {my_did}, pulling followers")
    my_followers = get_followers(client, my_did)
    return my_followers


def main():
    # Initialize the client and log in
    client = Client()
    client.login(USERNAME, PASSWORD)
    
    # Resolve the DID of the target account
    resolved = client.com.atproto.identity.resolve_handle(params={"handle": TARGET_HANDLE})
    target_did = resolved['did']
    print(f"Resolved {TARGET_HANDLE} to DID: {target_did}")
    
    # Fetch the followers using client.get_followers
    #followers = get_followers(client, target_did)
    #print(f"Found {len(followers)} followers for {TARGET_HANDLE}")

    # Save followers to disk
    #save_followers_to_disk(followers, FOLLOWERS_FILE)

    # Load followers from disk
    followers = load_followers_from_disk(FOLLOWERS_FILE)
    print(followers[0])
    while input("Do you want to continue? (Y/N): ").strip().lower() != 'y': pass

    # Send follow requests to each follower
    for follower in followers:
        as_json=json.loads(follower)
        print("following: ", as_json)
        follower_did = as_json['did']
        
        try:
            response=client.follow(follower_did)
            print("Response: ", response.dict())
            print("******")
            sleep(.5)
            #check rate limit
            print(f"Followed {as_json['handle']}")
            print("*********************************")
        except Exception as e:
            print(f"Failed to follow {as_json['handle']}: {e}")
            print (e.response)
            print (dir(e.response))
            if e.response.status_code==429:
                reset_timestamp = int(e.response.headers['ratelimit-reset'])
                # Calculate how long to sleep until the rate limit resets
                wait_time = reset_timestamp - time.time()
                if wait_time > 0:
                    minutes=wait_time/60
                    hours=minutes/60
                    print(f"Rate limit exceeded. Waiting for {wait_time}s {minutes}m {hours}h")
                    time.sleep(wait_time)  # Wait for the rate limit to reset
            else:
                print("not 429 status code")
                exit()

if __name__ == "__main__":
    main() 
