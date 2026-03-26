import streamlit as st
import requests
from datetime import datetime, timedelta
import re

# ==============================
# YouTube API Key
# ==============================
API_KEY = "AIzaSyCC_B5qrb2wibpaNIKtIHqUKv4VXqe0tnw"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL  = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ==============================
# Streamlit Config
# ==============================
st.set_page_config(page_title="Viral Horror Channel Discovery", layout="wide")
st.title("🎃 Viral Horror Channel Discovery Engine")
st.caption("🇺🇸 USA · English Only · 18min+ · Under 10K Subs · 18K+ Views · Max 14 Days")

days = st.number_input("Search from last N days:", min_value=1, value=14)

# ==============================
# Strategy 1 — Narrative Title Patterns
# How real viral horror creators title videos
# ==============================
narrative_keywords = [
    "I didn't realize until it was too late",
    "something was wrong with my neighbor",
    "I should have left when I had the chance",
    "I need to tell someone what happened",
    "there was someone in my house",
    "I don't think I was alone",
    "I took a job I never should have",
    "this actually happened to me",
    "something wasn't right about him",
    "I wish I had never gone back",
    "alone in the woods at night",
    "followed home at night",
    "the man who watched my house",
    "stranger kept coming back to my door",
    "realized I was being watched",
    "man outside my window every night",
    "found something disturbing in the woods",
    "something was living near my home",
    "stayed overnight and regretted it",
    "my neighbor scared me for months",
    "I was being stalked and didn't know",
    "he knew things he shouldn't have known",
    "I never should have answered that door",
    "something was wrong with the house",
    "the noises started on the third night"
]

# ==============================
# Strategy 2 — Broad Horror Keywords
# Covers every major horror sub-niche
# ==============================
broad_keywords = [

    # Core Narration Genre
    "true scary stories",
    "real horror stories",
    "scary story narration",
    "horror story narration",
    "scary stories for the night",
    "long scary story",
    "horror narration",
    "scary bedtime stories",
    "chilling true stories",
    "disturbing true stories",

    # Psychological & Subtle Horror
    "psychological horror story",
    "true psychological horror",
    "unsettling true stories",
    "deeply disturbing stories",
    "creepy but true stories",
    "true horror experience",
    "real life horror story",
    "nightmare true story",
    "horror that actually happened",

    # Reddit-Style Source
    "reddit horror stories",
    "reddit let's not meet",
    "reddit nosleep story",
    "reddit creepy stories",
    "reddit scary encounter",
    "reddit stalker story",
    "reddit disturbing experience",
    "nosleep horror story",

    # Encounter & Stalker
    "creepy encounter stories",
    "stalker true story",
    "real stalker experience",
    "being followed horror story",
    "stranger danger true story",
    "creepy man true story",
    "followed home true story",
    "predator encounter story",
    "scary person encounter",

    # Location-Based
    "alone in the woods horror",
    "camping horror story",
    "forest encounter true story",
    "cabin horror true story",
    "hiking horror story",
    "rural horror story",
    "small town horror story",
    "night shift horror story",
    "graveyard shift horror story",
    "hospital horror story",
    "hotel horror story",
    "airbnb horror story",
    "apartment horror story",
    "neighborhood horror story",

    # Relationship & Social Horror
    "neighbor horror story",
    "coworker horror story",
    "date gone wrong horror story",
    "roommate horror story",
    "landlord horror story",
    "online stranger horror story",
    "tinder date horror story",

    # Job & Situation Horror
    "security guard horror story",
    "delivery driver horror story",
    "babysitter horror story",
    "rideshare horror story",
    "uber driver horror story",
    "night job horror story",

    # High Performing Title Formats
    "something was wrong horror story",
    "I was being watched true story",
    "I survived horror story",
    "true crime horror story",
    "scary true crime narration",
    "horror story that kept me up",
    "true story that gave me chills"
]

# ==============================
# ISO 8601 Duration Converter
# ==============================
def duration_to_seconds(duration):
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)
    if not match:
        return 0
    hours   = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

