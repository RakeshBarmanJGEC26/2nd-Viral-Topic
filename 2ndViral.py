import streamlit as st
import requests
from datetime import datetime, timedelta
import re

# ==============================
# YouTube API Key
# ==============================
API_KEY = "AIzaSyCC_B5qrb2wibpaNIKtIHqUKv4VXqe0tnw"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ==============================
# Streamlit App
# ==============================
st.set_page_config(page_title="YouTube Viral Long-Form (EN)", layout="wide")
st.title("🔥 Viral Long-Form YouTube Videos (English Bias)")

days = st.number_input("Search videos from last N days:", min_value=1, max_value=60, value=5)

# Keywords
keywords = [
    "scary stories",
    "horror stories",
    "true scary stories",
    "scary story compilation",
    "night horror stories",
    "home alone horror stories",
    "airbnb horror stories",
    "hotel horror stories",
    "camping true horror stories",
    "disturbing encounters",
    "chilling true stories"
]

# ==============================
# ISO 8601 Duration Converter
# ==============================
def duration_to_seconds(duration):
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 3600 + minutes * 60 + seconds

# ==============================
# Fetch Button
# ==============================
if st.button("🚀 Fetch Viral Videos"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"🔍 Searching: **{keyword}**")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "relevanceLanguage": "en",  # ✅ ONLY English bias
                "key": API_KEY
            }

            data = requests.get(YOUTUBE_SEARCH_URL, params=search_params).json()
            if "items" not in data or not data["items"]:
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos]
            channel_ids = [v["snippet"]["channelId"] for v in videos]

            # Video details
            video_params = {
                "part": "statistics,contentDetails",
                "id": ",".join(video_ids),
                "key": API_KEY
            }
            video_data = requests.get(YOUTUBE_VIDEO_URL, params=video_params).json()

            # Channel details
            channel_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY
            }
            channel_data = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params).json()

            if "items" not in video_data or "items" not in channel_data:
                continue

            for vid, vdata, cdata in zip(videos, video_data["items"], channel_data["items"]):

                # 🔥 LONG-FORM FILTER (> 2 min)
                duration_seconds = duration_to_seconds(vdata["contentDetails"]["duration"])
                if duration_seconds < 120:
                    continue

                views = int(vdata["statistics"].get("viewCount", 0))
                subs = int(cdata["statistics"].get("subscriberCount", 0))

                all_results.append({
                    "Title": vid["snippet"]["title"],
                    "URL": f"https://www.youtube.com/watch?v={vid['id']['videoId']}",
                    "Views": views,
                    "Subscribers": subs,
                    "Duration (min)": round(duration_seconds / 60, 2)
                })

        # Sort by views (viral first)
        all_results = sorted(all_results, key=lambda x: x["Views"], reverse=True)

        if all_results:
            st.success(f"🔥 Found {len(all_results)} long-form videos (English bias)")
            for r in all_results:
                st.markdown(
                    f"### {r['Title']}\n"
                    f"🕒 **Duration:** {r['Duration (min)']} min  \n"
                    f"👁 **Views:** {r['Views']:,}  \n"
                    f"👥 **Subscribers:** {r['Subscribers']:,}  \n"
                    f"🔗 [Watch Video]({r['URL']})"
                )
                st.write("---")
        else:
            st.warning("❌ No long-form videos found.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
