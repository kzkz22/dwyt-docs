# A központ és a futtató közötti protokoll

Állapot: 1-es verzió, 2026. október 10.; a `dwyt-central` és a `dwyt-runner` 1. köre ezt valósítja meg. A fő döntések a [terv](terv.md) 12. fejezetében és a döntésnapló 7.x soraiban vannak. Ha a protokoll változik, a verziószáma nő, és a központ egy ideig az előzőt is elfogadja.

A kérések és válaszok pontos alakja JSON Schema-ként: [schemas/](../schemas/). A futtatótól érkező alakokat (`*-request`, `*-result`) a `dwyt-central/central/protocol.py` modelljeiből generáljuk; ha ott változik valami, a sémát is újra kell generálni.

## Alapok

- **Szállítás:** HTTPS, JSON. Minden kérést a futtató kezdeményez; a központ soha nem hívja a futtatót.
- **Verzió:** minden kérésben `Dwyt-Protocol: 1`. Ismeretlen vagy hiányzó verzióra `426` és egy magyar üzenet („frissítsd”); a futtató ilyenkor kiírja, és leáll.
- **Azonosítás:** a párosítás után `Authorization: Bearer <futtatótoken>`. A központ csak a token hash-ét tárolja; a felület Futtatók oldalán visszavonható. Érvénytelen vagy visszavont tokenre `401`; a futtató ilyenkor újrapárosítást kér, és leáll. Ugyanez történik, ha a felhasználót letiltották.
- **Útvonalak:** `/runner/v1/...`.

## Párosítás

1. `POST /runner/v1/pair/start` (token nélkül) → `{"code": "K7Q-4M2", "poll_id": "...", "expires_in": 600}`. A kód 6 karakter egy félreérthető betűk nélküli ábécéből (`ABCDEFGHJKLMNPQRSTUVWXYZ23456789`).
2. A futtató kiírja a kódot; a felhasználó a központ **Futtatók** oldalán beírja, és nevet ad a futtatónak. A kód kis- és nagybetűvel, kötőjellel vagy anélkül is elfogadott; tíz hibás próbálkozás után a felület 10 percig nem fogad kódot.
3. A futtató 3 másodpercenként kérdez: `POST /runner/v1/pair/poll {"poll_id"}` →
   - `202` amíg nincs jóváhagyva;
   - `200 {"runner_id", "name", "token"}` a jóváhagyás után (a token itt, a lekérdezéskor keletkezik, és csak egyszer adódik ki; a párosítási kérés törlődik);
   - `410`, ha lejárt.

## Munkakérés

`POST /runner/v1/claim`, legfeljebb kb. 25 másodpercig nyitva (long-poll):

```json
{
  "capabilities": {
    "kinds": ["transcribe", "summarize"],
    "transcribe_modes": ["captions", "cloud", "local"],
    "llm_roles": ["public", "private"],
    "allowed_domains": ["youtube.com", "youtu.be"],
    "local_sources": false,
    "whisper_models": ["large-v3", "large-v3-turbo"]
  },
  "runner_version": "0.1.0",
  "tool_versions": {"yt-dlp": "2026.8.19", "deno": "2.9.7"}
}
```

Válasz: `204` (nincs munka; a futtató azonnal újra kér) vagy `200`:

```json
{"job_id": 12, "kind": "transcribe", "lease_s": 900, "input": {"source": {...}, "options": {...}}}
```

- A központ csak a futtató felhasználójának munkáit adja, és csak olyat, ami a bejelentett képességeknek megfelel: fajta, átírási mód (helyi Whispernél a kért modellnek a `whisper_models` között kell lennie), összefoglalóhoz a szerep (`public`: nyilvános forrás, `private`: saját felvétel), URL-es munkánál az engedélyezett tartományok (pontos gépnév vagy aldomain; `*` = bármi).
- A futtató a kapott munkát maga is ellenőrzi (fajta, forrás, mód, tartomány), és ami nem fér bele, azt hibával visszaadja. A központ esetleges feltörése így sem tud a futtatóval mást csináltatni, mint ezeket a szűk munkákat.
- A bejelentett képességeket és verziókat a felület a Futtatók oldalon mutatja. Ha egy várakozó munkát egyik futtató sem tud elvégezni, a Munkák oldal ezt jelzi.
- Új, ismeretlen képességmezőt a központ figyelmen kívül hagy; így a futtató a protokoll verziójának emelése nélkül bővíthet.
- A munka bemenete: [transcribe-input](../schemas/transcribe-input.schema.json), [summarize-input](../schemas/summarize-input.schema.json). Az összefoglaló utasítását a futtató írja; a verziószámát (`prompt_version`) az eredménnyel együtt visszaküldi.

