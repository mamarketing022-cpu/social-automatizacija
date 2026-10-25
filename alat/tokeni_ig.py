"""Pravi Instagram token (Instagram Login) za nalog koji nije vezan za FB stranicu.

1. Na nalogu (npr. emmas.jewelry_) otvoriti link za prijavu (IG_LINK ispod) u
   Instagramovom ugrađenom browseru i kliknuti "Allow".
2. Instagram preusmjeri na github.com/...?code=XXXX - kopirati tu cijelu adresu.
3. Pokrenuti:
       python alat/tokeni_ig.py emma "<kopirana adresa ili samo code>"
   Skripta pita za Instagram App Secret (ne vidi se dok se lijepi).

Kod vrijedi 1 sat i može se iskoristiti samo jednom.
Dugotrajni IG token traje 60 dana; alat ga mora osvježavati (refresh).
"""

import getpass
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

KORIJEN = Path(__file__).resolve().parent.parent
NALOZI = json.loads((KORIJEN / "alat" / "nalozi.json").read_text(encoding="utf-8"))

IG_APP_ID = "1592320478794763"
REDIRECT = "https://github.com/mamarketing022-cpu/social-automatizacija"
IG_LINK = ("https://www.instagram.com/oauth/authorize?" + urllib.parse.urlencode({
    "client_id": IG_APP_ID,
    "redirect_uri": REDIRECT,
    "response_type": "code",
    "scope": "instagram_business_basic,instagram_business_content_publish",
}))


def zahtjev(url, podaci=None):
    tijelo = urllib.parse.urlencode(podaci).encode() if podaci else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=tijelo), timeout=60) as odgovor:
            return json.loads(odgovor.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Greška od Instagrama: {e.read().decode(errors='replace')}")


def main():
    if len(sys.argv) < 3:
        print("Link za prijavu:\n" + IG_LINK)
        print("\nUpotreba: python alat/tokeni_ig.py <biznis> \"<adresa sa code=...>\"")
        return
    biznis, ulaz = sys.argv[1], sys.argv[2].strip()
    nalog = NALOZI[biznis]
    ime = nalog.get("ig_token_env", nalog["token_env"])

    kod = urllib.parse.parse_qs(urllib.parse.urlparse(ulaz).query).get("code", [ulaz])[0]
    kod = kod.split("#")[0]
    tajna = os.environ.get("IG_APP_SECRET") or getpass.getpass("Zalijepite Instagram App Secret i Enter: ")
    tajna = tajna.strip()

    kratki = zahtjev("https://api.instagram.com/oauth/access_token", {
        "client_id": IG_APP_ID, "client_secret": tajna, "grant_type": "authorization_code",
        "redirect_uri": REDIRECT, "code": kod,
    })
    dugi = zahtjev("https://graph.instagram.com/access_token?" + urllib.parse.urlencode({
        "grant_type": "ig_exchange_token", "client_secret": tajna, "access_token": kratki["access_token"],
    }))
    ja = zahtjev("https://graph.instagram.com/v23.0/me?" + urllib.parse.urlencode({
        "fields": "user_id,username", "access_token": dugi["access_token"],
    }))
    if str(ja.get("user_id")) != nalog["ig_id"]:
        sys.exit(f"Pažnja: prijavljen je @{ja.get('username')}, a ne nalog za {biznis}. Token NIJE sačuvan.")

    env = KORIJEN / ".env"
    redovi = [r for r in (env.read_text(encoding="utf-8").splitlines() if env.exists() else [])
              if not r.startswith(ime + "=")]
    env.write_text("\n".join(redovi + [f"{ime}={dugi['access_token']}"]) + "\n", encoding="utf-8")
    dana = int(dugi.get("expires_in", 0)) // 86400
    print(f"OK @{ja['username']}: token upisan u .env kao {ime} (vrijedi {dana} dana).")


if __name__ == "__main__":
    main()
