# dwyt – funkcionális terv

Állapot: 2026. október 10. Az 1. kör elkészült és élesben fut (`dwyt-central`, `dwyt-runner`); a 2. kör (saját GPU: `dwyt-airouter`, `dwyt-gpu`, helyi Whisper a futtatóban) is elkészült és élesben működik (Unraid-indítóval, 2026. október 11.). Ez a dokumentum rögzíti a megbeszélt döntéseket; minden későbbi lépés erre hivatkozik, és ha egy döntés változik, itt kell átírni (a fejezetben és a 21. fejezet döntésnaplójában is).

## 1. Cél

Videók és hangfelvételek átirata (időbélyeggel, beszélőkkel), magyar fordítása és magyar összefoglalója, felhasználónként külön, kereshető könyvtárban, a YouTube-feliratkozások háttérfeldolgozásával. Interneten elérhető szolgáltatás, amelyet bárki telepíthet, és amelyre meghívással (vagy a telepítő döntése szerint nyitottan) lehet regisztrálni.

Alapelvek:

- **A pénzbe kerülő, titkos és a médiához nyúló munka a felhasználónál fut**, a saját futtatóján (8. fejezet). A központ irányít és tárol, nem számol.
- **Mindenkinek külön könyvtára van**, a felhasználók nem látnak át egymáshoz. Ugyanazon a forráson végzett munka (átirat, fordítás, összefoglaló) a szabályok szerint újrahasznosítható (7. fejezet).
- **Felhős szolgáltatás csak a felhasználó saját kulcsával** (AssemblyAI, OpenRouter vagy más), a költség az övé.
- **Saját helyi AI** (GPU, helyi LLM) bekapcsolható, másik hálózatban is (9–10. fejezet).
- **Nincs csendes átváltás** az átírási módok között; ami láncolat (felirat → helyi → felhő), az kifejezett, beállított szabály.

## 2. Viszony a régi rendszerhez

A régi rendszer (`yt-transcribe` és `yt-transcribe-webui`) változatlanul megmarad és fut tovább; a dwyt külön repókban, külön életet él. Ha a dwyt már jól működik, akkor dől el, kell-e még a régi.

Amit a dwyt a régiből átvesz (kódban és tapasztalatban):

- a yt-transcribe API letöltés-, ffmpeg-, felirat- és felhős kódja → a futtatóba;
- a GPU-worker (WhisperX, wav2vec2, pyannote) → a GPU-gép csomagjába;
- a llama-swap + LiteLLM felállás és az Unraid-indító → az AI-router csomagjába;
- a webui könyvtára, keresése (PostgreSQL, `pgvector`, `bge-m3`), összefoglaló- és fordításlogikája, postaládája, MCP-je → a központba, többfelhasználóssá alakítva.

A régi könyvtár tartalma később egyszeri behozatallal kerülhet át a tulajdonos fiókjába (18. fejezet); a dwyt üresen indul.

## 3. Repók és telepítési egységek

| Repó | Mi | Hol fut | Licenc |
| --- | --- | --- | --- |
| `dwyt-docs` | Ez a terv, az architektúra, a döntésnapló és a központ–futtató protokoll | – | MIT |
| `dwyt-central` | Központ: webes felület, belépés, könyvtár, keresés, postaláda, munkasor, MCP | Egy publikus szerver (a tulajdonosnál: Proxmox LXC) | AGPL-3.0 |
| `dwyt-runner` | Futtató: letöltés, felirat, felhős átírás, LLM-hívások, figyelt mappa | A felhasználó gépe vagy VPS-e; Linux, Windows, macOS | MIT |
| `dwyt-airouter` | AI-router: LiteLLM + llama-swap, indítók, ébresztés, `models.yaml` | Mindig bekapcsolt gép a felhasználónál | MIT |
| `dwyt-gpu` | GPU-gép: llama-server, Whisper GPU-worker, modellek letöltése | NVIDIA GPU-s gép, igény szerint bekapcsolva | MIT |

Telepítéskor a felhasználónak a futtató kötelező, az AI-router és a GPU-gép opcionális. A három csomag egy gépre is tehető, de mindegyik külön telepítés.

A tulajdonos saját felállása: központ a Proxmoxon (publikus, Apache mögött), futtató és AI-router az `ai-router` LXC-ben, GPU-gép az Unraidon (Unraid-indítóval).

## 4. Architektúra

![Architektúra](architektura.png)

Forrás: [architektura.svg](architektura.svg).

Adatfolyamok:

