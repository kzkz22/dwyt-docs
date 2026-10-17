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


DATA = "https://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData"
ORIGIN = "https://embed.indavideo.hu/"  # what the browser sends as Referer (origin only)
now = int(time.time() * 1000)
ASKS = {  # the video data asked for in several ways; the browser's answer had http_referer = ORIGIN (2026-10-17)
    "yt-dlp, Referer = embed page": (f"{DATA}/{HASH}/?_={now}", EMBED),
    "yt-dlp, Referer = origin": (f"{DATA}/{HASH}/?_={now}", ORIGIN),
    "player, Referer = embed page": (f"{DATA}/{HASH}/12////?https%3A%2F%2Findavideo.hu%2F&_={now}", EMBED),
    "player, Referer = origin": (f"{DATA}/{HASH}/12////?https%3A%2F%2Findavideo.hu%2F&_={now}", ORIGIN),
    "player + callback, Referer = origin": (
        f"{DATA}/{HASH}/12////?https%3A%2F%2Findavideo.hu%2F&callback=jQuery35100_{now}&_={now + 1}", ORIGIN),
}
for ask, (data_url, data_referer) in ASKS.items():
    status, body = get(data_url, referer=data_referer)
    text = body.decode("utf-8", "replace").strip()
    if text.startswith("jQuery"):  # JSONP: strip the callback
        text = text[text.index("(") + 1:text.rindex(")")]
    print(f"\n== {ask}: HTTP {status}")
    if status != 200:
        continue
    data = json.loads(text)["data"]
    print("   http_referer:", data.get("http_referer"), " ref:", data.get("ref"))
    files, tokens = data.get("video_files") or [], data.get("filesh") or {}
    if isinstance(files, dict):
        files = list(files.values())
    for raw in files[:1]:  # the first (smallest) file is enough
        height = next((h for h in tokens if f".{h}.mp4" in raw), None)
        token = tokens.get(height)
        if not token:
            continue
        for referer in (None, ORIGIN):
            code, _ = get(f"{raw}&token={token}", referer=referer, rng=True)
            print(f"   {height}p  {code}  download{', Referer origin' if referer else ''}")
