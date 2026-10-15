"""Try AssemblyAI's LLM Gateway with your own key (plan 19a, item 17). Standard library only; Windows, Linux, macOS.

    python assemblyai_gateway_proba.py                          # a built-in Hungarian sample text, the models below
    python assemblyai_gateway_proba.py atirat.txt               # your own transcript (e.g. a TXT downloaded from dwyt)
    python assemblyai_gateway_proba.py atirat.txt MODELL ...    # other models

The key is asked without echo and never printed. Each model gets the same streamed request (temperature 0.3); a
"too many requests" answer is retried once after a minute. It prints the summary, the time and the tokens used.
"""
import getpass
import json
import sys
import time
import urllib.error
import urllib.request

URL = "https://llm-gateway.assemblyai.com/v1/chat/completions"
MODELS = sys.argv[2:] or ["qwen3.5-4b-32k-fast", "alibaba/qwen3-next-80b-a3b", "gemini-2.5-flash-lite"]
SAMPLE = (
    "Ma a Huawei Watch D3 okosórát nézzük meg. Ez az első olyan okosóra, amely orvostechnikai kategóriás, "
    "mandzsettás vérnyomásmérést tesz lehetővé a csuklón: a szíjban egy kis felfújható mandzsetta van, ami "
    "méréskor rászorul a csuklóra, ugyanúgy, mint egy hagyományos vérnyomásmérő. A legtöbb okosóra csak optikai "
    "becslést ad, ami pontatlanabb. Az elődjéhez, a Watch D2-höz képest az óra vékonyabb és könnyebb lett, a "
    "kijelző nagyobb, az akkumulátor pedig nagyjából egy hétig bírja normál használat mellett. Hátrány, hogy a "
    "szoftverboltban kevés a harmadik féltől származó alkalmazás, és az ára magasabb, mint a versenytársaké. "
    "Összességében annak ajánlom, akinek rendszeresen mérnie kell a vérnyomását, és nem akar külön eszközt hordani."
)
PROMPT = ("Foglald össze magyarul, tömören, Markdownban: egy egymondatos lényeg, utána 3-6 pontban a fő "
          "állítások. Csak azt írd, ami a szövegben van.\n\nA szöveg:\n")


def call(key: str, model: str, text: str, bearer: bool = True, stream: bool = True, retry: bool = True) -> None:
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT + text}], "max_tokens": 900,
            "stream": stream, "temperature": 0.3}
    if stream:
        body["stream_options"] = {"include_usage": True}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST", headers={
        "Content-Type": "application/json", "Authorization": ("Bearer " if bearer else "") + key})
    label = f"{'Bearer' if bearer else 'kulcs Bearer nélkül'}, {'streamelt' if stream else 'egyben'}"
    print(f"\n=== {model} ({label}) ===")
    start = time.time()
    first = None
    out, usage = [], None
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            if not stream:
                data = json.loads(resp.read())
                out.append(data["choices"][0]["message"].get("content") or "")
                usage = data.get("usage")
            else:
                for raw in resp:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    chunk = json.loads(payload)
                    usage = chunk.get("usage") or usage
                    for choice in chunk.get("choices") or []:
                        piece = (choice.get("delta") or {}).get("content") or ""
                        if piece and first is None:
                            first = time.time() - start
                        out.append(piece)
    except urllib.error.HTTPError as exc:
        print(f"HIBA: HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:600]}")
        if exc.code == 429 and retry:
            print("(túl sok kérés: egy perc múlva még egyszer)")
            time.sleep(62)
            call(key, model, text, bearer, stream, retry=False)
        return
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"HIBA: nem érhető el: {exc}")
        return
    total = time.time() - start
    print("".join(out).strip() or "(üres válasz)")
    print(f"\n-- idő: {total:.1f} s" + (f", első szó: {first:.1f} s" if first is not None else "")
          + (f", tokenek: {usage}" if usage else ""))


def main() -> None:
    text = SAMPLE
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()[:60000]  # the 4B model has a 33K-token window: this is about its limit
    key = getpass.getpass("AssemblyAI-kulcs (nem látszik gépelés közben): ").strip()
    if not key:
        sys.exit("Nincs kulcs.")
    for model in MODELS:
        call(key, model, text)
    print("\nKérlek, másold vissza a fenti kimenetet (a kulcs nincs benne).")


if __name__ == "__main__":
    main()