1. A **futtató kapcsolódik ki** a központhoz HTTPS-en: munkát kér, eredményt ad le. A központ soha nem hívja a futtatót; a futtatónak nem kell nyitott port, VPN vagy NAT-beállítás.
2. A futtató a **felhőt** (felhős átírás, felhős LLM) a felhasználó saját kulcsával hívja, a **YouTube-ot** a saját IP-címéről éri el.
3. A futtató a **helyi AI-t** két címen éri el: az „LLM-cím” (LiteLLM vagy bármely OpenAI-kompatibilis szerver) és a „Whisper-cím” (a llama-swap felől a GPU-worker). Neki mindegy, mi van mögöttük.
4. Az **AI-router** llama-swapja egyedül birtokolja a GPU-t: indítja és leállítja a GPU-gép konténereit, és sorba állítja a kéréseket. A felhasználó többi kliense (OpenCode, Hermes, Open WebUI) is a LiteLLM-re mutat, így náluk sem okoz gondot, ha a GPU épp Whispert futtat.
5. A **keresés** a központban fut (a kérdést is vektorrá kell alakítani, és a futtató kikapcsolt állapotában is működnie kell).

## 5. Felhasználók, belépés, jogosultságok

- **Regisztrációs mód** telepítéskor: nyitott / meghívásos / zárt. A tulajdonos példánya meghívásos.
- **Meghívás:** az admin felvesz egy e-mail-címet; a rendszer egyszer használható, 7 napig érvényes meghívólinket készít, és e-mailben elküldi (ha a telepítő adott SMTP-szervert), különben az admin másolja ki és küldi el. Belépni csak az a Google-fiók tud, amelynek ellenőrzött e-mail-címe egyezik a meghívóval.
- **Belépés Google-lel** (OpenID Connect, „Web application” típusú OAuth-kliens, a nyilvános HTTPS-címre visszairányítva). A fiókot a Google állandó azonosítója (`sub`) köti, nem az e-mail-cím.
- **Második faktor:** a Google-fiók adja; telepítési beállítással kötelezővé tehető egy saját TOTP is a Google-belépés után.
- **Admin tartalékbelépés:** jelszó + TOTP, csak az admin fióknak, Google-kiesés vagy fióktiltás esetére.
- **Google-fiók nélküli felhasználó** az első körben nem lehet; a következő körben meghívólinkkel passkey-t regisztrálhat. További belépési szolgáltatók (Microsoft, GitHub) később.
- **Szerepek:**
  - *admin:* meghív, letilt, töröl; látja a fiókok adatait, a tárhely- és munkastatisztikát, a futtatók állapotát. **Nem látja** a felhasználók könyvtárát (átiratok, összefoglalók, keresések); a felületen erre nincs út, és ezt az adatvédelmi tájékoztató is így írja.
  - *felhasználó:* a saját könyvtára, futtatói, tokenjei, csatornái.
- **Fióktörlés** a felhasználó által: mindent töröl (könyvtár, tokenek, csatornák, futtatók). A másik felhasználónak már átadott (újrahasznosított) eredmény nála megmarad.
- **YouTube-feliratkozások:** ugyanaz a Web OAuth-kliens, de a `youtube.readonly` engedélyt csak akkor kéri, amikor a felhasználó bekapcsolja a feliratkozásokat. Ellenőrzés (Google verification) nélkül a felhasználók az „unverified app” figyelmeztetést látják, és legfeljebb 100 felhasználó engedélyezheti; a sima belépéshez (név, e-mail) nem kell ellenőrzés.

## 6. Könyvtár

- Felhasználónként külön: elemek, átiratok (elemenként több, egy fő), fordítások, összefoglaló-változatok, keresési darabok, címkék, jegyzetek, beszélőnevek. Minden felhasználói táblán ott a felhasználó, és a szétválasztást két védvonal őrzi:
  - *az alkalmazás:* minden lekérdezés a felhasználóra szűr;
  - *az adatbázis (sorvédelem, PostgreSQL row-level security):* a táblákon szabály áll (`USING`/`WITH CHECK user_id = current_setting('dwyt.user_id')`), és a központ minden kérés tranzakciójának elején `SET LOCAL dwyt.user_id`-t állít. Így egy kimaradt szűrő sem ad ki idegen sort, beállítás nélkül pedig a lekérdezés hibát ad. Az alkalmazás nem tulajdonos, a szabályt meg nem kerülő szerepkörrel kapcsolódik; a migrációk a tulajdonos szerepkörrel futnak. A szándékosan felhasználók közötti munkák (újrahasznosítás keresése, RSS-figyelés, admin statisztika) külön, szűk kódrészben, külön szerepkörrel futnak. Egy teszt szándékosan szűrő nélkül kérdez, és ellenőrzi, hogy idegen sor nem jön vissza.
- **Saját felvétel** (feltöltés, figyelt mappa) és **nyilvános forrás** (YouTube, URL) megkülönböztetése megmarad: saját felvétel csak a felhasználó helyi LLM-jéhez mehet automatikusan, felhős LLM-hez csak a felhasználó kifejezett beállításával.
- Hang és videó a központban nem tárolódik (a központon átmenő feltöltés csak addig, amíg a futtató át nem vette; 8. fejezet).
- A régi tervből még nem megvalósított, de ide tartozó funkciók: címkék, jegyzet, beszélők elnevezése, a teljes könyvtár exportja (Markdown, JSON).

## 7. Újrahasznosítás

