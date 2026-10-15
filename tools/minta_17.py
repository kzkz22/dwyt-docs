"""Mockups for plan 19a item 17 (AssemblyAI's LLM Gateway as a trial summary model), drawn into the real runner pages.

    python tools/minta_17.py DUMP_DIR OUT_DIR

DUMP_DIR holds step3.html, step4.html, mukodes.html (the runner window's setup steps 3-4 and Működés tab in Felhő
mode, dumped from its tests) and style.css; item.html + central.css from dwyt-central (an item page with a summary).
OUT_DIR gets the mockup pages; render them at 900 px (runner) and 1280 / 390 px (central).
"""
import re
import sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)


def page(name: str) -> str:
    html = (SRC / f"{name}.html").read_text()
    html = re.sub(r'href="/static/style\.css[^"]*"', 'href="style.css"', html)
    return re.sub(r'<script[^>]*src="[^"]*"[^>]*></script>', "", html)


def save(name: str, html: str) -> None:
    (OUT / f"{name}.html").write_text(html)


EXTRA = """<style>
.choice2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
@media (max-width:700px){.choice2{grid-template-columns:1fr}}
.choice2 .modecard{min-height:0}
.note.info{border-color:hsl(213 70% 55% / .5);background:hsl(213 80% 50% / .07)}
</style>"""

# ---- 3. Működési mód: the Felhő card says one registration is enough to try ---------------------------------------
html = page("step3")
html = html.replace("<small>fizetős, a te kulcsaiddal</small>",
                    "<small>fizetős, a te kulcsaiddal · <strong>egy AssemblyAI-regisztrációval kipróbálható</strong> "
                    "(50 $ induló kredit, bankkártya nélkül)</small>", 1)
save("1-mod", html.replace("</head>", EXTRA + "</head>", 1))

# ---- 4. Hozzávalók, Felhő mode: one AssemblyAI key, the summary as a choice ---------------------------------------
html = page("step4")
start = html.index('<section class="card ingredient">')
end = html.index('<section class="card ingredient off">', start)
new = '''<section class="card ingredient">
  <div class="row"><span class="dot green"></span><strong>AssemblyAI-kulcs: átírás és próba-összefoglaló</strong>
    <span class="right muted">kötelező ehhez a módhoz</span></div>
  <form class="form">
    <label>Kulcs<input type="password" placeholder="beállítva – új kulcshoz írd be"></label>
    <p class="muted">Regisztrációkor <strong>50 $ induló kreditet</strong> kapsz, bankkártya nélkül: ez nagyjából
      300 óra átírásra elég. A kulcsot a gép saját, védett kulcstárolójában őrizzük, a dwyt sosem látja.
      <a href="#">Regisztráció és kulcs</a></p>
    <p class="good">Kipróbáltuk: az átírás és a próba-összefoglaló is működik.</p>
    <button>Mentés és próba</button>
  </form>
</section>

<section class="card ingredient">
  <div class="row"><span class="dot green"></span><strong>Ki írja az összefoglalót, a fordítást és a válaszokat?</strong>
    <span class="right muted">később a Működés lapon átállítható</span></div>
  <div class="choice2" role="radiogroup">
    <label class="modecard"><input type="radio" name="llm_provider" checked>
      <span class="name">Az AssemblyAI-kulccsal <span class="badge">próba</span></span>
      <span class="muted">Nem kell újabb regisztráció. Kis, gyors próba-modell (Qwen3.5 4B), szinte ingyenes.</span>
      <small>a magyar szöveg gyengébb lehet</small></label>
    <label class="modecard"><input type="radio" name="llm_provider">
      <span class="name">OpenRouter-kulccsal <span class="badge">jobb minőség</span></span>
      <span class="muted">Bármelyik modell választható, a jobbak magyarul is jól írnak. Külön regisztráció kell.</span>
      <small>centes tétel videónként</small></label>
  </div>
  <div class="note warn"><strong>Mire számíts a próba-modellel?</strong>
    <p>Kis modell: az összefoglaló használható, de lehetnek benne nyelvi botlások, és ritkán elferdít egy számot vagy
      egy nevet – a fontos adatokat ellenőrizd az átiratban. Ingyenes fiókkal csak ez a modell érhető el, és
      percenként kevés kérést enged, ezért a hosszú videók összefoglalója és a fordítás lassabban készül.</p>
    <p>Okosabb modellhez töltsd fel az AssemblyAI-egyenleged (ugyanezzel a kulccsal, a Működés lapon választható
      nagyobb modellek), vagy válaszd az OpenRouter-t. Bármikor átállhatsz.</p></div>
  <p class="good">Kész: ugyanazt a kulcsot használom, a próba-modell: qwen3.5-4b-32k-fast.</p>
</section>

'''
html = html[:start] + new + html[end:]
html = html.replace('<p class="muted right-note">A Tovább gomb akkor lesz aktív, ha a „kell” jelű részek megvannak.</p>', "")
html = html.replace('<button class="primary" disabled>Tovább</button>', '<a class="button primary" href="#">Tovább</a>')
save("2-hozzavalok", html.replace("</head>", EXTRA + "</head>", 1))

