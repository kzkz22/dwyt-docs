# dwyt-docs

A **dwyt** közös leírásai: a funkcionális terv, az architektúra, a döntésnapló és a központ–futtató protokoll.

A dwyt videók és hangfelvételek átiratát (időbélyeggel, beszélőkkel), magyar fordítását és összefoglalóját készíti, felhasználónként külön, kereshető könyvtárban, a YouTube-feliratkozások háttérfeldolgozásával. A számítás a felhasználó saját futtatóján és (ha van) saját GPU-ján fut; a központ irányít és tárol.

## Leírások

- [Funkcionális terv és döntésnapló](docs/terv.md)
- [Központ–futtató protokoll (vázlat)](docs/protokoll.md)
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

Terv; kód még nincs.

## Az ábra frissítése

Az ábra forrása a `tools/architektura_svg.py` (ez írja a `docs/architektura.svg`-t); a PNG a `tools/render_png.js`-szel készül (`npm i playwright`, majd `node tools/render_png.js`).

## Licenc

MIT, lásd [LICENSE](LICENSE).
