"""Objavljuje odobrene objave na Facebook i Instagram.

Prolazi kroz biznisi/<biznis>/red/<GGGG-MM-DD_tip>/objava.json i objavljuje one
sa statusom "odobreno" čije je vrijeme došlo. Nakon objave upisuje status
"objavljeno" (ili "greska") nazad u objava.json.

Pokretanje:
    python alat/objavi.py              # objavi sve što je na redu
    python alat/objavi.py --proba      # samo ispiši šta bi objavio, ništa ne šalje
    python alat/objavi.py --sad <put>  # objavi tu jednu objavu odmah (mora biti odobrena)

Varijable okruženja:
    MEDIA_BASE_URL   javni URL korijena projekta (npr. raw.githubusercontent.com/...);
                     Instagram slike/video uzima samo s javnog linka.
    TOKEN_<BIZNIS>   pristupni token za svaki biznis (ime iz alat/nalozi.json).
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

KORIJEN = Path(__file__).resolve().parent.parent
BIZNISI = KORIJEN / "biznisi"
NALOZI = json.loads((KORIJEN / "alat" / "nalozi.json").read_text(encoding="utf-8"))

GRAPH = {"facebook": "https://graph.facebook.com/v23.0", "instagram": "https://graph.instagram.com/v23.0"}

# Objava starija od ovoga se više ne objavljuje automatski (npr. server je dugo stajao).
NAJDUZE_KASNJENJE = timedelta(hours=12)


def sarajevo_sad():
    """Trenutno vrijeme u Sarajevu (CET/CEST), bez zavisnosti od tzdata."""
    utc = datetime.now(timezone.utc)
    godina = utc.year
    # Ljetno vrijeme EU: od zadnje nedjelje u martu 01:00 UTC do zadnje nedjelje u oktobru 01:00 UTC.
    def zadnja_nedjelja(mjesec):
        d = datetime(godina, mjesec + 1, 1, 1, tzinfo=timezone.utc) - timedelta(days=1)
        return d - timedelta(days=(d.weekday() + 1) % 7)
    ljeto = zadnja_nedjelja(3) <= utc < zadnja_nedjelja(10)
    return (utc + timedelta(hours=2 if ljeto else 1)).replace(tzinfo=None)


def api(baza, putanja, token, podaci=None, metoda="POST"):
    podaci = dict(podaci or {}, access_token=token)
    url = f"{GRAPH[baza]}/{putanja}"
    if metoda == "GET":
        zahtjev = urllib.request.Request(url + "?" + urllib.parse.urlencode(podaci))
    else:
        zahtjev = urllib.request.Request(url, data=urllib.parse.urlencode(podaci).encode(), method="POST")
    try:
        with urllib.request.urlopen(zahtjev, timeout=120) as odgovor:
            return json.loads(odgovor.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{putanja}: {e.read().decode(errors='replace')}") from None


def javni_url(folder, ime):
    baza = os.environ.get("MEDIA_BASE_URL", "").rstrip("/")
    if not baza:
        raise RuntimeError("MEDIA_BASE_URL nije postavljen; Instagram/Facebook trebaju javni link medija.")
    relativno = (folder / ime).relative_to(KORIJEN).as_posix()
    return f"{baza}/{urllib.parse.quote(relativno)}"


def je_video(ime):
    return ime.lower().endswith((".mp4", ".mov"))


def objavi_fb(nalog, token, objava, folder):
    stranica = nalog["page_id"]
    tekst = objava.get("tekst_fb") or objava.get("tekst_ig", "")
    mediji = objava["mediji"]
    if je_video(mediji[0]):
        r = api("facebook", f"{stranica}/videos", token,
                {"file_url": javni_url(folder, mediji[0]), "description": tekst})
        return r.get("id")
    if len(mediji) == 1:
        r = api("facebook", f"{stranica}/photos", token,
                {"url": javni_url(folder, mediji[0]), "message": tekst})
        return r.get("post_id") or r.get("id")
    # Više slika: prvo neobjavljene fotografije, pa jedna objava koja ih sadrži.
    slike = [api("facebook", f"{stranica}/photos", token,
                 {"url": javni_url(folder, m), "published": "false"})["id"] for m in mediji]
    podaci = {"message": tekst}
    for i, slika in enumerate(slike):
        podaci[f"attached_media[{i}]"] = json.dumps({"media_fbid": slika})
    return api("facebook", f"{stranica}/feed", token, podaci).get("id")


def cekaj_ig_kontejner(baza, kontejner, token):
    for _ in range(60):
        status = api(baza, kontejner, token, {"fields": "status_code"}, metoda="GET").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram nije obradio medij (status {status}).")
        time.sleep(10)
    raise RuntimeError("Instagram predugo obrađuje medij.")


def ig_kontejner(baza, ig, token, folder, ime, dodatno):
    if je_video(ime):
        podaci = {"media_type": "REELS", "video_url": javni_url(folder, ime)}
    else:
        podaci = {"image_url": javni_url(folder, ime)}
    kontejner = api(baza, f"{ig}/media", token, {**podaci, **dodatno})["id"]
    cekaj_ig_kontejner(baza, kontejner, token)
    return kontejner


def objavi_ig(nalog, token, objava, folder):
    baza, ig = nalog.get("ig_api", nalog["api"]), nalog["ig_id"]
    tekst = objava.get("tekst_ig") or objava.get("tekst_fb", "")
    mediji = objava["mediji"]
    if len(mediji) == 1:
        kontejner = ig_kontejner(baza, ig, token, folder, mediji[0], {"caption": tekst})
    else:
        djeca = [ig_kontejner(baza, ig, token, folder, m, {"is_carousel_item": "true"}) for m in mediji]
        kontejner = api(baza, f"{ig}/media", token,
                        {"media_type": "CAROUSEL", "children": ",".join(djeca), "caption": tekst})["id"]
        cekaj_ig_kontejner(baza, kontejner, token)
    return api(baza, f"{ig}/media_publish", token, {"creation_id": kontejner}).get("id")


def objavi(biznis, folder, objava, proba):
    nalog = NALOZI[biznis]
    mreze = [m for m in objava.get("mreze", nalog["mreze"]) if m in nalog["mreze"]]
    if proba:
        print(f"  [proba] {biznis}: {folder.name} -> {', '.join(mreze)} ({', '.join(objava['mediji'])})")
        return
    rezultat = objava.setdefault("rezultat", {})
    for mreza in mreze:
        if rezultat.get(mreza):
            continue  # već objavljeno u ranijem pokušaju
        # IG može imati poseban token (Instagram Login) kad nije vezan za FB stranicu.
        ime_tokena = nalog.get("ig_token_env", nalog["token_env"]) if mreza == "ig" else nalog["token_env"]
        token = os.environ.get(ime_tokena)
        if not token:
            raise RuntimeError(f"Nema tokena {ime_tokena}.")
        funkcija = objavi_fb if mreza == "fb" else objavi_ig
        rezultat[mreza] = funkcija(nalog, token, objava, folder)
        print(f"  {biznis}: {folder.name} objavljeno na {mreza} (id {rezultat[mreza]})")


def sacuvaj(putanja, objava):
    putanja.write_text(json.dumps(objava, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def obradi(putanja, sad, proba, odmah=False):
    objava = json.loads(putanja.read_text(encoding="utf-8"))
    if objava.get("status") != "odobreno":
        return
    biznis = putanja.parent.parent.parent.name
    zakazano = datetime.fromisoformat(f"{objava['datum']}T{objava['vrijeme']}")
    if not odmah:
        if sad < zakazano:
            return
        if sad - zakazano > NAJDUZE_KASNJENJE:
            print(f"  {biznis}: {putanja.parent.name} PROPUŠTENO (zakazano {zakazano}), nije objavljeno.")
            if not proba:
                objava["status"] = "propusteno"
                sacuvaj(putanja, objava)
            return
    try:
        objavi(biznis, putanja.parent, objava, proba)
        if not proba:
            objava["status"] = "objavljeno"
            objava["objavljeno_u"] = sad.isoformat(timespec="minutes")
            objava.pop("greska", None)
    except Exception as e:  # noqa: BLE001 - grešku zapisujemo da je korisnik vidi
        print(f"  {biznis}: {putanja.parent.name} GREŠKA: {e}")
        objava["greska"] = str(e)
        if not proba:
            objava["status"] = "greska"
    if not proba:
        sacuvaj(putanja, objava)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proba", action="store_true", help="ništa ne šalje, samo ispisuje")
    parser.add_argument("--sad", help="objavi odmah ovu objavu (put do foldera ili objava.json)")
    args = parser.parse_args()
    sad = sarajevo_sad()
    print(f"Vrijeme (Sarajevo): {sad:%Y-%m-%d %H:%M}")
    if args.sad:
        putanja = Path(args.sad).resolve()
        obradi(putanja if putanja.suffix == ".json" else putanja / "objava.json", sad, args.proba, odmah=True)
        return
    for putanja in sorted(BIZNISI.glob("*/red/*/objava.json")):
        obradi(putanja, sad, args.proba)


if __name__ == "__main__":
    sys.exit(main())