# ==============================
# Hard English-Only Filter
# Blocks Hindi, Urdu, Arabic scripts
# and romanized non-English titles
# ==============================
def is_english(text):
    # Block Devanagari script (Hindi, Marathi, Nepali)
    if re.search(r'[\u0900-\u097F]', text):
        return False
    # Block Arabic / Urdu script
    if re.search(r'[\u0600-\u06FF]', text):
        return False
    # Block Bengali script
    if re.search(r'[\u0980-\u09FF]', text):
        return False
    # Block Tamil script
    if re.search(r'[\u0B80-\u0BFF]', text):
        return False
    # Block Telugu script
    if re.search(r'[\u0C00-\u0C7F]', text):
        return False
    # Block common romanized Hindi/Urdu title markers
    non_english_markers = [
        'hindi', 'bhoot', 'darr', 'kahani', 'kahaniya',
        'bhutiya', 'darawani', 'bhutni', 'horror hindi',
        'scary hindi', 'hindi horror', 'hindi story',
        'horror urdu', 'urdu horror', 'urdu story',
        'urdu kahani', 'sachi kahani', 'desi horror',
        'pakistani horror', 'indian horror hindi',
        'bhootiya', 'raat ko', 'andheri raat'
    ]
    lower = text.lower()
    for marker in non_english_markers:
        if marker in lower:
            return False
    return True

# ==============================
# Core Fetch & Filter Function
# ==============================
def fetch_and_filter(search_params, seen_ids):
    results = []

    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params=search_params, timeout=10)
        data = response.json()
    except Exception:
        return results

    if "items" not in data or not data["items"]:
        return results

    # Deduplicate + Hard English filter at title level
    unique_videos = []
    for v in data["items"]:
        vid_id = v["id"].get("videoId")
        title  = v["snippet"].get("title", "")
        if vid_id and vid_id not in seen_ids and is_english(title):
            seen_ids.add(vid_id)
            unique_videos.append(v)

    if not unique_videos:
        return results

    video_ids   = [v["id"]["videoId"] for v in unique_videos]
    channel_ids = list(set([v["snippet"]["channelId"] for v in unique_videos]))

    # Fetch video details
    try:
        video_data = requests.get(YOUTUBE_VIDEO_URL, params={
            "part": "statistics,contentDetails",
            "id": ",".join(video_ids),
            "key": API_KEY
        }, timeout=10).json()

        channel_data = requests.get(YOUTUBE_CHANNEL_URL, params={
            "part": "statistics",
            "id": ",".join(channel_ids),
            "key": API_KEY
        }, timeout=10).json()
    except Exception:
        return results

    if "items" not in video_data or "items" not in channel_data:
        return results

    # Build channel subscriber map
    channel_sub_map = {}
    for c in channel_data["items"]:
        channel_sub_map[c["id"]] = int(c["statistics"].get("subscriberCount", 0))

    # Build video stats map
    video_stats_map = {}
    for vdata in video_data["items"]:
        video_stats_map[vdata["id"]] = vdata

    for vid in unique_videos:
        vid_id   = vid["id"]["videoId"]
        vdata    = video_stats_map.get(vid_id)
        if not vdata:
            continue

        # Duration filter — minimum 18 minutes
        duration_seconds = duration_to_seconds(vdata["contentDetails"]["duration"])
        if duration_seconds < 1080:
            continue

        views      = int(vdata["statistics"].get("viewCount", 0))
        channel_id = vid["snippet"]["channelId"]
        subs       = channel_sub_map.get(channel_id, 0)

        # Views filter — minimum 18,000
        if views < 18000:
            continue

        # Subscriber filter — under 10,000 only
        if subs >= 10000:
            continue

        ratio = round(views / subs, 1) if subs > 0 else 0

        results.append({
            "Title"          : vid["snippet"]["title"],
            "Channel"        : vid["snippet"]["channelTitle"],
            "ChannelID"      : channel_id,
            "Published"      : vid["snippet"]["publishedAt"][:10],
            "URL"            : f"https://www.youtube.com/watch?v={vid_id}",
            "Views"          : views,
            "Subscribers"    : subs,
            "Duration (min)" : round(duration_seconds / 60, 2),
            "Views/Sub Ratio": ratio
        })

    return results

