#!/usr/bin/env python3
"""Zašifruje HTML dashboard denní marže pro web marze.algotech.info.

    python3 encrypt_for_web.py <dashboard.html> <publish_config.json> <vystup.json>

publish_config.json (Google Drive, složka „Algotech - denní marže“): {"page_password": "…"}
Výstup = jeden řádek JSON (gzip → AES-256-GCM, klíč PBKDF2-SHA256 310 000× z hesla). Agent ho nahraje
na Drive do složky „Algotech - marže web (šifrované)“; GitHub si ho odtud sám stáhne a zveřejní.
"""
import base64, gzip, json, os, sys
from datetime import datetime, timezone
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT = base64.b64decode("QWxnb3RlY2gtbWFyemUtdjE=")  # pevná sůl (není tajná), stejná ve webu
ITER = 310_000

html = open(sys.argv[1], encoding="utf-8").read()
pw = json.load(open(sys.argv[2], encoding="utf-8"))["page_password"]
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=ITER).derive(pw.encode())
iv = os.urandom(12)
ct = AESGCM(key).encrypt(iv, gzip.compress(html.encode("utf-8"), 9), None)
b = lambda x: base64.b64encode(x).decode()
out = {"v": 1, "iter": ITER, "salt": b(SALT), "iv": b(iv), "ct": b(ct),
       "published": datetime.now(timezone.utc).isoformat(timespec="seconds"), "len": len(ct)}
open(sys.argv[3], "w").write(json.dumps(out, separators=(",", ":")))
print(f"OK – zašifrováno {len(html)//1024} kB HTML → {os.path.getsize(sys.argv[3])//1024} kB")
