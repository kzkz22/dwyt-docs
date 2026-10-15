"""Mockups for round 8 (plan 19a, items 1-4), drawn into real dwyt-central pages dumped from its tests.

    python tools/minta_8.py DUMP_DIR OUT_DIR

DUMP_DIR holds inbox-new.html, inbox-done.html, library.html, item.html (the real pages with the real stylesheet);
this script replaces their lists and adds the new controls, then OUT_DIR gets the mockup pages (render them with
tools/render_png.js or any browser at 1280 and 390 px).
"""
import re
import sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

STAR = ('<svg class="icon" width="15" height="15" viewBox="0 0 24 24" fill="{fill}" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-4-7 4V5a2 2 0 0 1 2-2h10'
        'a2 2 0 0 1 2 2z"/></svg>')
CHECK = ('<svg class="icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>')
SPARK = ('<svg class="icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 5.8L20 10l-6.1 1.2L12 17'
         'l-1.9-5.8L4 10l6.1-1.2z"/></svg>')
EXTRA = """<style>
.thumb img{display:none}.thumb{background:linear-gradient(135deg,hsl(215 30% 75%),hsl(215 25% 55%));border-radius:8px;
 min-height:94px}
.item.focus{outline:2px solid hsl(var(--primary));outline-offset:-2px;border-radius:8px}
.keys{display:flex;gap:6px 14px;flex-wrap:wrap;align-items:center;font-size:.8rem;color:hsl(var(--muted-foreground));
 margin:-4px 0 12px}
.keys kbd{display:inline-block;min-width:1.4em;text-align:center;padding:1px 6px;border:1px solid hsl(var(--border));
 border-bottom-width:2px;border-radius:5px;background:hsl(var(--card));font:600 .75rem/1.4 ui-monospace,monospace}
.desc{margin:6px 0 0;font-size:.85rem;color:hsl(var(--muted-foreground));display:-webkit-box;-webkit-line-clamp:2;
 -webkit-box-orient:vertical;overflow:hidden}
.desc b{color:hsl(var(--foreground));font-weight:600}
.unread-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:hsl(var(--primary));
 margin-right:6px;vertical-align:.1em}
.item.read .title{font-weight:500;color:hsl(var(--muted-foreground))}
button.on,.button.on{background:hsl(var(--primary)/.1);color:hsl(var(--primary));border-color:hsl(var(--primary)/.5)}
.row-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.side-toggle{margin-left:auto;align-self:flex-start}
.item.media{align-items:flex-start}
.consent{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.note-box{border:1px dashed hsl(var(--border));border-radius:10px;padding:10px 14px;margin:14px 0;font-size:.85rem;
 color:hsl(var(--muted-foreground))}
.note-box strong{color:hsl(var(--foreground))}
</style>"""


def page(name: str) -> str:
    html = (SRC / f"{name}.html").read_text(encoding="utf-8")
    return html.replace("</head>", EXTRA + "</head>")


def replace_list(html: str, new: str) -> str:
    start = html.index('<ul class="items">')
    end = html.index("</ul>", start) + len("</ul>")
    return html[:start] + new + html[end:]


def save(name: str, html: str) -> None:
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")


def btn(label: str, cls: str = "secondary small", icon: str = "") -> str:
    return f'<button class="{cls}">{icon}{label}</button>'