Ha egy felhasználó olyan munkát kér, amit valaki már elvégzett ugyanazon a forráson ugyanazokkal a beállításokkal, a központ nem küldi ki a futtatónak, hanem átveszi az eredményt.

- **A forrás azonosítója:** YouTube-nál a videóazonosító, egyéb URL-nél a normalizált URL, feltöltésnél és figyelt mappánál a fájl SHA-256 hash-e.
- **Lépésenként** dönt (átirat; fordítás; összefoglaló), mert a lépések külön munkák. Egy lépés kulcsa a forrás + a lépés beállításai (mód, modell, nyelv, beszélő-beállítás; fordításnál és összefoglalónál a bemeneti átirat hash-e, a modell és az utasítás-verziója).
- **YouTube és URL:** mindhárom lépés átvehető.
- **Feltöltés:** csak akkor, ha az eredeti feltöltő ezt engedi; saját felvételnél alapból nem engedi. (Az eredményt csak az kaphatja meg, akinél ugyanaz a fájl van; a tartalom így nem szivárog, de az kiderülhetne, hogy a fájl már járt a rendszerben.)
- Az átvett tartalom jelölve van („átvett átirat”), de nem derül ki, kitől származik.
- Az átvevő nem fizet érte (az eredeti kérő fizetett); ezt a felhasználók köre miatt elfogadjuk.
- **Tárolás: közös, módosíthatatlan eredménytár.** Az átirat, a fordítás, az összefoglaló és a belőlük készült keresési darabok (vektorokkal) egyszer tárolódnak, a lépés kulcsa szerint. A felhasználó könyvtárbejegyzése csak hivatkozik rájuk; a személyes adatok (címkék, jegyzet, beszélőnevek, melyik a fő átirat, az összefoglaló választott változata) a felhasználó saját, sorvédett tábláiban vannak. A keresés a felhasználó könyvtárbejegyzésein át éri el a darabokat.
- Az eredménytár nem a felhasználói sorvédelem alatt van, ezért csak a könyvtárbejegyzésen át, illetve az újrahasznosítás szűk kódrészén át olvasható.
- A feltöltésből készült eredmény a tárban „privát” jelölést kap; más csak az eredeti feltöltő engedélyével hivatkozhat rá.
- **Törlés:** ha egy eredményre már senki nem hivatkozik, a rendszer törli (fióktörlésnél is így marad meg a másiknál az átadott eredmény).

## 8. Futtató (`dwyt-runner`)

A felhasználónál fut, kötelező. A régi yt-transcribe API-ból nő ki, egy kifelé kapcsolódó résszel.

- **Feladatai:** YouTube-felirat, letöltés (yt-dlp), hangkonverzió (ffmpeg), felhős átírás, a helyi Whisper hívása (a llama-swap felől), összefoglaló és fordítás (felhős vagy helyi LLM).
- **Kulcsok csak a futtatónál** vannak (AssemblyAI, OpenRouter stb.), helyben tárolva; a központ soha nem látja őket. Ezért az összefoglaló újrakérése is csak bekapcsolt futtatóval megy.
- **Saját felvétel útja:**
  - *(a)* böngészőből a központon át, méretkorláttal (alapból 2 GB): a központ csak addig tárolja, amíg a futtató le nem töltötte;
  - *(b)* közvetlenül a futtatónál: figyelt mappa vagy a futtató helyi feltöltő oldala. A saját felvétel így el sem hagyja a felhasználó gépét; a központ csak az átiratot kapja. Saját felvételhez ez az ajánlott út.
- **Képességek:** minden munkakéréskor bejelenti, mit tud (felirat, felhős átírás, helyi Whisper, LLM-modellek, engedélyezett tartományok, legnagyobb fájlméret); a központ csak ennek megfelelő munkát ad.
- **Biztonság:** csak szűk, ellenőrzött munkatípusokat fogad el; választható tartomány-szűrő (például „csak YouTube”); jogosultság nélküli felhasználóként vagy konténerben fut; saját, visszavonható tokenje van. Ha a központot feltörnék, a támadó ennél többet ne tudjon a futtatóval csináltatni.
- **Telepítés:**
  - minden gépre egy paranccsal, az `uv` csomagkezelővel (Linux, Windows, macOS; a Pythont is hozza, rendszergazda nem kell); az `ffmpeg` és a YouTube-hoz kellő `deno` letöltését maga intézi (a `deno` pip-csomagos elérhetőségét ellenőrizni kell);
  - VPS-re és Linux-szerverre Docker-kép is.
- **Párosítás:** telepítéskor rövid párosítókódot mutat; a felhasználó ezt beírja a felületen, és a futtató megkapja a saját hosszú tokenjét.
- **Frissítés:** naponta megnézi, van-e új változat; magától csak akkor frissül, ha ezt a felhasználó bekapcsolta, alapból csak szól. A yt-dlp mindig magától frissül.
- **Több futtató** is lehet felhasználónként (például otthoni GPU-s és egy VPS). Az első körben egy munkát mindig egy futtató kap: az, amelyik elérhető és tudja a kért módot.
- **Helyi Whisper:** a futtató a `whisper_url` címen (a llama-swap upstream-címe) éri el a GPU-workert, a `whisper_models` modelleket jelenti be. Ha a GPU-gép nem érhető el, a munka később újrapróbálkozik (megvárja); ha a worker elutasítja vagy hibát jelez, a munka hibával áll le. Másik módra nem vált.
- **Kikapcsolt futtató:** a munkák várnak (mint a régi rendszerben az Unraidra). Az RSS-figyelés és a postaláda központi, ezért az új videók akkor is megjelennek, csak feldolgozni nem lehet őket.

