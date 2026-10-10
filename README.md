# dwyt-docs

A **dwyt** közös leírásai: a funkcionális terv, az architektúra, a döntésnapló és a központ–futtató protokoll.

A dwyt videók és hangfelvételek átiratát (időbélyeggel, beszélőkkel), magyar fordítását és összefoglalóját készíti, felhasználónként külön, kereshető könyvtárban, a YouTube-feliratkozások háttérfeldolgozásával. A számítás a felhasználó saját futtatóján és (ha van) saját GPU-ján fut; a központ irányít és tárol.

## Leírások

- [Funkcionális terv és döntésnapló](docs/terv.md)
- [Központ–futtató protokoll](docs/protokoll.md) és a [JSON-sémák](schemas/)
- [Adatvédelmi tájékoztató](docs/adatvedelem.md)
- [Architektúra-ábra](docs/architektura.png) ([SVG](docs/architektura.svg))

## A dwyt repói

| Repó | Mi |
| --- | --- |
| [dwyt-docs](https://github.com/kzkz22/dwyt-docs) | Ez: terv, architektúra, protokoll |
| [dwyt-central](https://github.com/kzkz22/dwyt-central) | Központ: webes felület, belépés, könyvtár, keresés, MCP |
| [dwyt-runner](https://github.com/kzkz22/dwyt-runner) | Futtató: letöltés, felirat, átírás, LLM-hívások (Linux, Windows, macOS) |
| [dwyt-airouter](https://github.com/kzkz22/dwyt-airouter) | AI-router: LiteLLM + llama-swap, GPU-sor, indítók |
| [dwyt-gpu](https://github.com/kzkz22/dwyt-gpu) | GPU-gép: llama-server, Whisper GPU-worker, modellek |

## Állapot

Az 1. kör kész: a központ ([dwyt-central](https://github.com/kzkz22/dwyt-central)) és a futtató ([dwyt-runner](https://github.com/kzkz22/dwyt-runner)) Google-belépéssel, meghívóval, sorvédett könyvtárral, YouTube-felirattal, felhős átírással és összefoglalóval. A 2. kör (saját GPU) is elkészült: az AI-router ([dwyt-airouter](https://github.com/kzkz22/dwyt-airouter): `models.yaml`, llama-swap, LiteLLM, indítók, ébresztés), a GPU-gép ([dwyt-gpu](https://github.com/kzkz22/dwyt-gpu): llama-server, Whisper-worker, modellletöltés) és a helyi Whisper a futtatóban; éles kipróbálásra vár. Következik a 3. kör: fordítás, keresés, újrahasznosítás.

## Az ábra frissítése

Az ábra forrása a `tools/architektura_svg.py` (ez írja a `docs/architektura.svg`-t); a PNG a `tools/render_png.js`-szel készül (`npm i playwright`, majd `node tools/render_png.js`).

## Licenc

MIT, lásd [LICENSE](LICENSE).
