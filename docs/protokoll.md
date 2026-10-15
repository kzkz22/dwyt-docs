# A központ és a futtató közötti protokoll

Állapot: 1-es verzió, 2026. október 10. (a 6. kör `ask` munkafajtája bővítés, a verziót nem emeli); a `dwyt-central` és a `dwyt-runner` 1. köre ezt valósítja meg. A fő döntések a [terv](terv.md) 12. fejezetében és a döntésnapló 7.x soraiban vannak. Ha a protokoll változik, a verziószáma nő, és a központ egy ideig az előzőt is elfogadja.

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
    "kinds": ["transcribe", "summarize", "translate", "ask"],
    "transcribe_modes": ["captions", "cloud", "local"],
    "llm_roles": ["public", "private"],
    "allowed_domains": ["youtube.com", "youtu.be"],
    "local_sources": false,
    "whisper_models": ["large-v3", "large-v3-turbo"],
    "source_kinds": ["upload", "local"],
    "llm_models": {"public": ["osszefoglalo", "cloud/okos"], "private": ["osszefoglalo-helyi"]},
    "llm_model_info": {"osszefoglalo": {"description": "Összefoglaló és fordítás.", "where": "local",
                                         "target_label": "Qwen3.6-35B-A3B, általános beállítás", "context": 262144,
                                         "vision": true, "thinking": false,
                                         "fallback": [{"name": "cloud/qwen3.8-flash-gyors", "target_label": "Qwen3.8 Flash",
                                                       "where": "cloud", "provider": "OpenRouter", "thinking": false}]}},
    "llm_server": "LiteLLM",
    "llm_defaults": {"summarize": "osszefoglalo", "translate": "osszefoglalo", "ask": "kerdes",
                     "private": "osszefoglalo-helyi"}
  },
  "runner_version": "0.1.0",
  "tool_versions": {"yt-dlp": "2026.8.19", "deno": "2.9.7"}
}
```

A futtató (0.11.1-től) a kérésben a `holding` listában megmondja, mely munkákon dolgozik még (egyszerre egy munkát végez, így munkakéréskor ez üres). Ha a központ szerint ennél a futtatónál fut egy munka, amely nincs a listában (a futtató a munka közben újraindult), a központ azonnal visszateszi a sorba, a már megszakítottat pedig lezárja; nem várja ki a lízing lejártát. A régebbi futtató nem küldi a mezőt, nála ez elmarad.

Ismeretlen fajtát vagy módot a központ nem utasít el (egy újabb futtató többet tudhat), csak nem ad rá munkát.

Válasz: `204` (nincs munka; a futtató azonnal újra kér) vagy `200`:

```json
{"job_id": 12, "kind": "transcribe", "lease_s": 900, "input": {"source": {...}, "options": {...}}}
```

- A központ csak a futtató felhasználójának munkáit adja, és csak olyat, ami a bejelentett képességeknek megfelel: fajta, átírási mód (helyi Whispernél a kért modellnek a `whisper_models` között kell lennie), összefoglalóhoz és fordításhoz a szerep (`public`: nyilvános forrás, `private`: saját felvétel), és ha a munkán választott modell van (`model`), annak a futtató `llm_models` listájában kell lennie az adott szerepnél; URL-es munkánál az engedélyezett tartományok (pontos gépnév vagy aldomain; `*` = bármi).
- A futtató a kapott munkát maga is ellenőrzi (fajta, forrás, mód, tartomány), és ami nem fér bele, azt hibával visszaadja. A központ esetleges feltörése így sem tud a futtatóval mást csináltatni, mint ezeket a szűk munkákat.
- A bejelentett képességeket és verziókat a felület a Futtatók oldalon mutatja. Ha egy várakozó munkát egyik futtató sem tud elvégezni, a Munkák oldal ezt jelzi.
- Új, ismeretlen képességmezőt a központ figyelmen kívül hagy; így a futtató a protokoll verziójának emelése nélkül bővíthet.
- A munka bemenete: [transcribe-input](../schemas/transcribe-input.schema.json), [summarize-input](../schemas/summarize-input.schema.json), [translate-input](../schemas/translate-input.schema.json), [ask-input](../schemas/ask-input.schema.json).
- **Fordítás** (`translate`, a 3. körtől): az átirat szegmensei sorszámmal; a futtató a sorszámokat megtartva adja vissza a magyar sorokat ([translate-result](../schemas/translate-result.schema.json)), a ki nem fordított sorokat kihagyja, és a számukat a `missing` mezőben jelzi. A modellt a szerep szerint maga választja (`private` → `llm_private_model`; `public` → `llm_translate_model`, ha van, különben `llm_public_model`).
- **Választott modell** (3c): az `llm_models` képesség szerepenként sorolja fel, mely modelleket ajánlja fel a futtató a felhasználónak (az alapmodellek és az `llm_models`, illetve saját felvételhez az `llm_private_models` beállítás). Az elemoldalon választott modell a munka bemenetében `model` mezőként érkezik; a futtató csak a saját listájából fogad el modellt, mást végleges hibával (`never`) visszaad. `model` nélkül a szerep szerinti alapmodell dolgozik. Az összefoglaló utasítását a futtató írja; a verziószámát (`prompt_version`) az eredménnyel együtt visszaküldi.

- **Modell-leírás** (17.4): az `llm_model_info` nevenként mondja meg, mi fut a név mögött: `description` (mire való), `where` (`local` / `cloud`), `target` és `target_label` (a modell), `provider`, `context` (token), `vision`, `thinking` (`true` / `false`; hiányzik = a modell alapértelmezése), `thinking_budget`, és `fallback` (legfeljebb 3 tartalék ugyanilyen mezőkkel és a `name`-mel: mi válaszol, ha a GPU-gép ki van kapcsolva). Az `llm_server` az LLM-szerver fajtája (`LiteLLM`, `OpenRouter`, `OpenAI-kompatibilis szerver`), az `llm_defaults` feladatonként (`summarize`, `translate`, `ask`, `private`) az alapmodell neve. A dwyt-airouter LiteLLM-je a `/model/info` válaszában `model_info.dwyt` alatt adja ezeket; a futtató csak a felsorolt mezőket küldi tovább (kulcsot, címet soha), és óránként frissíti. A központ is csak ezeket a mezőket tárolja (legfeljebb 40 név, 40 000 karakter); ha a mezők hiányoznak, régebbi futtatónak tekinti. Mindhárom csak tájékoztatás: azt, hogy mi kérhető, továbbra is az `llm_models` dönti el.

- **Felirat használata** (18.9): a felirat-munkánál a futtató a megtalált sávot küldi (`caption_kind`: `manual` vagy `auto`), ahogy eddig. A központ dönti el a felhasználó szabálya szerint, hogy megtartja-e: ha nem, az eredményt nem tárolja, a válasz `{"rejected": "…"}`, és a munka a feliratkozási láncban továbblép, kézi beküldésnél hibával zárul. A futtatón ehhez nincs teendő.

- **Megosztott futtató** (17.5): a központ a futtató gazdájának munkái mellett azoknak a felhasználóknak a munkáit is adhatja, akikkel a gazda megosztotta, és akik elfogadták; csak a megosztás szerinti képességekkel és havi kereten belül. A futtató számára ez nem változás: a munka ugyanolyan. Ha a kérőnek nincs felhős nyelvi kerete, a nyilvános forrás munkája is `role: "private"`-tal érkezik, vagyis a futtató helyi modelljével készül; a választott `model` ilyenkor csak a `private` listából lehet. A felhasznált keretet a központ az eredményből számolja (`transcript.cloud.audio_seconds`; nyelvi munkánál a `model_used`, összevetve a modell-leírás felhős tartalékával).

- **Kérdés** (`ask`, a 6. körtől): egy beszélgetés következő válasza ([ask-input](../schemas/ask-input.schema.json) → [ask-result](../schemas/ask-result.schema.json)). A bemenetben a `scope` (`item`: egy elem; `library`: a könyvtár), a `role` (`public`, saját felvétel oldalán `private`), a háttér forrásai sorszámmal (`sources`: cím, csatorna, nyelv, az összefoglaló, az átirat sorai időponttal és a magyar fordítással; `partial: true`, ha csak részletek), és az eddigi üzenetek (`messages`, az utolsó a megválaszolandó kérdés). Könyvtár-kérdésnél (17.6) a bemenetben a teljes könyvtár rövid listája is ott van (`catalog`: sorszám, cím, csatorna, dátum, címkék, az összefoglaló eleje; a `sources`-ban szereplő videó ugyanazzal a sorszámmal) és a videók száma (`library_total`); a `sources` ilyenkor üres is lehet. A futtató az utasításban megmondja a modellnek, hogy a lista teljes, a részletek pedig csak a legjobb találatok. A futtató írja az utasítást (a hivatkozás alakja: elemnél `[12:34]`, könyvtárnál `[#2 12:34]`), a modell a szerep szerinti: `public` → `llm_ask_model`, ha van, különben `llm_public_model`; `private` → `llm_private_model`; a választott `model` itt is csak a futtató listájából. A futtató a `kinds`-ban `ask`-kal jelzi, hogy tud ilyet; a régebbi futtató nem kap kérdést.

## Szívverés és megszakítás

`POST /runner/v1/jobs/{job_id}/heartbeat {"stage": "captions", "progress": {...}}` legalább a lízing harmadánként (a futtató 30 másodpercenként, és minden új lépésnél azonnal küldi). Minden futtatói kérés, a szívverés is, frissíti a futtató „utoljára jelentkezett” idejét, így egy hosszú munka közben is elérhetőnek látszik. Válasz: `{"lease_s": 900, "cancel": false}`.

A `progress` hosszú LLM-munkáknál (3c): `{"part": 3, "parts": 12, "model": "forditas"}` (fordításnál a köteg, darabolt összefoglalónál a lépés sorszáma); a felület az elemoldalon és a Munkák oldalon mutatja. Legfeljebb 5 másodpercenként küldi.

- `cancel: true`: a felhasználó megszakította; a futtató a következő lépésnél abbahagyja, és `fail`-lel zárja (a központ megszakítottnak jelöli). A nyelvi modell válaszát a futtató folyamként (stream) kéri, így egy összefoglaló, fordítás vagy kérdés a válasz következő darabjánál áll le; ha a szerver 3 percig (helyi modellszervernél 10 percig) egy bájtot sem küld, a kapcsolatot halottnak tekinti, és a munkát `later`-rel adja vissza.
- `404`/`409`: a munka már nem ezé a futtatóé (törölték, vagy lejárt a lízing, és más kapta meg); a futtató abbahagyja, és nem ad le eredményt.
- Lejárt lízing (a futtató eltűnt): a munka visszakerül a sorba; a próbálkozások száma nő, és a 6. után a munka hibával áll le.
- A lépések nevei (`download`, `captions`, `prepare-audio`, `upload`, `transcribe`, `summarize`, `write`; helyi Whispernél még `waiting-for-gpu`, `load-audio`, `align`, `diarize`) a felületen magyarul látszanak.

## Eredmény leadása

`PUT /runner/v1/jobs/{job_id}/result`, a munka fajtájától függően: [transcribe-result](../schemas/transcribe-result.schema.json), [summarize-result](../schemas/summarize-result.schema.json), [translate-result](../schemas/translate-result.schema.json) vagy [ask-result](../schemas/ask-result.schema.json).

- Ismételhető: ha a futtató nem kapott választ, újra leadhatja; a központ a már tárolt eredményt nem tárolja kétszer, és ugyanazt a választ adja.
- Érvénytelen alakra `422` (például üres szegmenslista); a futtató ezt hibaként naplózza.
- A futtató a leadást átmeneti hibánál (hálózat, `5xx`) egyre ritkábban, kb. 20 percig próbálja.
- Átírás után, ha a beküldő kérte, a központ magától sorba teszi az összefoglalót; ha az átirat nem magyar, és a felhasználó nem kapcsolta ki, a fordítást is.

## Hiba

`POST /runner/v1/jobs/{job_id}/fail {"error": "...", "retry": "later" | "never" | "next_step"}`

- `later`: átmeneti (YouTube-tiltás, élő adás, elérhetetlen szolgáltató); a központ 1, 5, 15, 60, 180, 360 perc múlva újra kiadja, legfeljebb 6 próbálkozásig.
- `never`: végleges (nincs kulcs, rossz modellnév, nem engedélyezett tartomány); a munka hibával áll le, a felületen „Újra” gombbal újraindítható.
- `next_step`: ez a mód ennél a forrásnál nem működik (például nincs felirat a videó nyelvén). A feliratkozásos videók láncolatában a következő mód jön (terv, 14. fejezet); kézi beküldésnél végleges, mint a `never`.
- A hibaüzenet magyarul, a felhasználónak szól; kulcsot vagy belső részletet nem tartalmazhat.

## Helyi Whisper (a futtató és a GPU-worker között)

Ez nem a központ protokollja, hanem a futtató és a felhasználó saját GPU-workere közötti kapcsolat (dwyt-airouter, dwyt-gpu); a központ csak a `local` módot és a `whisper_models` képességet látja.

- `POST {whisper_url}/transcribe?model=large-v3&language=hu&diarize=true&num_speakers=2`, a törzs a 16 kHz-es mono FLAC. A `whisper_url` a llama-swap upstream-címe, például `http://AI-ROUTER:8080/upstream/whisper`.
- Az egész munka EGY kérés: amíg nyitva van, a llama-swap a GPU-t a workernél tartja, és az LLM-kéréseket mögé sorolja. A válasz NDJSON: `{"stage": ...}` legalább 10 másodpercenként, a végén `{"result": {...}}` vagy `{"error": "..."}`. A kapcsolat bontása leállítja a munkát a workeren, és felszabadítja a GPU-t.
- A futtató hibakezelése: elérhetetlen worker, a llama-swap `502`/`503`/`504`-e vagy félbeszakadt folyam → `retry: later` (megvárja a GPU-gépet); a worker elutasítása (`4xx`) vagy hibasora → `never`. Másik módra soha nem vált.

## Saját felvételek (a 3. körtől)

- **Böngészős feltöltés:** a központ a fájlt a futtató letöltéséig tárolja. A munka forrása `{"kind": "upload", "sha256", "name", "size", "media": "/runner/v1/jobs/{job_id}/media"}`; a futtató a `GET …/media` címről tölti le (a saját tokenjével, csak a nála futó munkáét; `Range`-kéréssel folytatható), és az átírás előtt ellenőrzi a SHA-256-ot. A fájlt a központ az eredmény leadása után törli (legkésőbb 7 nap múlva).
- **Figyelt mappa:** a futtató az új fájlt bejelenti: `POST /runner/v1/local-items {"sha256", "name", "size", "options", "summarize"}` ([local-item-request](../schemas/local-item-request.schema.json)). Válasz: `{"item_id", "job_id", "existing"}`; `existing: true`, ha ennek a fájlnak már van átirata (nincs új munka). A munka forrása `{"kind": "local", "sha256", "name", "size"}`, és csak az a futtató kapja meg, amelyik bejelentette; a fájl nem hagyja el a gépet.
- Mindkettőhöz a futtató a `source_kinds` képességben jelenti, mit tud (`upload`; figyelt mappával `local` is). A saját felvétel eredménye nem osztható meg, az összefoglaló és a fordítás `private` szereppel kérődik.

## Telepítés egy paranccsal (7d)

A dwyt Futtatók oldalán a gazda kér egy **telepítőkódot**. Ez 5 percig él, egyszer használható, és a parancsban van: `curl -fsSL https://KÖZPONT/futtato.sh | sh -s -- KÓD`. A `/futtato.sh` a központ címével kitöltött telepítő szkript (a szövege bárki által olvasható, kód és titok nincs benne).

- `POST /runner/v1/pair/redeem {"code", "name"}` (token nélkül; ugyanaz a kéréskorlát, mint a `pair/start`-nál) → `200 {"runner_id", "name", "token"}`. Lejárt, felhasznált vagy ismeretlen kódra `410`. Jóváhagyni nem kell: a kód maga a jóváhagyás, ezért csak 5 percig él.
- A szkript a kódot **legelőször** váltja be, még a letöltések előtt: `?format=env` esetén a válasz szöveges (`DWYT_RUNNER_ID=…`, `DWYT_TOKEN=…`), mert egy puszta `sh` nem olvas JSON-t. A tokent a szkript csak a tulajdonosa által olvasható ideiglenes fájlban tartja, és a `dwyt-runner adopt` parancsnak környezeti változóban adja át (parancssori argumentumban látszana a folyamatlistában).

## Távoli beállítás (7d)

Szerver-telepítésnél a futtató beállításai a dwyt Futtatók → Beállítás oldaláról állíthatók (terv 15b, 18.11). A központ itt is csak tárol és továbbít: a futtató kérdez, és ő dönt minden értékről.

**Bekapcsolás.** A futtató `remote_settings` beállítása `auto` | `on` | `off`; `auto` a parancssoros (`run`) futtatónál be, az asztali alkalmazásnál ki. Ez a beállítás a dwyt-ből nem állítható. Kikapcsolva a futtató csak a változatát és a telepítés fajtáját jelenti, a beállításait nem.

**Jelentés.** `PUT /runner/v1/settings`, induláskor, minden (helyi vagy távoli) változás után, és óránként:

```json
{
  "runner_version": "0.10.0", "latest_version": "0.10.1", "install": "service",
  "remote": true,
  "public_key": "-----BEGIN PUBLIC KEY-----\n…",
  "describe": {"groups": [...]},
  "modes": [{"id": "felho", "title": "Felhő", "text": "…", "values": {"whisper_builtin": "nem", ...}}],
  "mode": "egyeni",
  "values": {"name": "Otthoni LXC", "polite_wait_min": "10", "allowed_domains": "youtube.com, youtu.be", ...},
  "secrets_set": ["assemblyai_key", "llm_key"]
}
```

- `install`: `service` (a `run` parancs, például systemd alatt), vagy `app` (asztali alkalmazás). A „Frissítés most” csak a `service`-nek ajánlható fel.
- `latest_version`: a legújabb változat, amit a futtató naponta egyszer a forrásából kiolvas. Üres, ha nem tudja.
- `describe`: a beállítások leírása, ugyanaz, mint a `dwyt-runner config describe --json` ([runner-settings](../schemas/runner-settings.json)). A központ ebből rajzolja a Beállítás oldalt, így egy újabb futtató új mezői a központ módosítása nélkül megjelennek.
- `values`: minden nem titkos beállítás **szövegként**, abban az alakban, ahogy a `config set` is elfogadja (lista: vesszővel, térkép: `név=leírás; …`, igen/nem). Titkos értéket a futtató soha nem küld; a `secrets_set` csak azt mondja meg, melyik kulcs van megadva.
- `public_key`: a futtató saját RSA-kulcsának nyilvános fele (3072 bit, PEM). A titkos fele a futtató beállítási mappájában van, csak a tulajdonosa olvashatja.
- `remote: false` esetén a `describe`, `modes`, `values`, `secrets_set` és `public_key` hiányzik; a központ ilyenkor a korábban tárolt értékeket is törli.
- Ha a korábban jelentett értékekhez képest valami a futtató gépén változott, a központ ezt „a futtató gépén” bejegyzésként naplózza (kulcsnál csak azt, hogy megadták vagy törölték).
- Válasz: `{"pending": 0}`, vagyis ennyi változás vár átadásra.

**Változás.** A gazda a Beállítás oldalon menti a változásokat. A böngésző a kulcsokat a futtató nyilvános kulcsával titkosítja (RSA-OAEP, SHA-256, WebCrypto), így a kulcs nyílt szövegként el sem jut a központhoz. Egy mentés egy változás: értékek szövegként, titkosított kulcsok, vagy egy művelet.

- A munkakérés (`claim`) válaszában a `Dwyt-Settings: pending` fejléc jelzi, hogy változás vár. Ha nincs munka, a központ ilyenkor nem tartja nyitva a long-pollt, hanem azonnal `204`-et ad.
- `GET /runner/v1/settings/changes` → `{"changes": [{"id": 7, "values": {"polite_wait_min": "15"}, "secrets": {"llm_key": "<base64>"}, "clear": ["assemblyai_key"], "action": null}]}`. A kiadott változást a központ „átadva” állapotúra teszi, és többé nem jelzi. Ha 10 percen belül nincs eredmény, „nem jelzett vissza” hibával zárja.
- `action`: `null` vagy `"update"` (Frissítés most).
- A futtató minden értéket a saját leírása szerint ellenőriz (ugyanaz, mint a `config set`). Csak a dwyt-ből állítható (`remote: true`, nem `readonly`) mezőket fogadja el, a többit elutasítja. A kulcsot a saját titkos kulcsával fejti meg, elmenti, majd egy próbahívással kipróbálja (AssemblyAI, LLM).
- `POST /runner/v1/settings/changes/{id}/result {"applied": [...], "errors": {"kulcs": "magyar ok"}, "checks": {"llm_key": [true, "rendben"]}, "message": "…"}`. A központ ezután törli a változás titkosított kulcsait, és elkészül a napló bejegyzése és az értesítés. Utána a futtató új jelentést küld.
- **Frissítés most** (`action: "update"`): a futtató csak `service` telepítésnél és munka nélkül hajtja végre. Ilyenkor ugyanazt a `uv tool install --force --refresh …` parancsot futtatja, mint a kézi frissítés (a meglévő kiegészítőkkel). Siker után leadja az eredményt, és újraindul: systemd alatt kilép (75-ös kóddal, amire a szolgáltatás újraindítja), máskülönben önmagát indítja újra. Aláírás-ellenőrzés még nincs (terv 18.16, a 7c-vel jön).

## Később

- Kéréskorlát futtatónként; a GPU-gép ébredésének jelzése a felületen.
- A kérdés válaszának folyamatos küldése (streaming) a szívverésekben (`progress.partial`).