## 9. AI-router (`dwyt-airouter`)

Opcionális, mindig bekapcsolt gépre. A régi `ai-router` LiteLLM + llama-swap felállása általánosítva.

- **llama-swap:** egyedül birtokolja a GPU-t, sorba állítja a kéréseket, indítja és leállítja a GPU-gép LLM- és Whisper-konténereit. Ehhez a felhasználó LLM-szerverét a llama-swap indítja (a meglévő llama-server indítóparancsa a llama-swap beállításába kerül); mellette önállóan futó, a GPU-t foglaló szerver nem lehet.
- **Támogatott LLM-szerver** az első körben: llama.cpp (llama-server) és bármi, ami parancssorból vagy Docker-konténerként indítható. Ollama később (ott a modellek ürítését az Ollama API-jával kellene kérni).
- **LiteLLM:** ajánlott, de kikapcsolható. Stabil modellnevek és felhős tartalék (`auto`) a többi kliensnek; akinek csak a futtató számít, annak a llama-swap is elég (az is OpenAI-kompatibilis).
- **Indítók** (a llama-swap mellett cserélhető):
  - *helyi Docker*, ha a GPU-gép ugyanaz a gép;
  - *Docker SSH-n át* (`docker -H ssh://…`), ha a GPU-gép Linux;
  - *Unraid API* (a régi `unraid-container.sh`).
  Windowsos GPU-gép az első körben csak az „egy gépen minden” változatban.
- **Ébresztés (Wake-on-LAN):** opcionális lépés az indítóban: ha a GPU-gép nem válaszol, felkelti, és megvárja. Altatás és kikapcsolás nem a rendszer dolga. Ébresztés nélkül: az LLM a LiteLLM-tartalékkal a felhőbe megy (a felhasználó beállítása szerint), a Whisper-munka vár.
- **Egyetlen modell-leíró fájl** (`models.yaml`): ebből készül a LiteLLM és a llama-swap beállítása, és a GPU-gépen a modellfájlok letöltési listája. A modellneveket így egy helyen kell karbantartani.
- **A `models.yaml` részei:** a GPU-gép (indító, cím, ébresztés, más GPU-s konténerek), a llama-server és a Whisper konténere, a helyi modellek (név, Hugging Face-fájl, kapcsolók, kontextus), a felhős modellek (a kulcs környezeti változóban), a stabil nevek (`auto`, `osszefoglalo`, `osszefoglalo-helyi`: célmodell, gondolkodás ki/be, tartalék) és további GPU-s konténerek (például a régi rendszer workere). Egy AI-routerhez egy GPU-gép tartozik.
- **`dwyt-airouter generate`** ebből írja a `llama-swap.yaml`-t, a `litellm.yaml`-t, a llama-server presetjeit (`models.ini`), a letöltési listát (`downloads.json`) és a portokat (`ports.env`). A `models.ini`-t és a `downloads.json`-t kézzel kell a GPU-gépre másolni.
- **llama.cpp router módban:** egyetlen llama-server konténer, a presetek a `models.ini`-ből, egyszerre egy betöltött modell. A llama-swapban ez egy bejegyzés, és minden presetnév ennek az álneve, így a presetek közötti váltás nem indítja újra a konténert. LiteLLM nélkül a stabil nevekből is preset lesz (a gondolkodás kikapcsolása ekkor a presetben van; tartalék nincs).
- **Az indítók** Pythonban vannak (`dwyt-airouter container run|stop`, ez a llama-swap `cmd`/`cmdStop` parancsa): csak a már létrehozott konténereket indítják és állítják le, indítás előtt leállítják a többi GPU-s konténert, és amíg a konténer fut, a folyamat is fut. A régi `unraid-container.sh` ezzel kiváltva.
- **Telepítés:** `/opt/dwyt-airouter` (program, llama-swap, LiteLLM saját környezetben), beállítások `/etc/dwyt-airouter`, `airouter` felhasználó, két systemd-szolgáltatás (`dwyt-llama-swap`, `dwyt-litellm`). A llama-swap és a LiteLLM változata rögzített (a dokumentáció szerinti, kipróbált változat).

## 10. GPU-gép (`dwyt-gpu`)

Opcionális, NVIDIA GPU-s gépre, igény szerint bekapcsolva.

