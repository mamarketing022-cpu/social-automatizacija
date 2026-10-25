"""Pravi trajne tokene za FB stranice (i njihove IG naloge).

Pokreće ga korisnik sam u terminalu:
    python alat/tokeni.py

Pita za (unos se ne prikazuje na ekranu):
  1. User token iz Graph API Explorera (dugme "Copy Token")
  2. App Secret (App settings -> Basic -> App secret -> Show)

Kratki user token mijenja za dugotrajni, a iz njega uzima tokene stranica,
koji ne ističu. Upisuje ih u lokalni fajl .env (nikad ne ide na GitHub)
i ispisuje koje GitHub Secrets treba napraviti.
"""

import getpass
import json
import urllib.parse
import urllib.request
from pathlib import Path

KORIJEN = Path(__file__).resolve().parent.parent
GRAPH = "https://graph.facebook.com/v23.0"
NALOZI = json.loads((KORIJEN / "alat" / "nalozi.json").read_text(encoding="utf-8"))


def get(putanja, **parametri):
    url = f"{GRAPH}/{putanja}?{urllib.parse.urlencode(parametri)}"
    with urllib.request.urlopen(url, timeout=60) as odgovor:
        return json.loads(odgovor.read())


def main():
    app_id = "1147688117825200"
    kratki = getpass.getpass("Zalijepite User token (ne vidi se dok lijepite) i Enter: ").strip()
    tajna = getpass.getpass("Zalijepite App Secret i Enter: ").strip()

    dugi = get("oauth/access_token", grant_type="fb_exchange_token", client_id=app_id,
               client_secret=tajna, fb_exchange_token=kratki)["access_token"]
    stranice = get("me/accounts", fields="id,name,access_token", limit=100, access_token=dugi)["data"]
    po_id = {s["id"]: s for s in stranice}

    redovi = []
    for biznis, nalog in NALOZI.items():
        if biznis.startswith("_") or nalog.get("api") != "facebook":
            continue
        stranica = po_id.get(nalog["page_id"])
        if not stranica:
            print(f"  ! {biznis}: stranica {nalog['page_id']} nije među odobrenima")
            continue
        redovi.append(f"{nalog['token_env']}={stranica['access_token']}")
        print(f"  OK {biznis}: {stranica['name']}")

    env = KORIJEN / ".env"
    postojeci = [r for r in (env.read_text(encoding="utf-8").splitlines() if env.exists() else [])
                 if r.split("=", 1)[0] not in {x.split("=", 1)[0] for x in redovi}]
    env.write_text("\n".join(postojeci + redovi) + "\n", encoding="utf-8")
    print(f"\nTokeni su upisani u {env} (samo na ovom računaru).")
    print("Na GitHubu napravite Secrets s ovim imenima:", ", ".join(r.split("=", 1)[0] for r in redovi))


if __name__ == "__main__":
    main()
