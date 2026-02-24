"""
BILI Master System - Dynamic Refresh for Store Pins
Fetches latest video/post from a store's profile URL so pins stay fresh without manual updates.
Supports: YouTube (channel RSS), and noembed.com fallback for direct video/post URLs.
"""
import re
from datetime import datetime
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def _extract_youtube_channel_id(profile_url: str) -> Optional[str]:
    """Extract YouTube channel ID from channel URL or @handle URL."""
    if not profile_url or "youtube.com" not in profile_url and "youtu.be" not in profile_url:
        return None
    # /channel/UCxxxxxxxxxxxxxxxxxx
    m = re.search(r"youtube\.com/channel/([a-zA-Z0-9_-]{20,})", profile_url)
    if m:
        return m.group(1)
    # /@Username or /c/CustomName - we need to resolve to channel ID via page fetch
    m = re.search(r"youtube\.com/(@[a-zA-Z0-9_-]+)", profile_url)
    if m:
        handle = m.group(1).lstrip("@")
        try:
            r = requests.get(
                f"https://www.youtube.com/@{handle}",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; BILI/1.0)"},
            )
            if r.status_code != 200:
                return None
            # Channel page contains channel_id or "externalId" in JSON
            match = re.search(r'"channelId":"(UC[a-zA-Z0-9_-]{22})"', r.text)
            if match:
                return match.group(1)
            match = re.search(r'"externalId":"(UC[a-zA-Z0-9_-]{22})"', r.text)
            if match:
                return match.group(1)
        except Exception:
            pass
    return None


def _fetch_youtube_latest(channel_id: str) -> Optional[dict]:
    """Fetch latest video from YouTube channel RSS. Returns dict with url, thumbnail, title or None."""
    if not HAS_REQUESTS:
        return None
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "BILI/1.0"})
        if r.status_code != 200:
            return None
        text = r.text
        # Parse first entry: videoId, title, thumbnail (regex to avoid namespace issues)
        video_id_m = re.search(r"<yt:videoId>([^<]+)</yt:videoId>", text)
        if not video_id_m:
            video_id_m = re.search(r"<id>yt:video:([^<]+)</id>", text)
        video_id = video_id_m.group(1).strip() if video_id_m else None
        if not video_id:
            return None
        title_m = re.search(r"<title>([^<]+)</title>", text)
        title = title_m.group(1).strip() if title_m else f"Video {video_id}"
        thumb_m = re.search(r'<media:thumbnail\s+url="([^"]+)"', text)
        thumb = thumb_m.group(1) if thumb_m else f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
        return {
            "latest_content_url": f"https://www.youtube.com/watch?v={video_id}",
            "latest_content_thumbnail": thumb,
            "latest_content_title": title,
        }
    except Exception:
        return None


def _fetch_noembed(url: str) -> Optional[dict]:
    """Fetch thumbnail and title via noembed.com for direct video/post URLs."""
    if not HAS_REQUESTS:
        return None
    try:
        r = requests.get(
            "https://noembed.com/embed",
            params={"url": url},
            timeout=10,
            headers={"User-Agent": "BILI/1.0"},
        )
        if r.status_code != 200:
            return None
        data = r.json()
        thumb = data.get("thumbnail_url") or data.get("thumbnail")
        title = data.get("title") or ""
        if not thumb and not title:
            return None
        return {
            "latest_content_url": url,
            "latest_content_thumbnail": thumb,
            "latest_content_title": title,
        }
    except Exception:
        return None


def fetch_latest_content_from_profile(profile_url: str) -> Optional[dict]:
    """
    Fetch latest video or post content from a profile URL.
    Returns dict with latest_content_url, latest_content_thumbnail, latest_content_title,
    or None if fetch failed or URL not supported.
    """
    if not profile_url or not profile_url.strip():
        return None
    profile_url = profile_url.strip()

    # YouTube channel or @handle
    channel_id = _extract_youtube_channel_id(profile_url)
    if channel_id:
        result = _fetch_youtube_latest(channel_id)
        if result:
            return result

    # Fallback: noembed (works for direct YouTube video, Vimeo, etc.)
    return _fetch_noembed(profile_url)


def refresh_pin_content(pin) -> bool:
    """
    Update a ManualMapPin's latest_content_* from its profile_url.
    Returns True if content was updated, False otherwise.
    """
    if not pin.profile_url:
        return False
    content = fetch_latest_content_from_profile(pin.profile_url)
    if not content:
        return False
    pin.latest_content_url = content.get("latest_content_url")
    pin.latest_content_thumbnail = content.get("latest_content_thumbnail")
    pin.latest_content_title = content.get("latest_content_title")
    pin.content_fetched_at = datetime.utcnow()
    return True