# ---- Működés tab: the trial model in the picture and a note with the ways up ---------------------------------------
html = page("mukodes")
html = html.replace('''<strong>Összefoglaló, fordítás, kérdések</strong><span class="muted">felhőben (OpenRouter)</span>
      <span class="cost">fizetős, a te kulcsoddal</span>''', '''<strong>Összefoglaló, fordítás, kérdések</strong><span class="muted">felhőben (AssemblyAI, próba-modell)</span>
      <span class="cost">az AssemblyAI-kreditből</span>''', 1)
html = html.replace('''<strong>Átírás</strong><span class="muted">YouTube-feliratból</span>
      <span class="cost">ingyenes</span>''', '''<strong>Átírás</strong><span class="muted">YouTube-felirat vagy AssemblyAI</span>
      <span class="cost">az AssemblyAI-kreditből</span>''', 1)
note = '''<div class="note warn"><strong>Próba-modell írja az összefoglalókat</strong> (AssemblyAI · Qwen3.5 4B).
  <p>Gyors és szinte ingyenes, de a magyar szöveg gyengébb lehet, és ritkán elferdít egy számot vagy nevet.
    Jobb minőséghez:</p>
  <ul><li>töltsd fel az AssemblyAI-egyenleged, és válassz nagyobb modellt lent, a <em>Részletes beállítások → Nyelvi
    modell</em> alatt (ugyanaz a kulcs), vagy</li>
  <li>add meg egy OpenRouter-kulcsot a <a href="#">Kulcsok</a> lapon, és állítsd át a szolgáltatót.</li></ul></div>
'''
html = html.replace('<p class="muted" data-unsaved hidden>', note + '<p class="muted" data-unsaved hidden>', 1)
save("3-mukodes", html.replace("</head>", EXTRA + "</head>", 1))

# ---- dwyt-central item page: the line under a summary written by the trial model ----------------------------------
if (SRC / "item.html").exists():
    html = (SRC / "item.html").read_text()
    html = re.sub(r'href="/static/style\.css[^"]*"', 'href="central.css"', html)
    html = re.sub(r'<script[^>]*src="[^"]*"[^>]*></script>', "", html)
    html = re.sub(r'<link rel="(?:preload|icon|manifest|apple-touch-icon)"[^>]*>', "", html)
    marker = '<div class="summary summary-text">'
    i = html.index(marker)
    j = html.index("</div>", i) + len("</div>")
    trial = ('\n  <p class="trial-note"><svg class="icon" width="15" height="15" viewBox="0 0 24 24" fill="none" '
             'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" '
             'cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg><span>Próba-modellel készült '
             '(AssemblyAI · Qwen3.5 4B): a magyar szöveg gyengébb lehet, a számokat és a neveket érdemes az átiratban '
             'ellenőrizni. Jobb modellel lent, az <strong>Új összefoglaló</strong> alatt kérheted újra.</span></p>')
    html = html[:j] + trial + html[j:]
    html = html.replace("</head>", """<style>.trial-note{display:flex;gap:8px;align-items:flex-start;margin:10px 0 4px;
padding:8px 12px;border:1px solid hsl(var(--warning-line));background:hsl(var(--warning-bg));border-radius:8px;
font-size:.85rem}.trial-note .icon{flex-shrink:0;margin-top:2px}</style></head>""", 1)
    save("4-elem", html)
print("written:", ", ".join(sorted(p.name for p in OUT.glob("*.html"))))