VIDEOS = [
    ("Helyi LLM 2026-ban: mire elég egy 24 GB-os kártya?", "Otthoni szerverek", "2026-10-15 11:19", "24:10",
     "Megnézzük, mely új nyílt modellek férnek el egy RTX 3090-en, mennyit számít a kvantálás, és hogyan "
     "kapcsolható mindez Home Assistanthez.",
     "A videó azt vizsgálja, hogyan változtatja meg a helyi nyelvi modellek új generációja az otthoni szerverek "
     "használatát: a 30 milliárd paraméteres modellek már egy 24 GB-os kártyán is elfutnak."),
    ("Proxmox 9 frissítés lépésről lépésre", "Otthoni szerverek", "2026-10-15 08:19", "18:45",
     "A Proxmox 8-ról 9-re frissítés buktatói: tárolók, hálózati nevek, a Ceph és a mentések ellenőrzése a "
     "frissítés előtt és után.",
     "Lépésenként mutatja be a frissítést; a legfontosabb a mentés és a pve8to9 ellenőrző futtatása előtte, mert "
     "a hálózati csatolók neve megváltozhat."),
    ("Unraid vagy TrueNAS? Egy év után őszintén", "Otthoni szerverek", "2026-10-15 05:19", "31:02",
     "Egy év napi használat után: tárolás, Docker, virtuális gépek, frissítések és az, hogy melyiket választanám "
     "ma újra.", ""),
    ("Home Assistant: a 10 legjobb automatizmus télre", "Okos otthon", "2026-10-15 04:19", "12:30",
     "Fűtésvezérlés jelenlét alapján, páratartalom-figyelés, fagyvédelem és a reggeli rutin: tíz automatizmus, "
     "amit érdemes beállítani október végéig.", ""),
]
KEYS_NEW = ('<p class="keys"><span>Billentyűk:</span><span><kbd>j</kbd> <kbd>k</kbd> lépés</span><span><kbd>ö</kbd> '
            'összefoglaló kérése</span><span><kbd>m</kbd> megnézendő</span><span><kbd>x</kbd> kihagyás</span></p>')
KEYS_DONE = ('<p class="keys"><span>Billentyűk:</span><span><kbd>j</kbd> <kbd>k</kbd> lépés</span><span><kbd>Enter</kbd> '
             'megnyitás</span><span><kbd>m</kbd> megnézendő</span><span><kbd>x</kbd> elolvastam</span></p>')


def thumb() -> str:
    return '<a class="thumb" href="#"><img alt=""></a>'


# ---- Postaláda, Új ----------------------------------------------------------------------------------
rows = []
for i, (title, ch, when, length, desc, _summary) in enumerate([VIDEOS[2], VIDEOS[3]]):
    saved = i == 1
    rows.append(f'''<li class="item media{' focus' if i == 0 else ''}">{thumb()}<div style="flex:1;min-width:0">
  <span class="title">{title}</span>
  <div class="meta">{ch} · {when} · {length}</div>
  <p class="desc"><b>A videó leírása:</b> {desc}</p>
  <div class="row-actions">{btn("Összefoglaló kérése", "small", SPARK)}
    {btn("Megnézendő" if not saved else "A megnézendő listán", "small on" if saved else "secondary small",
         STAR.format(fill="currentColor" if saved else "none"))}
    {btn("Kihagyás")}</div></div></li>''')
html = page("inbox-new")
html = replace_list(html, '<ul class="items">' + "".join(rows) + "</ul>")
html = html.replace('<ul class="items">', KEYS_NEW + '<ul class="items">', 1)
save("1-postalada-uj", html)

# ---- Postaláda, Kész ------------------------------------------------------------------------------------
rows = []
for i, (title, ch, when, length, _desc, summary) in enumerate(VIDEOS[:2]):
    saved = i == 0
    rows.append(f'''<li class="item media{' focus' if i == 0 else ''}">{thumb()}<div style="flex:1;min-width:0">
  <a class="title" href="#"><span class="unread-dot" title="olvasatlan"></span>{title}</a>
  <div class="meta">{ch} · {when} · {length} · YouTube saját felirat</div>
  <p class="preview">{summary}</p>
  <div class="row-actions">
    {btn("A megnézendő listán" if saved else "Megnézendő", "small on" if saved else "secondary small",
         STAR.format(fill="currentColor" if saved else "none"))}
    {btn("Elolvastam", "secondary small", CHECK)}</div></div></li>''')
