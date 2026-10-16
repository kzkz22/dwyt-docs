"""Where is the video or the audio on a page yt-dlp does not know? (plan 19a item 18, the page resolver)
Standard library only; run it with the runner's Python:

    python oldal_proba.py URL

It downloads the page the way a plain HTTP client sees it (no JavaScript) and lists what a resolver could use:
YouTube ids, podcast players and hosts, audio/video file links, oEmbed / Open Graph / JSON-LD hints, and the
script blocks that hold the page's data (where a JavaScript player usually takes its source from).
"""
import json
import re
import sys
import urllib.request

PODCAST_HOSTS = ("spotify.com", "anchor.fm", "megaphone.fm", "simplecast", "acast", "buzzsprout", "podbean",
                 "libsyn", "soundcloud", "transistor.fm", "captivate", "omny", "podigee", "apple.com/podcast",
                 "podcasts.apple", "castos", "ausha", "redcircle", "spreaker", "audioboom", "rss", "feed")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Használat: python oldal_proba.py URL")
    url = sys.argv[1]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) dwyt-proba",
                                               "Accept-Language": "hu,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", "replace")
    print(f"Letöltve: {len(html)} karakter\n")

    yt = sorted(set(re.findall(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|shorts/|live/)|youtu\.be/|"
                               r"[\"']videoId[\"']\s*:\s*[\"'])([A-Za-z0-9_-]{11})", html)))
    print("YouTube-azonosítók:", ", ".join(yt) or "nincs")

    media = sorted(set(m for m in re.findall(r"https?:[^\"'\s<>]+?\.(?:mp3|m4a|aac|ogg|opus|mp4|m3u8)(?:\?[^\"'\s<>]*)?",
                                             html.replace("\\/", "/"))))
    print("Hang- és videófájlok:", *(media[:15] or ["nincs"]), sep="\n  ")

    hosts = sorted(set(m for m in re.findall(r"https?://[^\"'\s<>]+", html.replace("\\/", "/"))
                       if any(h in m.lower() for h in PODCAST_HOSTS)))
    print("Podcast-szolgáltatók, RSS:", *(hosts[:20] or ["nincs"]), sep="\n  ")

    iframes = re.findall(r"<iframe[^>]+src=[\"']([^\"']+)", html, re.I)
    print("Beágyazott iframe-ek:", *(iframes[:10] or ["nincs"]), sep="\n  ")

    for prop in ("og:video", "og:video:url", "og:audio", "og:type", "twitter:player"):
        found = re.findall(rf"<meta[^>]+(?:property|name)=[\"']{re.escape(prop)}[\"'][^>]+content=[\"']([^\"']+)",
                           html, re.I)
        if found:
            print(f"{prop}: {found[0]}")
    oembed = re.findall(r"<link[^>]+type=[\"']application/json\+oembed[\"'][^>]+href=[\"']([^\"']+)", html, re.I)
    if oembed:
        print("oEmbed:", oembed[0])

    for block in re.findall(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", html, re.S | re.I):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and item.get("@type") in ("VideoObject", "AudioObject", "PodcastEpisode"):
                print("JSON-LD:", item.get("@type"), item.get("embedUrl") or item.get("contentUrl") or item.get("url"))

    print("\nAdatokat tartalmazó script-blokkok (név, méret):")
    for name in ("__NUXT__", "__NEXT_DATA__", "__INITIAL_STATE__", "__APOLLO_STATE__", "window.__data"):
        i = html.find(name)
        if i >= 0:
            print(f"  {name}: a {i}. karakternél")
    print("\nA szöveg körül, ahol 'youtube' vagy 'podcast' szerepel (legfeljebb 5 hely):")
    for m in list(re.finditer(r"youtube|podcast|audio", html, re.I))[:5]:
        print("  …" + html[max(0, m.start() - 120):m.start() + 160].replace("\n", " ") + "…")


if __name__ == "__main__":
    main()
