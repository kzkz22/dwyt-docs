"""Which Indavideo download address works? (plan 19a item 18: yt-dlp's IndavideoEmbed gets HTTP 403, 2026-10-16)

    python inda_proba.py [embed hash]          (default: 3bd2eb26b3)

Fetches the player's video data like the player does, then asks for the first bytes of the video file in several
ways and prints the HTTP status of each. Standard library only; nothing is saved.
"""
import json
import sys
import time
import urllib.error
import urllib.request

HASH = sys.argv[1] if len(sys.argv) > 1 else "3bd2eb26b3"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
EMBED = f"https://embed.indavideo.hu/player/video/{HASH}"


def get(url, referer=None, rng=False):
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    if rng:
        headers["Range"] = "bytes=0-1023"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read(2048 if rng else 10_000_000)
    except urllib.error.HTTPError as exc:
        return exc.code, b""


status, body = get(f"https://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/{HASH}/"
                   f"?_={int(time.time())}", referer=EMBED)
print("video data:", status)
data = json.loads(body)["data"]
files, tokens = data.get("video_files") or [], data.get("filesh") or {}
if isinstance(files, dict):
    files = list(files.values())
print("files:", files)
print("tokens:", tokens)

for raw in files:
    height = next((h for h in tokens if f".{h}.mp4" in raw), None)
    token = tokens.get(height)
    if not token:
        continue
    base, _, query = raw.partition("?")
    clean_query = "&".join(p for p in query.lstrip("?").split("&") if p)
    variants = {
        "yt-dlp style (single ?)": f"{base}?{clean_query}&token={token}",
        "as given (??&) + token": f"{raw}&token={token}",
    }
    for host in ("index1-hu", "magex1-hu"):
        for name, url in list(variants.items()):
            if host not in url:
                variants[f"{name}, host {host}"] = url.replace("magex1-hu", host).replace("index1-hu", host)
    print(f"\n{height}p")
    for name, url in variants.items():
        for referer in (None, "https://embed.indavideo.hu/"):
            code, _ = get(url, referer=referer, rng=True)
            print(f"  {code}  {name}{', Referer embed' if referer else ''}")
