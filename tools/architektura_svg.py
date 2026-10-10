P=dict(fill="#EEEDFE",stroke="#534AB7",t="#3C3489",s="#534AB7")
T=dict(fill="#E1F5EE",stroke="#0F6E56",t="#085041",s="#0F6E56")
C=dict(fill="#FAECE7",stroke="#993C1D",t="#712B13",s="#993C1D")
G=dict(fill="#F1EFE8",stroke="#888780",t="#2C2C2A",s="#5F5E5A")
W=dict(fill="#FFFFFF",stroke="#B4B2A9",t="#2C2C2A",s="#5F5E5A")
out=[]
def rect(x,y,w,h,c,rx=8,dash=False):
    d=' stroke-dasharray="4 3"' if dash else ''
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="0.8"{d}/>')
def text(x,y,s,c,bold=False,anchor="start",size=14,sub=False):
    col=c["s"] if sub else c["t"]
    w=' font-weight="600"' if bold else ''
    out.append(f'<text x="{x}" y="{y}" fill="{col}" font-size="{size}"{w} text-anchor="{anchor}" dominant-baseline="central">{s}</text>')
def box(x,y,w,h,title,sub,c=W):
    rect(x,y,w,h,c)
    text(x+w/2,y+16,title,c,bold=True,anchor="middle")
    text(x+w/2,y+35,sub,c,anchor="middle",size=12,sub=True)
def line(d): out.append(f'<path d="{d}" fill="none" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a)"/>')
rect(40,20,600,120,G,rx=18); text(60,40,"Központ (publikus) — dwyt-central",G,bold=True)
for i,(t,s) in enumerate([("Apache","TLS, proxy"),("Webes felület","könyvtár, MCP"),("PostgreSQL","átirat, vektor"),("bge-m3","keresés, CPU")]):
    box(50+i*148,64,136,56,t,s,P)
box(470,160,170,48,"Felhő, YouTube","saját kulccsal, saját IP")
rect(40,230,600,380,W,rx=18); text(624,252,"Felhasználó infrastruktúrája",W,bold=True,anchor="end")
for (x,w,c,t,s) in [(56,170,P,"1. Futtató","dwyt-runner"),(244,180,T,"2. AI-router","dwyt-airouter, mindig megy"),(442,182,C,"3. GPU-gép","dwyt-gpu, igény szerint")]:
    rect(x,270,w,320,c,rx=12); text(x+15,292,t,c,bold=True); text(x+15,310,s,c,size=12,sub=True)
rows=[326,386,446,506]
for r,(t,s) in zip(rows,[("Futtató","yt-dlp, ffmpeg"),("Kulcsok","helyben tárolva"),("Figyelt mappa","saját felvétel")]): box(71,r,140,48,t,s)
for r,(t,s) in zip(rows,[("LiteLLM","nevek, tartalék"),("llama-swap","GPU-sor, indítók, WOL"),("models.yaml","egy helyen a modellek")]): box(259,r,150,48,t,s)
for r,(t,s) in zip(rows,[("llama-server","LLM-modellek"),("Whisper","GPU-worker"),("NVMe-gyorsítótár","modellfájlok"),("NVIDIA GPU","VRAM, CUDA")]): box(457,r,152,48,t,s)
line("M71 350 L48 350 L48 144")
line("M200 326 L200 184 L466 184")
line("M211 346 L255 346")
line("M211 364 L235 364 L235 410 L255 410")
line("M334 374 L334 384")
line("M409 400 L433 400 L433 350 L453 350")
line("M409 416 L453 416")
out.append('<text x="40" y="628" fill="#5F5E5A" font-size="12" dominant-baseline="central">Lila: a központ és a futtató (kötelező). Zöld és korall: opcionális csomagok, egy gépre is tehetők.</text>')
out.append('<text x="40" y="646" fill="#5F5E5A" font-size="12" dominant-baseline="central">A futtató csak kifelé kapcsolódik a központhoz; a központ soha nem hívja a futtatót.</text>')
svg=('<svg xmlns="http://www.w3.org/2000/svg" width="680" height="666" viewBox="0 0 680 666" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
 '<title>dwyt architektúra</title>'
 '<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>'
 '<rect width="680" height="666" fill="#FFFFFF"/>'+"".join(out)+'</svg>')
open(__import__('pathlib').Path(__file__).resolve().parents[1]/'docs'/'architektura.svg','w').write(svg)
