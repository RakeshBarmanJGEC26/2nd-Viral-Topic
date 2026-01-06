import streamlit as st
import requests
from datetime import datetime, timedelta
import re

# YouTube API Key
API_KEY = "AIzaSyCC_B5qrb2wibpaNIKtIHqUKv4VXqe0tnw"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=60, value=5)

# Keywords
keywords = [
    "scary stories","horror stories","8 Most Disturbing Things Caught on Doorbell Camera Footage","Chilling Scares","disturbing forest encounters","real forest horror stories","10 scary stories","true scary stories","night horror stories","scary story compilation","true nighttime horror stories","home alone horror stories","airbnb horror stories","hotel horror stories","night car drive horror stories","night drive scary stories","halloween horror stories","food delivery horror stories","camping true horror stories"
]

# Convert ISO 8601 duration to seconds
def duration_to_seconds(duration):
    pattern = re.compile(r'PT(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)
    minutes = int(match.group(1)) if match.group(1) else 0
    seconds = int(match.group(2)) if match.group(2) else 0
    return minutes * 60 + seconds

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos]
            channel_ids = [v["snippet"]["channelId"] for v in videos]

            # Get video stats + duration
            video_params = {
                "part": "statistics,contentDetails",
                "id": ",".join(video_ids),
                "key": API_KEY
            }
            video_response = requests.get(YOUTUBE_VIDEO_URL, params=video_params)
            video_data = video_response.json()

            if "items" not in video_data:
                continue

            # Get channel stats
            channel_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY
            }
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data:
                continue

            for vid, vdata, cdata in zip(videos, video_data["items"], channel_data["items"]):

                duration = vdata["contentDetails"]["duration"]
                duration_seconds = duration_to_seconds(duration)

                # 🔥 FILTER: less than 2 minutes (120 seconds)
                if duration_seconds >= 120:
                    continue

                subs = int(cdata["statistics"].get("subscriberCount", 0))
                if subs >= 3000000:
                    continue

                views = int(vdata["statistics"].get("viewCount", 0))

                all_results.append({
                    "Title": vid["snippet"]["title"],
                    "Description": vid["snippet"]["description"][:200],
                    "URL": f"https://www.youtube.com/watch?v={vid['id']['videoId']}",
                    "Views": views,
                    "Subscribers": subs,
                    "Duration (sec)": duration_seconds
                })

        if all_results:
            st.success(f"Found {len(all_results)} SHORT videos (<2 min)!")
            for r in all_results:
                st.markdown(
                    f"**Title:** {r['Title']}  \n"
                    f"**Duration:** {r['Duration (sec)']} sec  \n"
                    f"**Views:** {r['Views']}  \n"
                    f"**Subscribers:** {r['Subscribers']}  \n"
                    f"**URL:** [Watch]({r['URL']})"
                )
                st.write("---")
        else:
            st.warning("No short videos found.")

    except Exception as e:
        st.error(f"Error: {e}")
