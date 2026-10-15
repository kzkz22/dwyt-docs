"""Mockups for round 7d, drawn in the real dwyt shell and stylesheet."""
import json
import re
import sys
from pathlib import Path

S = Path(sys.argv[1])
STATIC = Path(sys.argv[2])
schema = json.loads(Path(sys.argv[3]).read_text())
shell = (S / "shell.html").read_text().splitlines()
head = "\n".join(shell[:107])
tail = "\n".join(shell[269:])
head = re.sub(r'"/static/([^"?]*)[^"]*"', lambda m: f'"file://{STATIC}/{m.group(1)}"', head)
tail = re.sub(r'"/static/([^"?]*)[^"]*"', lambda m: f'"file://{STATIC}/{m.group(1)}"', tail)
head = head.replace("<title>Futtatók · dwyt</title>", "<title>Minta · dwyt</title>")

EXTRA = """<style>
.mock-tabs{display:flex;gap:.25rem;border-bottom:1px solid hsl(var(--border));margin:.5rem 0 1rem}
.mock-tabs span{padding:.5rem .9rem;border-bottom:2px solid transparent;color:hsl(var(--muted-foreground))}
.mock-tabs span.on{border-color:hsl(var(--primary));color:hsl(var(--foreground));font-weight:600}
.cmd{display:flex;gap:.5rem;align-items:stretch;flex-wrap:wrap}
.cmd code{flex:1 1 320px;display:block;padding:.75rem .9rem;border-radius:.5rem;background:hsl(var(--muted));font-size:.9rem;word-break:break-all}
.modes{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:.6rem;margin:.4rem 0 .2rem}
.modes label{border:1px solid hsl(var(--border));border-radius:.6rem;padding:.6rem .75rem;display:flex;flex-direction:column;gap:.2rem;cursor:pointer}
.modes label.on{border:2px solid hsl(var(--primary));background:hsl(var(--primary)/.06)}
.field{display:grid;grid-template-columns:minmax(180px,260px) 1fr;gap:.35rem 1rem;padding:.7rem 0;border-top:1px solid hsl(var(--border));align-items:start}
.field:first-of-type{border-top:0}
.field .lbl{font-weight:600}
.field .help{grid-column:2;color:hsl(var(--muted-foreground));font-size:.85rem;margin:0}
.field.off{opacity:.6}
.field input[type=text],.field input[type=password],.field select,.field textarea{width:100%;max-width:440px}
.secret{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}
.lock{font-size:.85rem;color:hsl(var(--muted-foreground))}
.savebar{display:flex;gap:.75rem;align-items:center;justify-content:flex-end;padding:.75rem 0;background:hsl(var(--background));border-top:1px solid hsl(var(--border));flex-wrap:wrap}
.state{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap}
.log td,.log th{padding:.5rem .6rem;text-align:left;vertical-align:top}
.log{width:100%;border-collapse:collapse}
.card .table-wrap{overflow-x:auto}
@media (max-width:640px){.log thead{display:none}.log tr{display:block;padding:.5rem 0}.log td{display:block;padding:.15rem 0}.log tr+tr td{border-top:0}.log tr+tr{border-top:1px solid hsl(var(--border))}}
.log tr+tr td{border-top:1px solid hsl(var(--border))}
.spin{display:inline-block;width:.9rem;height:.9rem;border:2px solid hsl(var(--border));border-top-color:hsl(var(--primary));border-radius:50%}
@media (max-width:640px){.field{grid-template-columns:1fr}.field .help{grid-column:1}}
</style>"""


def page(name, body):
    (S / "m7d" / f"{name}.html").write_text(head.replace("</head>", EXTRA + "</head>") + body + tail)


