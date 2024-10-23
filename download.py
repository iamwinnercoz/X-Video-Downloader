import tweepy
import requests
import re
import os
import json


def load_api_keys(file_path):
    # Step 1: Load API keys from JSON file
    with open(file_path, "r") as f:
        keys = json.load(f)
    return keys


# Step 2: Load the credentials from a config.json file
config_file = "config.json"
keys = load_api_keys(config_file)

# Step 3: Set up Twitter API credentials (loaded from JSON)
API_KEY = keys["API_KEY"]
API_KEY_SECRET = keys["API_KEY_SECRET"]
ACCESS_TOKEN = keys["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = keys["ACCESS_TOKEN_SECRET"]

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def get_video_url(tweet_url):
    # Step 4: Extract the tweet ID from the tweet URL
    tweet_id = tweet_url.split("/")[-1]

    try:
        # Step 5: Get tweet's media information
        tweet = api.get_status(tweet_id, tweet_mode="extended")
        media = tweet.entities.get("media", [])

        if len(media) > 0 and "video_info" in media[0]:
            video_info = media[0]["video_info"]
            variants = video_info["variants"]

            # Step 6: Find the highest bitrate video URL
            video_url = max(variants, key=lambda x: x.get("bitrate", 0))["url"]
            return video_url
        else:
            print("No video found in the tweet.")
            return None
    except tweepy.errors.Forbidden as e:  # Updated exception
        print(f"Error: {e}")
        return None
    except tweepy.errors.TooManyRequests as e:  # Handle rate limit
        print(f"Rate limit exceeded: {e}")
        return None
    except Exception as e:  # Catch-all for any other exceptions
        print(f"An error occurred: {e}")
        return None


def download_video(video_url, save_path):
    # Step 7: Download the video
    if video_url:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as video_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        video_file.write(chunk)
            print(f"Video downloaded successfully: {save_path}")
        else:
            print(f"Failed to download video. Status code: {response.status_code}")


if __name__ == "__main__":
    tweet_url = input("Enter the tweet URL: ")
    video_url = get_video_url(tweet_url)

    if video_url:
        file_name = re.sub(r"[^\w\s]", "", tweet_url.split("/")[-1])  # Clean filename
        save_path = os.path.join(os.getcwd(), f"{file_name}.mp4")
        download_video(video_url, save_path)
