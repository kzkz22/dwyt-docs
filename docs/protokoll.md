# A központ és a futtató közötti protokoll (vázlat)

Állapot: vázlat, 2026. október 10. A fő döntések a [terv](terv.md) 12. fejezetében és a döntésnapló 7.x soraiban vannak; ez a dokumentum a részleteket gyűjti, és a megvalósítás előtt véglegesítjük. A `dwyt-central` és a `dwyt-runner` ehhez a leíráshoz igazodik; ha változik, a protokoll verziószáma nő.

## Alapok

- **Szállítás:** HTTPS, JSON. A futtató kezdeményez minden kérést; a központ soha nem hívja a futtatót.
- **Azonosítás:** `Authorization: Bearer <futtatótoken>`. A token a párosításkor keletkezik, a központ csak a hash-ét tárolja, a felületen visszavonható.
- **Verzió:** minden kérésben `Dwyt-Protocol: <egész szám>` fejléc. A központ az aktuális és az előző verziót fogadja el; régebbire `426 Upgrade Required` és a felületen „frissítsd a futtatót” üzenet.
- **Útvonal-előtag:** `/runner/v1/…` (a verziószám az URL-ben a nagy, nem visszafelé kompatibilis váltásokhoz; a fejléc a kisebbekhez).

## Párosítás

1. A futtató első indításkor kér egy párosítókódot: `POST /runner/v1/pair/start` → `{"code": "K7Q-4M2", "poll_id": "...", "expires_in": 600}`.
2. A futtató kiírja a kódot; a felhasználó a központ felületén (Futtatók → Új futtató) beírja, és nevet ad a futtatónak.
3. A futtató közben kérdezi: `POST /runner/v1/pair/poll {"poll_id"}` → függőben `202`, jóváhagyás után `{"runner_id", "token"}`. A tokent a futtató helyben, csak a saját felhasználójának olvashatóan tárolja.

## Munkakérés (long-poll)

`POST /runner/v1/claim`, legfeljebb kb. 30 másodpercig nyitva:

```json
{
  "capabilities": {
    "kinds": ["transcribe", "translate", "summarize"],
    "transcribe_modes": ["captions", "cloud", "local"],
    "llm_models": ["osszefoglalo", "osszefoglalo-helyi"],
    "allowed_domains": ["youtube.com", "youtu.be"],
    "max_upload_bytes": 2147483648,
    "local_sources": true
  },
  "runner_version": "0.1.0",
  "busy": 0
}
```

Válasz: `204` (nincs munka; a futtató azonnal újra kér) vagy egy munka:

```json
{
  "job_id": "...",
  "kind": "transcribe",
  "lease_s": 900,
  "input": { "source": {"kind": "youtube", "video_id": "..."}, "options": {"mode": "local", "...": "..."} }
}
```

A központ csak a bejelentett képességeknek megfelelő munkát ad. Egy felhasználónak több futtatója lehet; egy munkát egyszerre egy futtató kap.

## Szívverés és megszakítás

`POST /runner/v1/jobs/{job_id}/heartbeat {"stage": "transcribe", "progress": {...}}`, legalább a lízing harmadánként. Válasz: `{"lease_s": 900, "cancel": false}`. `cancel: true` esetén a futtató leállítja a munkát, és `abandoned` állapottal zárja. Lejárt lízingnél a központ a munkát visszateszi a sorba.

## Bemeneti fájl a központon át

Ha a felhasználó a böngészőben töltött fel (méretkorláttal), a munka `input.source` mezője egy rövid életű letöltési címet ad: `GET /runner/v1/jobs/{job_id}/media` (Range-kérésekkel folytatható). A futtató sikeres letöltés után jelzi, és a központ törli az átmeneti fájlt.

## Eredmény leadása

`PUT /runner/v1/jobs/{job_id}/result` a munka fajtájának megfelelő JSON-nal (átirat: szegmensek, beszélők, nyelv, mód, modell, figyelmeztetések, költség; fordítás: szegmensenkénti szöveg; összefoglaló: Markdown, modell, tokenek). Ismételhető (idempotens): ugyanarra a munkára a második leadás nem hoz létre új eredményt.

Hiba: `POST /runner/v1/jobs/{job_id}/fail {"error": "...", "retry": "later" | "never" | "next_step"}`. A `next_step` a beállított láncolatban a következő lépést kéri (például nincs felirat → helyi Whisper).

## Helyi forrás (figyelt mappa)

A futtató maga is kezdeményezhet munkát a saját forrásából: `POST /runner/v1/local-items {"sha256", "name", "size", "options"}`. A központ létrehozza az elemet és a munkát (újrahasznosítás a hash alapján, a terv 7. fejezete szerint), és a munkát ugyanennek a futtatónak adja; a fájl el sem hagyja a felhasználó gépét.

## Nyitott részletek

- A munkák pontos bemeneti és kimeneti sémája (JSON Schema a `dwyt-docs`-ban).
- A long-poll időtúllépése az Apache `ProxyTimeout`-jához igazítva.
- Kéréskorlát futtatónként.
- Hogyan jelzi a futtató, hogy a GPU-gép épp ébred (várakozó állapot a felületen).