# ---- 1: the runners page --------------------------------------------------------------------
page("1-futtatok", """
<h1>Futtatók</h1>
<p class="muted">A futtató a saját gépeden vagy VPS-eden végzi el a munkát (letöltés, felirat, átírás, összefoglaló, kérdések); a kulcsaid nála maradnak.</p>
<h2>Párosított futtatók</h2>
<section class="card runner">
  <div class="bar"><span class="runner-name"><strong>Otthoni LXC</strong> <span class="badge own">elérhető</span> <span class="badge cloud">a dwyt-ből állítható</span></span>
    <span class="runner-actions"><button class="small">Beállítás</button><button class="secondary small">Kikapcsolás</button><button class="danger small">Visszavonás</button></span></div>
  <div class="meta">dwyt-runner 0.9.9 · <strong>újabb van: 0.10.0</strong> <button class="small">Frissítés most</button> · utoljára: 2026-10-15 07:14 · LLM-szerver: LiteLLM</div>
  <p class="muted">… átírás, nyelvi modellek, megosztás – mint eddig …</p>
</section>
<section class="card runner">
  <div class="bar"><span class="runner-name"><strong>DESKTOP-7U2KT4C</strong> <span class="badge own">elérhető</span></span>
    <span class="runner-actions"><button class="small" disabled title="A futtató ablakában kapcsolható be: Működés → A dwyt-ből is állítható">Beállítás</button><button class="secondary small">Kikapcsolás</button><button class="danger small">Visszavonás</button></span></div>
  <div class="meta">dwyt-runner 0.10.0 · asztali alkalmazás · a beállítás a gép ablakában történik (a dwyt-ből állítás ott kapcsolható be) · utoljára: 2026-10-15 07:12</div>
</section>
<section class="card">
  <h2>Új futtató</h2>
  <div class="mock-tabs"><span class="on">Szerverre (Linux)</span><span>Asztali gépre</span><span>Párosítás kóddal</span></div>
  <p>Másold be ezt a parancsot a szerveren (VPS, LXC, NAS) – rendszergazdaként vagy a saját felhasználóddal:</p>
  <div class="cmd"><code>curl -fsSL https://dwyt.iodate.date/futtato.sh | sh -s -- K7Q2-M9XA</code><button class="small">Másolás</button></div>
  <p class="muted">A parancs 5 percig érvényes, egyszer használható. Telepíti a futtatót (uv-vel, rendszergazdai jog nélkül is), szolgáltatásként elindítja, és ehhez a fiókhoz párosítja – jóváhagyni nem kell. Utána minden beállítás innen, a <strong>Beállítás</strong> gombbal megy; a kulcsokat a böngésződ titkosítja a futtató saját kulcsával.</p>
  <p class="muted">Mit csinál pontosan? <a href="#">A telepítő szövege</a> (érdemes elolvasni, mielőtt futtatod).</p>
</section>
""")


# ---- 2: the settings page -----------------------------------------------------------------------
VALUES = {"name": "Otthoni LXC", "assemblyai_key": "set", "cloud_delete_after": True, "whisper_builtin": False,
          "whisper_models": "large-v3, large-v3-turbo", "polite_mode": True, "polite_wait_min": "10", "local_llm": "",
          "llm_url": "http://127.0.0.1:4000", "llm_key": "set", "llm_reasoning": "auto",
          "llm_public_model": "osszefoglalo", "llm_private_model": "osszefoglalo-helyi",
          "allowed_domains": "youtube.com, youtu.be", "ytdlp_auto_update": True, "watch_dirs": "/mnt/felvetelek",
          "watch_mode": "local", "watch_summarize": True, "server": "https://dwyt.iodate.date", "lmstudio_token": ""}


def field(s):
    key, kind, label, help_ = s["key"], s["kind"], s["label"], s["help"]
    off = (not s["remote"]) or s["readonly"]
    v = VALUES.get(key, s["default"])
    if kind == "secret":
        if off:
            ctl = '<span class="muted">csak a futtató gépén</span>'
        else:
            state = '<span class="badge own">beállítva</span>' if v == "set" else '<span class="badge">nincs</span>'
            ctl = (f'<div class="secret">{state}<input type="password" placeholder="új kulcs" autocomplete="off">'
                   '<span class="lock">🔒 a böngésződ titkosítja a futtató kulcsával; a dwyt nem látja, kiolvasni nem lehet</span></div>')
    elif kind == "bool":
        ctl = f'<label class="choice"><input type="checkbox" {"checked" if v else ""} {"disabled" if off else ""}> be</label>'
    elif kind == "choice":
        opts = "".join(f'<option {"selected" if c["value"] == v else ""}>{c["label"]}</option>' for c in s["choices"])
        ctl = f'<select {"disabled" if off else ""}>{opts}</select>'
    else:
        ctl = f'<input type="text" value="{v if v not in (None, [], {}) else ""}" {"disabled" if off else ""}>'
    note = " · csak a futtató gépén állítható" if off and kind != "secret" else ""
    return (f'<div class="field{" off" if off else ""}"><span class="lbl">{label}</span><div>{ctl}</div>'
            f'<p class="help">{help_}{note}</p></div>')