- **Tartalma:** llama-server konténer, Whisper GPU-worker konténer (a régi `gpu-worker`), a modellek NVMe-gyorsítótára.
- **Modellek letöltése:** `modellek letöltése` parancs: a `models.yaml` listájából a Hugging Face-ről tölti le a GGUF- és Whisper-modelleket, és ellenőrzi a helyet. Kézi másolás is lehetséges.
- **Platform:** Linux + NVIDIA + Docker; Windows WSL2-vel. macOS-en nincs helyi Whisper (a Docker ott nem éri el a GPU-t; ehhez whisper.cpp vagy MLX kellene, ez későbbi kérdés).
- **Hálózat:** a GPU-gép portjait tűzfallal csak az AI-router érje el (a llama-server és a worker maga nem kér azonosítást).
- **Konténerek:** a `compose.yaml` csak létrehozza őket (`docker compose create`), indítani és leállítani az AI-router fogja. `dwyt-llama`: a llama.cpp hivatalos `server-cuda` képe router módban; `dwyt-whisper`: a GPU-worker, helyben építve a repó `worker/` mappájából. Unraidon a két konténer sablonból készül, ugyanezekkel a beállításokkal.
- **Modellmappa** (NVMe): `gguf/` a llama-servernek, `hf/` a Hugging Face-gyorsítótár a Whispernek, mellette a `models.ini`. Mindkét konténer `/models`-ként látja.
- **`dwyt-gpu download downloads.json`:** a hiányzó fájlokat tölti le (darabolt GGUF-nél minden részt), előtte ellenőrzi a helyet; ami megvan, azt kihagyja. A beszélőfelismerő modellhez `HF_TOKEN` kell. **`dwyt-gpu check`:** meghajtó, Docker GPU-hozzáféréssel, konténerek, modellmappa.
- **A worker** a régi `gpu-worker` átvétele változatlan működéssel (egy kérés = egy munka, NDJSON, 10 másodperces szívverés, CUDA-hiba után CPU, ellenőrzőpont a Whisper-lépés után), magyar hibaüzenetekkel.

## 11. Feldolgozás

- **Munkák lépésenként:** átírás, fordítás, összefoglaló, indexelés (ez utóbbi a központban). A központ lépésenként dönt az újrahasznosításról és arról, melyik futtató kapja.
- **Átírási láncolat** (feliratkozásoknál beállított szabály, minden lépés látszik a munkán): YouTube-felirat → helyi Whisper (megvárja a GPU-gépet) → felhős átírás, csak ha a csatornán engedélyezve van.
- **Összefoglaló és fordítás** a régi rendszer szerint: magyar összefoglaló az eredeti nyelvű átiratból; fordítás szegmensenként, időbélyeggel, mozaikszavak magyarázatával; gondolkodás nélküli modellnevek.

## 12. A központ–futtató protokoll

Részletesen: [protokoll.md](protokoll.md), a kérések alakja JSON Schema-ként a [schemas/](../schemas/) mappában. Fő döntések:

- HTTPS, a futtató kezdeményez; munkakérés hosszan várakozó kéréssel (long-poll, kb. 30 s).
- Munka lépésenként, a futtató bejelentett képességei szerint; lízing szívveréssel, lejárt lízingnél a munka visszakerül a sorba.
- Megszakítás a szívverés válaszában.
- Verziózott protokoll: a központ az aktuális és az előző verziót fogadja; régebbi futtató nem kap munkát, és a felületen „frissítsd a futtatót” üzenet jelenik meg.

## 13. Keresés

A régi rendszer szerint (PostgreSQL teljes szöveges keresés `hungarian` + `unaccent`, `pg_trgm`, `pgvector` `bge-m3`-mal, összefésült rangsor), a központban, felhasználónként szűrve. A `bge-m3` egy példányban fut mindenkinek (CPU, kb. 2,2 GB RAM); néhány tucat felhasználónál ez bírható.

## 14. YouTube-feliratkozások és postaláda

A régi rendszer szerint (csatornák Google-lel, Takeout-fájlból vagy kézzel; RSS-figyelés; „mindig / kérdezzen / soha” szabály; Shorts és élő adás kezelése), felhasználónként. Az RSS-figyelés központi: ugyanazt a csatornát több felhasználó követheti, a hírcsatornát elég egyszer lekérni.

## 15. MCP

Felhasználónként, a felületen létrehozott, névvel ellátott, visszavonható tokenekkel (az adatbázisban csak a hash-ük; létrehozáskor egyszer látszanak). Tokenenkénti jogkör: csak olvasás / indítás is; saját felvételekkel / nélkülük. A `/mcp` a nyilvános címen érhető el, mert a felhasználók kívülről használják; tokennel és kéréskorláttal.

## 16. Értesítés

Felhasználónként választható csatorna:

- **ntfy:** a felhasználó telepíti az ntfy alkalmazást, és megad egy véletlen nevű témát (az ntfy.sh-n vagy saját ntfy-szerveren).
- **Home Assistant webhook:** a hozzáértőknek, a régi rendszer értesítéseinek mintájára.
- **Később:** web push (a telefonon a kezdőképernyőre tett oldallal, iPhone-on is).
- **E-mail:** csak meghívóhoz, és csak ha a telepítő megad SMTP-szervert. Ha nincs, az admin kimásolja a meghívólinket, és maga küldi el.

