"""Mockups for plan 19a item 18 (the page resolver), drawn into real dwyt-central pages dumped from its tests.

    python tools/minta_18.py DUMP_DIR OUT_DIR

DUMP_DIR holds item.html, library.html, submit.html (a telex.hu page submitted and transcribed) and central.css.
"""
import re
import sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
URL = "https://telex.hu/video/2026/09/27/balogh-petya-uzletember-interju-gen-eu-holnap"
EXTRA = """<style>
.pagecard{margin:14px 0}
.pagecard h2{margin-bottom:6px}
.pick{display:flex;gap:12px;align-items:flex-start;padding:10px 12px;border:1px solid hsl(var(--border));border-radius:10px;
 margin:8px 0}
.pick.chosen{border:2px solid hsl(var(--primary));background:hsl(var(--primary)/.06)}
.pick .ph{width:120px;aspect-ratio:16/9;border-radius:6px;flex-shrink:0;background:linear-gradient(135deg,hsl(0 0% 20%),hsl(0 60% 45%))}
.pick .ph.audio{background:linear-gradient(135deg,hsl(215 30% 75%),hsl(215 25% 55%))}
.pick .what{font-weight:600}
.pick .muted{font-size:.85rem}
.thumb .fake,.cover.fake{display:block;width:168px;aspect-ratio:16/9;border-radius:6px;
 background:linear-gradient(135deg,hsl(35 70% 60%),hsl(10 60% 45%))}
@media (max-width:600px){.thumb .fake{width:112px}.pick .ph{width:80px}}
</style>"""


def page(name: str) -> str:
    html = (SRC / f"{name}.html").read_text()
    html = re.sub(r'href="/static/style\.css[^"]*"', 'href="central.css"', html)
    html = re.sub(r'<script[^>]*src="[^"]*"[^>]*></script>', "", html)
    html = re.sub(r'<link rel="(?:preload|icon|manifest|apple-touch-icon)"[^>]*>', "", html)
    return html.replace("</head>", EXTRA + "</head>", 1)


# ---- item page: what the resolver chose on the page, and the other candidates -------------------------------------
html = page("item")
html = html.replace('<li><span class="fact-k">Forrás</span> Weboldal</li>',
                    '<li><span class="fact-k">Forrás</span> telex.hu (videós oldal)</li>', 1)
html = html.replace('<li><span class="fact-k">Hossz</span> 02:00</li>', '<li><span class="fact-k">Hossz</span> 38:12</li>')
html = re.sub(r'<div class="cover nocover"[^>]*>.*?</div>', '<div class="cover fake" aria-hidden="true"></div>', html,
              count=1, flags=re.S)
card = '''<section class="card pagecard" id="oldal">
  <h2>Az oldalról</h2>
  <p class="muted">A futtató ezt a felvételt találta az oldalon, ebből készült az átirat. Az oldal szövege (a felvezető és a
    kérdések) háttérként az összefoglalóhoz került.</p>
  <div class="pick chosen"><span class="ph"></span><div>
    <div class="what">YouTube-videó <span class="badge cloud">ezt használtuk</span></div>
    <div class="muted">„Balogh Petya: Akinek több tízmilliós cipője van…” · 38:12 ·
      <a href="#">youtube.com/watch?v=I3eE-GoA57M</a></div>
    <div class="muted">A YouTube saját felirata volt hozzá: gyors és ingyenes.</div></div></div>
  <details><summary>Más is van az oldalon (1)</summary>
    <form class="stack">
      <label class="pick"><span class="ph audio"></span><span><input type="radio" name="pick" checked>
        <span class="what">Podcast-hangfájl</span><br><span class="muted">audio-assets.telex.hu · a cikk napjáról
        (2026. 09. 27.)</span></span></label>
      <p><button class="secondary small">Átírás ebből</button>
        <span class="muted">Új átirat készül; a mostani megmarad, a fő átiratot te választod.</span></p>
    </form>
  </details>
</section>
'''
html = html.replace('<nav class="jump"', card + '<nav class="jump"', 1)
(OUT / "1-elem.html").write_text(html)

# ---- library row: the page's picture, the site, the source the resolver chose -------------------------------------
html = page("library")
html = html.replace('<span class="nothumb">nincs kép</span>', '<span class="fake"></span>', 1)
html = re.sub(r'Telex · \s*02:00 · \s*(2026-[0-9-]+ [0-9:]+)\s*· Helyi Whisper \(universal-2\) \(hu\)',
              r'telex.hu · Telex · 38:12 · \1 · YouTube saját felirat, az oldalról (hu)', html, count=1)
(OUT / "2-konyvtar.html").write_text(html)

# ---- submit page: any page with a video or a podcast ----------------------------------------------------------------
html = page("submit")
html = html.replace('''<label>Videó URL-je <input name="url" value="" placeholder="https://www.youtube.com/watch?v=…"></label>''',
                    '''<label>Videó vagy oldal címe <input name="url" value="''' + URL + '''"></label>
    <p class="muted">YouTube, vagy egy oldal, amelyen videó vagy podcast van (például Telex, 444, HVG, Index,
      Indavideo, Facebook-videó). Az oldalon a futtató keresi meg a felvételt; ha YouTube-videót talál, annak a
      feliratát is használhatja.</p>''', 1)
(OUT / "3-uj.html").write_text(html)
print("written:", ", ".join(sorted(p.name for p in OUT.glob("*.html"))))