# ==============================
# Main Search Button
# ==============================
if st.button("🚀 Discover Viral Horror Channels"):
    try:
        start_date          = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results         = []
        seen_ids            = set()
        discovered_channels = set()

        total_passes = len(narrative_keywords) + len(broad_keywords)
        progress     = st.progress(0)
        status       = st.empty()

        # ─────────────────────────────────────────
        # PASS 1 — Narrative Title Pattern Search
        # ─────────────────────────────────────────
        st.markdown("### 🔎 Pass 1 — Narrative Title Patterns")
        for i, keyword in enumerate(narrative_keywords):
            status.write(f"Searching: **{keyword}**")
            progress.progress((i + 1) / total_passes)

            found = fetch_and_filter({
                "part"            : "snippet",
                "q"               : keyword,
                "type"            : "video",
                "order"           : "viewCount",
                "publishedAfter"  : start_date,
                "maxResults"      : 10,
                "regionCode"      : "US",
                "relevanceLanguage": "en",
                "videoDuration"   : "long",
                "safeSearch"      : "none",
                "key"             : API_KEY
            }, seen_ids)

            all_results.extend(found)
            for r in found:
                discovered_channels.add(r["ChannelID"])

        # ─────────────────────────────────────────
        # PASS 2 — Broad Horror Keyword Search
        # ─────────────────────────────────────────
        st.markdown("### 🔎 Pass 2 — Broad Horror Keywords")
        for i, keyword in enumerate(broad_keywords):
            status.write(f"Searching: **{keyword}**")
            progress.progress((len(narrative_keywords) + i + 1) / total_passes)

            found = fetch_and_filter({
                "part"            : "snippet",
                "q"               : keyword,
                "type"            : "video",
                "order"           : "viewCount",
                "publishedAfter"  : start_date,
                "maxResults"      : 10,
                "regionCode"      : "US",
                "relevanceLanguage": "en",
                "videoDuration"   : "long",
                "safeSearch"      : "none",
                "key"             : API_KEY
            }, seen_ids)

            all_results.extend(found)
            for r in found:
                discovered_channels.add(r["ChannelID"])

        # ─────────────────────────────────────────
        # PASS 3 — Channel Deep Dive
        # Sweeps all discovered channels for more
        # recent uploads that keywords may have missed
        # ─────────────────────────────────────────
        st.markdown("### 🔎 Pass 3 — Channel Deep Dive")
        channel_list = list(discovered_channels)
        for i, channel_id in enumerate(channel_list):
            status.write(f"Deep diving channel {i + 1} of {len(channel_list)}")

            found = fetch_and_filter({
                "part"          : "snippet",
                "channelId"     : channel_id,
                "type"          : "video",
                "order"         : "viewCount",
                "publishedAfter": start_date,
                "maxResults"    : 5,
                "videoDuration" : "long",
                "key"           : API_KEY
            }, seen_ids)

            all_results.extend(found)

        progress.empty()
        status.empty()

        # Sort by Views/Sub Ratio — most underdog viral first
        all_results = sorted(all_results, key=lambda x: x["Views/Sub Ratio"], reverse=True)

        # ─────────────────────────────────────────
        # Results Display
        # ─────────────────────────────────────────
        if all_results:
            st.success(f"✅ Found **{len(all_results)}** viral horror videos from small channels")

            for r in all_results:
                ratio = r["Views/Sub Ratio"]
                if ratio >= 10:
                    badge = "🔥 MEGA VIRAL"
                elif ratio >= 5:
                    badge = "⚡ VIRAL"
                else:
                    badge = "📈 TRENDING"

                st.markdown(
                    f"### {r['Title']}\n"
                    f"{badge}  \n"
                    f"🕒 **Duration:** {r['Duration (min)']} min  \n"
                    f"👁 **Views:** {r['Views']:,}  \n"
                    f"👥 **Subscribers:** {r['Subscribers']:,}  \n"
                    f"📊 **Views/Sub Ratio:** {ratio}x  \n"
                    f"📅 **Published:** {r['Published']}  \n"
                    f"📺 **Channel:** {r['Channel']}  \n"
                    f"🔗 [Watch Video]({r['URL']})"
                )
                st.write("---")
        else:
            st.warning("❌ No matching videos found. Try increasing the day range.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