groups = []
for g in schema["groups"]:
    g = dict(g, settings=[s for s in g["settings"] if s["remote"] and not s["readonly"] or s["key"] == "server"])
    basic = [s for s in g["settings"] if not s["advanced"]]
    adv = [s for s in g["settings"] if s["advanced"]]
    if not basic and not adv:
        continue
    inner = "".join(field(s) for s in basic)
    if adv:
        inner += (f'<details><summary class="muted">Haladó ({len(adv)})</summary>' + "".join(field(s) for s in adv)
                  + "</details>")
    groups.append(f'<section class="card"><h2>{g["title"]}</h2>{inner}</section>')

MODES = """<section class="card"><h2>Működési mód</h2>
<div class="modes">
 <label><strong>Felhő</strong><span class="muted">átírás AssemblyAI, összefoglaló felhőben</span></label>
 <label><strong>Vegyes</strong><span class="muted">átírás ezen a gépen, összefoglaló felhőben</span></label>
 <label><strong>Saját gép</strong><span class="muted">minden ezen a gépen</span></label>
 <label class="on"><strong>Egyéni</strong><span class="muted">GPU-gép (whisper_url) és saját LiteLLM – lent részletezve</span></label>
</div></section>"""

page("2-beallitas", f"""
<p class="muted"><a href="#">← Futtatók</a></p>
<h1>Otthoni LXC – beállítás</h1>
<div class="state"><span class="badge own">szinkronban</span><span class="muted">A futtató 07:31-kor jelentette a beállításait (dwyt-runner 0.9.9). A változást a következő jelentkezésekor veszi át, ez általában pár másodperc.</span></div>
{MODES}
{''.join(groups)}
<div class="savebar"><span class="muted">Csak a gazda állíthatja. Minden változás a naplóba kerül, és értesítés megy róla.</span><button>Mentés</button></div>
""")


# ---- 3: after saving: waiting for the runner, and the log ---------------------------------------
page("3-atadas-naplo", """
<p class="muted"><a href="#">← Futtatók</a></p>
<h1>Otthoni LXC – beállítás</h1>
<p class="warn-box"><span class="spin"></span> 2 változás vár átadásra: <strong>yt-dlp frissítése magától: ki</strong>, <strong>LLM-szerver kulcsa: új kulcs</strong>. A futtató a következő jelentkezésekor átveszi (pár másodperc); ha ki van kapcsolva a gép, bekapcsoláskor.</p>
<p class="notice">Átvette 07:33-kor. <span class="muted">A kulcsot a futtató kipróbálta: rendben.</span></p>
<p class="error">Nem vette át: <strong>Udvarias mód: leghosszabb várakozás</strong> – 0 és 120 között lehet. A többi változást átvette.</p>
<section class="card"><h2>Napló</h2>
<div class="table-wrap"><table class="log">
<thead><tr><th>Mikor</th><th>Ki</th><th>Mit</th><th>Eredmény</th></tr></thead>
<tbody>
<tr><td>2026-10-15 07:33</td><td>Zoltán</td><td>yt-dlp frissítése magától: be → ki<br>LLM-szerver kulcsa: új kulcs (a tartalma nem kerül a naplóba)</td><td><span class="badge own">átvette</span> <span class="muted">kulcspróba: rendben</span></td></tr>
<tr><td>2026-10-14 21:05</td><td>Zoltán</td><td>Udvarias mód: leghosszabb várakozás: 10 → 999</td><td><span class="badge warn">elutasítva</span> <span class="muted">0 és 120 között lehet</span></td></tr>
<tr><td>2026-10-14 20:58</td><td>a futtató gépén</td><td>Modell a nyilvános videókhoz: osszefoglalo → kerdes</td><td><span class="badge cloud">helyben állították</span></td></tr>
<tr><td>2026-10-14 09:10</td><td>Zoltán</td><td>Frissítés most: 0.9.8 → 0.9.9</td><td><span class="badge own">kész</span></td></tr>
</tbody></table></div>
<p class="muted">A naplóba a beállítás neve és a régi → új érték kerül; kulcsnál csak annyi, hogy megváltozott.</p>
</section>
""")