A szabályok a régi rendszerből jönnek, felhasználónként beállíthatóan: kézi beküldésről azonnal; feliratkozásokról napi összesítő vagy csatornánként azonnal; hibáról mindig.

## 17. Nyilvános üzemeltetés

- **Kvóták** (alapértékek; az admin felhasználónként felülírhatja; nyitott regisztrációnál kötelezőek, meghívásosnál ugyanezek az alapértékek):
  - böngészős feltöltés legfeljebb 2 GB fájlonként, egyszerre legfeljebb 2 várakozó feltöltés felhasználónként;
  - felhasználónként 2 GB szöveg és vektor (egy óra átirat vektorokkal kb. 0,3–0,5 MB);
  - a központi munkasorban (indexelés) a felhasználók felváltva kerülnek sorra, így egy nagy behúzás nem akasztja meg a többieket.

- **Apache reverse proxy:** saját (al)domain, Let's Encrypt-tanúsítvány, név szerinti virtual host (a meglévő proxytunnel-beállítástól külön); `LimitRequestBody` a feltöltési korláthoz igazítva (az újabb Apache-ok alapból 1 GB-ra korlátoznak), `ProxyTimeout` a hosszú feltöltésekhez; `X-Forwarded-Proto https`, és a központ csak az Apache címéről fogadja el a továbbított kliens-IP-t; HSTS; fail2ban a belépés ellen.
- A sütik `Secure` jelzővel; a passkey (következő kör) a HTTPS miatt itt már lehetséges.
- **Adatkezelés (GDPR):** a központ üzemeltetője adatkezelő a felhasználók adataira és a feltöltött felvételekben szereplő harmadik személyekre is. Adatvédelmi tájékoztató, fióktörlés, export kell.
- Mentés: a központ adatbázisa (a tulajdonosnál a Proxmox-mentés a PBS-re).

## 18. Átállás a tulajdonosnál

1. A régi rendszer fut tovább.
2. A dwyt központ új LXC-be (publikus, Apache mögött).
3. Futtató és AI-router az `ai-router` LXC-ben (a régi LiteLLM és llama-swap helyett vagy mellett, külön porton), GPU-gép az Unraidon az Unraid-indítóval.
   Átmenetileg két llama-swap osztozik a GPU-n: a dwyt-é a régi konténereket (`llama.cpp`, `yt-transcribe-gpu`) az `other_gpu_containers` között leállítja indítás előtt, a régi `unraid-container.sh` `GPU_CONTAINERS` listájába pedig a dwyt konténerei kerülnek. Egyszerűbb, ha a régi rendszer is a dwyt llama-swapját használja: a régi worker `extra_containers` bejegyzésként kerül bele, és a régi API `WORKER_URL`-je erre mutat.
4. A régi könyvtár egyszeri behozatala a tulajdonos fiókjába (később, nem sürgős).
5. Ha a dwyt jól működik, eldől, kell-e még a régi.

## 19. Körök és sorrend

Körönként egy kipróbálható szelet. A régi rendszer közben fut tovább, ezért a dwyt-nek az első kör után még nem kell mindent tudnia.

| Kör | Tartalom | Repók |
| --- | --- | --- |
| 1. (kész) | GPU nélküli működő szelet: Google-belépés + meghívás + admin tartalékbelépés; könyvtár sorvédelemmel; futtató párosítása; munkasor a protokoll szerint. A futtató YouTube-feliratot és felhős átírást végez, összefoglalót bármely OpenAI-kompatibilis címmel készít. | central, runner, docs (JSON-sémák) |
| 2. (kész, élesben fut) | Saját GPU: `models.yaml` és a belőle készülő beállítások, a három indító, ébresztés, Whisper-worker és llama-server konténer, modellletöltés; a futtató helyi Whisperrel. | airouter, gpu, runner, central |
| 3. | Könyvtár teljesen: fordítás, keresés (`bge-m3`), újrahasznosítás, kvóták, figyelt mappa. | central, runner |
| 4. | Háttér és kliensek: feliratkozások és postaláda, értesítés (ntfy, Home Assistant), MCP. | central |
| 5. | Kiegészítések: passkey, címkék, jegyzet, beszélőnevek, export, a régi könyvtár behozatala; fióktörlés a felhasználó által (5.7); a Google utáni kötelező TOTP beállítása (5.5); meghívó e-mailben SMTP-vel. | central |