## Szívverés és megszakítás

`POST /runner/v1/jobs/{job_id}/heartbeat {"stage": "captions", "progress": {...}}` legalább a lízing harmadánként (a futtató 60 másodpercenként, és minden új lépésnél azonnal küldi). Válasz: `{"lease_s": 900, "cancel": false}`.

- `cancel: true`: a felhasználó megszakította; a futtató a következő lépésnél abbahagyja, és `fail`-lel zárja (a központ megszakítottnak jelöli).
- `404`/`409`: a munka már nem ezé a futtatóé (törölték, vagy lejárt a lízing, és más kapta meg); a futtató abbahagyja, és nem ad le eredményt.
- Lejárt lízing (a futtató eltűnt): a munka visszakerül a sorba; a próbálkozások száma nő, és a 6. után a munka hibával áll le.
- A lépések nevei (`download`, `captions`, `prepare-audio`, `upload`, `transcribe`, `summarize`, `write`; helyi Whispernél még `waiting-for-gpu`, `load-audio`, `align`, `diarize`) a felületen magyarul látszanak.

## Eredmény leadása

`PUT /runner/v1/jobs/{job_id}/result`, a munka fajtájától függően: [transcribe-result](../schemas/transcribe-result.schema.json) vagy [summarize-result](../schemas/summarize-result.schema.json).

- Ismételhető: ha a futtató nem kapott választ, újra leadhatja; a központ a már tárolt eredményt nem tárolja kétszer, és ugyanazt a választ adja.
- Érvénytelen alakra `422` (például üres szegmenslista); a futtató ezt hibaként naplózza.
- A futtató a leadást átmeneti hibánál (hálózat, `5xx`) egyre ritkábban, kb. 20 percig próbálja.
- Átírás után, ha a beküldő kérte, a központ magától sorba teszi az összefoglalót.

## Hiba

`POST /runner/v1/jobs/{job_id}/fail {"error": "...", "retry": "later" | "never" | "next_step"}`

- `later`: átmeneti (YouTube-tiltás, élő adás, elérhetetlen szolgáltató); a központ 1, 5, 15, 60, 180, 360 perc múlva újra kiadja, legfeljebb 6 próbálkozásig.
- `never`: végleges (nincs kulcs, rossz modellnév, nem engedélyezett tartomány); a munka hibával áll le, a felületen „Újra” gombbal újraindítható.
- `next_step`: ez a mód ennél a forrásnál nem működik (például nincs felirat a videó nyelvén); a feliratkozások láncolatában (4. kör) a következő mód jön, addig a központ `never`-ként kezeli.
- A hibaüzenet magyarul, a felhasználónak szól; kulcsot vagy belső részletet nem tartalmazhat.

## Helyi Whisper (a futtató és a GPU-worker között)

Ez nem a központ protokollja, hanem a futtató és a felhasználó saját GPU-workere közötti kapcsolat (dwyt-airouter, dwyt-gpu); a központ csak a `local` módot és a `whisper_models` képességet látja.

- `POST {whisper_url}/transcribe?model=large-v3&language=hu&diarize=true&num_speakers=2`, a törzs a 16 kHz-es mono FLAC. A `whisper_url` a llama-swap upstream-címe, például `http://AI-ROUTER:8080/upstream/whisper`.
- Az egész munka EGY kérés: amíg nyitva van, a llama-swap a GPU-t a workernél tartja, és az LLM-kéréseket mögé sorolja. A válasz NDJSON: `{"stage": ...}` legalább 10 másodpercenként, a végén `{"result": {...}}` vagy `{"error": "..."}`. A kapcsolat bontása leállítja a munkát a workeren, és felszabadítja a GPU-t.
- A futtató hibakezelése: elérhetetlen worker, a llama-swap `502`/`503`/`504`-e vagy félbeszakadt folyam → `retry: later` (megvárja a GPU-gépet); a worker elutasítása (`4xx`) vagy hibasora → `never`. Másik módra soha nem vált.

## Később

- **Bemeneti fájl a központon át** (3. kör): böngészős feltöltésnél a munka egy rövid életű letöltési címet kap (`GET /runner/v1/jobs/{job_id}/media`, Range-kérésekkel).
- **Helyi forrás** (3. kör): a futtató a figyelt mappából maga kezdeményez munkát: `POST /runner/v1/local-items {"sha256", "name", "size", "options"}`; a fájl el sem hagyja a gépet.
- Kéréskorlát futtatónként; a GPU-gép ébredésének jelzése a felületen.
