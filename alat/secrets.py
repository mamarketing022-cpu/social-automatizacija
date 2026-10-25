"""Osvježava Instagram tokene i šalje sve tokene iz .env u GitHub Secrets.

    python alat/secrets.py            # osvježi IG tokene + pošalji sve na GitHub
    python alat/secrets.py --samo-slanje

Instagram (Instagram Login) tokeni traju 60 dana; osvježavanje ih produži na
novih 60. Zato ovo treba pokrenuti bar jednom mjesečno (zakazano na računaru).
GitHub pristup uzima iz Git prijave koja je već sačuvana na ovom računaru.
"""

import base64
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from nacl import encoding, public

KORIJEN = Path(__file__).resolve().parent.parent
ENV = KORIJEN / ".env"
REPO = "mamarketing022-cpu/social-automatizacija"
NALOZI = json.loads((KORIJEN / "alat" / "nalozi.json").read_text(encoding="utf-8"))


def ucitaj_env():
    parovi = {}
    for red in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in red:
            k, v = red.split("=", 1)
            parovi[k.strip()] = v.strip()
    return parovi


def ig_tokeni():
    """Imena tokena koji su Instagram Login (ističu za 60 dana)."""
    imena = []
    for biznis, nalog in NALOZI.items():
        if biznis.startswith("_"):
            continue
        if nalog.get("ig_api") == "instagram":
            imena.append(nalog["ig_token_env"])
        elif nalog.get("api") == "instagram":
            imena.append(nalog["token_env"])
    return imena


def osvjezi(parovi):
    for ime in ig_tokeni():
        if ime not in parovi:
            continue
        url = "https://graph.instagram.com/refresh_access_token?" + urllib.parse.urlencode(
            {"grant_type": "ig_refresh_token", "access_token": parovi[ime]})
        try:
            with urllib.request.urlopen(url, timeout=60) as odgovor:
                novi = json.loads(odgovor.read())
            parovi[ime] = novi["access_token"]
            print(f"  osvježen {ime} (još {int(novi.get('expires_in', 0)) // 86400} dana)")
        except urllib.error.HTTPError as e:
            print(f"  ! {ime} nije osvježen: {e.read().decode(errors='replace')}")
    ENV.write_text("".join(f"{k}={v}\n" for k, v in parovi.items()), encoding="utf-8")


def github_token():
    upit = "protocol=https\nhost=github.com\n\n"
    izlaz = subprocess.run(["git", "credential", "fill"], input=upit, capture_output=True,
                           text=True, check=True).stdout
    return dict(r.split("=", 1) for r in izlaz.splitlines() if "=" in r)["password"]


def github(metoda, putanja, token, tijelo=None):
    zahtjev = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{putanja}", method=metoda,
        data=json.dumps(tijelo).encode() if tijelo else None,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(zahtjev, timeout=60) as odgovor:
        sadrzaj = odgovor.read()
        return json.loads(sadrzaj) if sadrzaj else {}


def posalji(parovi):
    token = github_token()
    kljuc = github("GET", "actions/secrets/public-key", token)
    kutija = public.SealedBox(public.PublicKey(kljuc["key"].encode(), encoding.Base64Encoder()))
    for ime, vrijednost in parovi.items():
        if not ime.startswith("TOKEN_"):
            continue
        sifrovano = base64.b64encode(kutija.encrypt(vrijednost.encode())).decode()
        github("PUT", f"actions/secrets/{ime}", token,
               {"encrypted_value": sifrovano, "key_id": kljuc["key_id"]})
        print(f"  GitHub Secret {ime} postavljen")


def main():
    parovi = ucitaj_env()
    if "--samo-slanje" not in sys.argv:
        osvjezi(parovi)
    posalji(parovi)


if __name__ == "__main__":
    main()