- Az adatbázis-séma már az 1. körben az eredménytárral (7. fejezet) készül, akkor is, ha az újrahasznosítás csak a 3. körben működik.
- **Cím:** `dwyt.iodate.date` (a tulajdonos `iodate.date` domainjének aldomainje), az Apache-on külön virtual hosttal és Let's Encrypt-tanúsítvánnyal. Fejlesztés alatt a Google-belépés `http://localhost` visszairányítással is kipróbálható.
- **Hol fut az 1. körben:** új Proxmox LXC (Debian, PostgreSQL 17 + `pgvector`, systemd), eleinte csak a belső hálózaton, tesztfelhasználókkal. Az internetre akkor kerül ki, amikor a belépés, a sorvédelem és az Apache-beállítás kész és át van nézve.
- **Automatikus tesztelés** (GitHub Actions) minden repóban az 1. körtől: tesztek, ruff, pip-audit; a futtató tesztjei Linuxon, Windowson és macOS-en is.

## 20. Nyitott kérdések

| Kérdés | Mit jelent |
| --- | --- |
| A futtató helyi feltöltő oldala | Hogyan lép be a felhasználó a saját gépén futó oldalra (párosított futtatónál helyi token). |
| macOS helyi Whisper | whisper.cpp vagy MLX, diarizálással vagy anélkül. |
| Windowsos távoli GPU-gép | Saját kis ügynökprogram az indításhoz. |
| Ollama a GPU-gépen | Modellürítés az Ollama API-jával. |
| A Whisper-worker képe registryben | Most a GPU-gépen épül (`docker compose build`); kész kép a GitHub Container Registryben (ghcr.io) egyszerűsítené az Unraid-sablont. |
| llama-swap alias-lista | LiteLLM nélkül a `/v1/models` csak a `llama-server` bejegyzést mutatja, a presetneveket nem; a klienseknél kézzel kell megadni a nevet. |
| A régi könyvtár behozatala | Formátum és időpont. |

## 21. Döntésnapló

