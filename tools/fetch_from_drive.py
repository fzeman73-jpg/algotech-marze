#!/usr/bin/env python3
"""GitHub Action: stáhne nejnovější šifrovaný dashboard ze sdílené složky na Google Drive.

Složka „Algotech - marže web (šifrované)“ je sdílená „kdokoli s odkazem – čtenář“ a obsahuje JEN
šifrované soubory marze_web_RRRRMMDD-HHMM.json (nahrává je ranní agent). Bez hesla jsou nečitelné.
Při jakékoli chybě skript skončí s chybou → nasazení se přeskočí a na webu zůstane poslední dobrá verze.
"""
import json, os, re, sys, urllib.request, base64

FOLDER = os.environ.get("DRIVE_FOLDER_ID", "1C0IGB-CVTw316lgRIjHwe-HdMvNLSVdw")
OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/dashboard.enc.json"
UA = {"User-Agent": "Mozilla/5.0 (algotech-marze publisher)"}

def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()

html = get(f"https://drive.google.com/embeddedfolderview?id={FOLDER}").decode("utf-8", "replace")
# položky: odkaz na soubor + název
entries = re.findall(r'href="https://drive\.google\.com/file/d/([\w-]+)/view[^"]*".*?class="flip-entry-title">([^<]+)<', html, re.S)
files = sorted(((t.strip(), i) for i, t in entries if re.fullmatch(r"marze_web_\d{8}-\d{4}\.json", t.strip())), reverse=True)
if not files:
    sys.exit(f"Ve složce není žádný soubor marze_web_*.json (nalezeno položek: {len(entries)}). Je složka sdílená odkazem?")
title, fid = files[0]
data = get(f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t")
d = json.loads(data)
assert d.get("v") == 1 and all(k in d for k in ("iv", "ct", "salt", "iter", "published")), "nečekaný formát"
ct = base64.b64decode(d["ct"], validate=True)
assert d.get("len") in (None, len(ct)), f"soubor je useknutý ({len(ct)} B místo {d.get('len')} B)"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "wb").write(data)
print(f"OK – {title} (publikováno {d['published']}, {len(data)//1024} kB)")
