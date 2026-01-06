import streamlit as st
import requests
import re

# ==============================
# YouTube API Key
# ==============================
API_KEY = "AIzaSyCC_B5qrb2wibpaNIKtIHqUKv4VXqe0tnw"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ==============================
# Streamlit App
# ==============================
st.set_page_config(page_title="YouTube Long-Form Finder", layout="wide")
st.title("🔥 Long-Form Viral YouTube Videos (English Bias)")

keywords = [
    "scary stories",
    "horror stories",
    "true scary stories",
    "scary story compilation",
    "night horror stories",
    "airbnb horror stories",
    "hotel horror stories",
    "camping true horror stories",
    "disturbing true stories"
]

# ==============================
# Duration Converter
# ==============================
def duration_to_seconds(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    h = int(match.group(1)) if match.group(1) else 0
    m = int(match.group(2)) if match.group(2) else 0
    s = int(match.group(3)) if match.group(3) else 0
    return h * 3600 + m * 60 + s

# ==============================
# Fetch Button
# ==============================
if st.button("🚀 Fetch Long-Form Videos"):
    try:
        results = []

        for keyword in keywords:
            st.write(f"🔍 Searching: **{keyword}**")

            # 🔥 KEY FIX IS HERE
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "videoDuration": "long",     # ✅ THIS SOLVES EVERYTHING
                "maxResults": 25,
                "relevanceLanguage": "en",
                "key": API_KEY
            }

            search_data = requests.get(SEARCH_URL, params=search_params).json()
            if "items" not in search_data or not search_data["items"]:
                continue

            video_ids = [i["id"]["videoId"] for i in search_data["items"]]
            channel_ids = [i["snippet"]["channelId"] for i in search_data["items"]]

            video_data = requests.get(
                VIDEO_URL,
                params={
                    "part": "contentDetails,statistics",
                    "id": ",".join(video_ids),
                    "key": API_KEY
                }
            ).json()

            channel_data = requests.get(
                CHANNEL_URL,
                params={
                    "part": "statistics",
                    "id": ",".join(channel_ids),
                    "key": API_KEY
                }
            ).json()

            for i in range(min(len(video_data["items"]), len(channel_data["items"]))):
                v = video_data["items"][i]
                c = channel_data["items"][i]

                duration_sec = duration_to_seconds(v["contentDetails"]["duration"])

                # Extra safety (optional)
                if duration_sec < 120:
                    continue

                results.append({
                    "Title": search_data["items"][i]["snippet"]["title"],
                    "URL": f"https://www.youtube.com/watch?v={video_ids[i]}",
                    "Views": int(v["statistics"].get("viewCount", 0)),
                    "Subscribers": int(c["statistics"].get("subscriberCount", 0)),
                    "Duration (min)": round(duration_sec / 60, 2)
                })

        results = sorted(results, key=lambda x: x["Views"], reverse=True)

        if results:
            st.success(f"🔥 Found {len(results)} LONG-FORM videos")
            for r in results:
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
        st.error(f"Error: {e}")
