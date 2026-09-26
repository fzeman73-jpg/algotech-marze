# Algotech – denní marže (web)

**https://marze.algotech.info** – zašifrovaný denní dashboard marže (heslo zná jen úzký okruh).

Jak to běží (nikdo se o nic nestará):
1. **Ranní agent** (Claude, skill `algotech-denni-marze`) sestaví HTML dashboard, zašifruje ho
   (`tools/encrypt_for_web.py`, heslo z `publish_config.json` na Drive) a nahraje jako
   `marze_web_RRRRMMDD-HHMM.json` do složky Google Drive **„Algotech - marže web (šifrované)“**
   (sdílená odkazem – obsahuje jen šifrované soubory).
2. **GitHub Action** (`.github/workflows/publish.yml`) každou hodinu dopoledne stáhne nejnovější soubor
   (`tools/fetch_from_drive.py`) a nasadí web přes GitHub Pages. Když se něco nepovede, zůstane
   na webu poslední dobrá verze.
3. **Web** (`docs/index.html`) po zadání hesla dashboard rozšifruje v prohlížeči.

Šifrování: gzip → AES-256-GCM, klíč PBKDF2-SHA256 (310 000 iterací) z hesla stránky.
Na GitHubu nejsou žádné tokeny ani hesla.