| # | Döntés |
| --- | --- |
| 1.1 | Többfelhasználós, interneten elérhető szolgáltatás; bárki telepítheti; regisztráció a telepítő döntése szerint (nyitott / meghívásos / zárt); a tulajdonosnál meghívásos. |
| 1.2 | Felhasználónként külön, át nem járható könyvtár. |
| 1.3 | Felhős szolgáltatás csak a felhasználó saját kulcsával; a költség az övé. |
| 1.4 | A régi rendszer megmarad; a dwyt `dwyt-` kezdetű, külön repókban él. |
| 2.1 | Központ + felhasználónkénti futtató; a futtató kötelező, és csak kifelé kapcsolódik (nincs port, VPN, NAT-beállítás). |
| 2.2 | A YouTube-letöltés és a sávszélesség a felhasználó futtatóját terheli; nincs központi futtató. |
| 2.3 | Kulcsok és LLM-hívások csak a futtatónál; a központ nem lát kulcsot. |
| 2.4 | Saját felvétel a központon át (méretkorláttal, 2 GB) vagy közvetlenül a futtatónál (figyelt mappa, helyi feltöltés; ez az ajánlott). |
| 2.5 | Futtató telepítése `uv`-val Linuxra, Windowsra, macOS-re; Docker-kép szervereknek. Docker Desktop nem kötelező. |
| 2.6 | macOS-en az első körben nincs helyi Whisper. |
| 2.7 | Több futtató felhasználónként; egy munkát egy futtató kap, az elérhető és megfelelő képességű. |
| 2.8 | Keresés és `bge-m3` a központban, egy példányban. |
| 3.1 | Újrahasznosítás lépésenként: YouTube/URL mindhárom lépés; feltöltés csak az eredeti feltöltő engedélyével (saját felvételnél alapból nem); jelölve, forrás megnevezése nélkül. |
| 4.1 | Három telepítési csomag: futtató, AI-router (LiteLLM + llama-swap, mindig bekapcsolva), GPU-gép (llama-server, Whisper, NVMe, GPU); egy gépre is tehetők. |
| 4.2 | Támogatott LLM-szerver: llama.cpp és parancssorból vagy Dockerrel indítható szerver; Ollama később. |
| 4.3 | Indítók: helyi Docker, Docker SSH-n át, Unraid API; Windowsos távoli GPU-gép később. |
| 4.4 | LiteLLM ajánlott, de kikapcsolható. |
| 4.5 | Ébresztés (Wake-on-LAN) opcionális lépés az indítóban; altatás és kikapcsolás nem. |
| 4.6 | Egyetlen `models.yaml`; ebből a LiteLLM, a llama-swap beállítása és a letöltési lista. |
| 4.7 | A GPU-gép csomagjában modellletöltő parancs; kézi másolás is lehet. |
| 5.1 | Belépés Google-lel (OIDC, Web application kliens), meghívással; azonosítás a Google `sub` szerint. |
| 5.2 | Google-fiók nélkül az első körben nincs felhasználó; passkey meghívólinkkel a következő körben; más szolgáltatók később. |
| 5.3 | Admin tartalékbelépés jelszó + TOTP-vel. |
| 5.4 | Az admin nem látja a felhasználók könyvtárát; csak fiókadatokat és statisztikát. |
| 5.5 | Saját TOTP a Google mellett telepítési beállítással kötelezővé tehető; alapból nem. |
| 5.6 | MCP- és futtatótokenek felhasználónként, a felületen kezelve, hash-elve; futtató párosítókóddal. |
| 5.7 | Fióktörlés a felhasználó által; az átadott eredmény a másiknál megmarad. |
| 6.1 | Öt repó: `dwyt-docs`, `dwyt-central`, `dwyt-runner`, `dwyt-airouter`, `dwyt-gpu`. |
| 6.2 | Nyilvános repók; AGPL-3.0 a központra, MIT a többire. |
| 6.3 | A dwyt üresen indul; a régi könyvtár később egyszeri behozatallal. |
| 7.1 | Protokoll: HTTPS long-poll; munka lépésenként, képességek szerint; lízing és szívverés. |
| 7.2 | Verziózott protokoll (aktuális + előző); a futtató naponta ellenőriz, önfrissítés csak bekapcsolva; a yt-dlp mindig frissül. |
| 8.1 | Az MCP a nyilvános címen érhető el, felhasználónkénti tokennel és kéréskorláttal. |
| 8.2 | Sorvédelem: PostgreSQL row-level security a felhasználói táblákon, második védvonalként; felhasználók közötti munkák külön szerepkörrel. |
| 8.3 | Értesítés: ntfy és Home Assistant webhook az első körben, web push később; e-mail csak meghívóhoz, ha van SMTP, különben az admin másolja a linket. |
| 8.4 | Kvóták: 2 GB-os böngészős feltöltés, egyszerre 2; 2 GB szöveg és vektor felhasználónként; felváltva kiszolgált központi sor; az admin felülírhatja. |
| 8.5 | Újrahasznosítás közös, módosíthatatlan eredménytárral (átirat, fordítás, összefoglaló, keresési darabok); személyes adatok a felhasználó tábláiban; hivatkozás nélküli eredmény törlődik. |
| 9.1 | Sorrend: 1. GPU nélküli szelet; 2. saját GPU; 3. fordítás, keresés, újrahasznosítás, kvóták, figyelt mappa; 4. feliratkozások, értesítés, MCP; 5. kiegészítések. |
| 9.2 | A központ címe `dwyt.iodate.date`. |
| 9.3 | GitHub Actions minden repóban; a futtató Linuxon, Windowson és macOS-en tesztelve. |
| 9.4 | Az 1. körben új Proxmox LXC, eleinte csak belső hálózaton; internetre átnézés után. |
| 10.1 | Az összefoglaló utasítását és darabolását a futtató írja; a központ a szerkezetes átiratot és a szerepet (`public`/`private`) küldi, a futtató az utasítás verzióját visszaküldi. |
| 10.2 | A futtató a szerep szerint a saját beállításából választ modellt (`llm_public_model`, `llm_private_model`); a központ modellnevet nem ismer. |
| 10.3 | A futtató az ffmpeg-et (`imageio-ffmpeg`) és a `deno`-t is Python-csomagként kapja; mindhárom platformon kézi telepítés nélkül. |
| 10.4 | Élesben a két adatbázis-szerepkör (`dwyt` tulajdonos, `dwyt_app` sorvédett) jelszó nélkül, peer hitelesítéssel és névleképezéssel csatlakozik. |
| 10.5 | Az 1. körben a meghívó linkjét az admin másolja ki; SMTP-s küldés, fióktörlés a felhasználó által és a Google utáni kötelező TOTP az 5. körben. |
| 11.1 | Egy `models.yaml` írja le a GPU-gépet, a konténereket, a helyi és felhős modelleket és a stabil neveket; `dwyt-airouter generate` ebből készíti a llama-swap, a LiteLLM és a llama-server (`models.ini`) beállítását és a letöltési listát. Egy AI-routerhez egy GPU-gép. |
| 11.2 | A llama-server egyetlen router módú konténer; a presetnevek egy llama-swap-bejegyzés álnevei. LiteLLM nélkül a stabil nevek presetek lesznek, tartalék nélkül. |
| 11.3 | Az indítók Pythonban, a llama-swap `cmd`/`cmdStop` parancsaként; csak meglévő konténert indítanak és állítanak le, a többi GPU-s konténert (`other_gpu_containers` is) előtte leállítják. Az ébresztés ugyanitt: 30 másodpercenként csomag, amíg a gép nem válaszol. |
| 11.4 | A GPU-gépen `compose.yaml` (csak létrehozás), a llama.cpp hivatalos képe és a helyben épített Whisper-worker; közös modellmappa `gguf/` és `hf/` almappával; `dwyt-gpu download` és `check`. |
| 11.5 | A futtató helyi Whisper-módja: `whisper_url`, `whisper_models`, `whisper_timeout_min`; elérhetetlen GPU-gép → később újra, elutasítás vagy worker-hiba → végleges hiba. A futtató bejelenti a `whisper_models` képességet, a központ a kért modell szerint ad munkát, és jelzi, ha egyik futtató sem tudja. |
| 11.6 | A régi rendszer átmenetileg ugyanazon a GPU-n: kölcsönösen leállítják egymás konténereit, vagy a régi worker a dwyt llama-swapjába kerül (`extra_containers`). |