html = page("inbox-done")
html = replace_list(html, '<ul class="items">' + "".join(rows) + "</ul>")
html = html.replace('<ul class="items">', KEYS_DONE + '<form class="filters"><label class="choice"><input '
                    'type="checkbox"> Az elolvasottak is</label></form><ul class="items">', 1)
save("2-postalada-kesz", html)

# ---- Könyvtár -----------------------------------------------------------------------------------------
rows = []
for i, (title, ch, when, length, _desc, summary) in enumerate(VIDEOS):
    read = i in (1, 3)
    saved = i == 0
    summary = summary or "A videó összefoglalója itt látszik, két sorban."
    rows.append(f'''<li class="item media{' read' if read else ''}">{thumb()}<div style="flex:1;min-width:0">
  <a class="title" href="#">{'' if read else '<span class="unread-dot" title="olvasatlan"></span>'}{title}</a>
  <div class="meta">{ch} · {length} · {when} · YouTube saját felirat{' · <span class="badge cloud">megnézendő</span>'
                                                                     if saved else ''}</div>
  <p class="preview">{summary}</p></div>
  <button class="{'small on' if saved else 'secondary small'} side-toggle" title="Megnézendő a YouTube-on">
    {STAR.format(fill="currentColor" if saved else "none")}</button></li>''')
html = page("library")
html = replace_list(html, '<ul class="items">' + "".join(rows) + "</ul>")
html = re.sub(r'(<select name="szures"[^>]*>)', r'\1<option>Olvasatlan</option><option>Megnézendő</option>', html,
              count=1)
save("3-konyvtar", html)

# ---- Elem oldala -----------------------------------------------------------------------------------------
html = page("item")
html = html.replace('<div class="actions head-actions">', '''<div class="actions head-actions">
      <button class="small on">''' + STAR.format(fill="currentColor") + '''A megnézendő listán</button>
      <button class="secondary small">''' + CHECK + '''Olvasatlannak jelölés</button>''', 1)
consent = ('<div class="note-box"><strong>Ha még nem engedélyezted (első használat):</strong> a gomb helyett ez '
           'látszik — <span class="consent">„A Megnézendő gomb a YouTube-fiókodban egy <em>dwyt – megnézendő</em> '
           'lejátszási listát kezel. Ehhez egyszer engedélyezd, hogy a dwyt írhasson a lejátszási listáidba.” '
           '<button class="small">Engedélyezés a Google-nál</button></span></div>')
html = html.replace('<nav class="jump"', consent + '<nav class="jump"', 1)
save("4-elem", html)

# ---- Megosztás telefonról --------------------------------------------------------------------------------
html = page("inbox-new")
body = '''<h1>Összefoglaló kérése</h1>
<section class="card">
  <p class="muted">A YouTube-alkalmazásból osztottad meg:</p>
  <div class="item media" style="padding:0;border:0">''' + thumb() + '''<div><span class="title">Unraid vagy TrueNAS? Egy év
    után őszintén</span><div class="meta">Otthoni szerverek · 31:02</div></div></div>
  <form class="stack">
    <label>Átírás <select><option>YouTube-felirat (ha van), különben helyi Whisper</option><option>Helyi Whisper</option>
      <option>Felhős átírás (AssemblyAI)</option></select></label>
    <label class="choice"><input type="checkbox" checked> Összefoglaló</label>
    <label class="choice"><input type="checkbox"> Megnézendő is (a YouTube-fiókodban)</label>
    <p><button>''' + SPARK + '''Kérem</button></p>
    <p class="muted">Ha már a könyvtáradban van, egyenesen az oldalára visz.</p>
  </form>
</section>'''
start = html.index("<h1>")
end = html.index("</main>") if "</main>" in html else html.rindex("</div>")
html = html[:start] + body + html[end:]
save("5-megosztas", html)
print("written:", ", ".join(sorted(p.name for p in OUT.glob("*.html"))))
