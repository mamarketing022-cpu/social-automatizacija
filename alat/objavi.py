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

# Provjera da je objava stvarno na profilu: 10 min nakon objave (najkasnije 6 h poslije).
PROVJERA_NAKON = timedelta(minutes=10)
PROVJERA_DO = timedelta(hours=6)


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
        return objavi_fb_reels(stranica, token, tekst, javni_url(folder, mediji[0]))
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


def objavi_fb_reels(stranica, token, tekst, url):
    """Video kao Facebook Reels (ne običan video): start -> upload s linka -> finish."""
    video = api("facebook", f"{stranica}/video_reels", token, {"upload_phase": "start"})["video_id"]
    zahtjev = urllib.request.Request(f"https://rupload.facebook.com/video-upload/v23.0/{video}", method="POST",
                                     headers={"Authorization": f"OAuth {token}", "file_url": url})
    try:
        with urllib.request.urlopen(zahtjev, timeout=300) as odgovor:
            json.loads(odgovor.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"FB reels upload: {e.read().decode(errors='replace')}") from None
    api("facebook", f"{stranica}/video_reels", token,
        {"upload_phase": "finish", "video_id": video, "video_state": "PUBLISHED", "description": tekst})
    return video


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
    if je_video(ime) and "is_carousel_item" in dodatno:
        podaci = {"media_type": "VIDEO", "video_url": javni_url(folder, ime)}
    elif je_video(ime):
        podaci = {"media_type": "REELS", "video_url": javni_url(folder, ime), "share_to_feed": "true"}
        # Naslovna slika: cover.jpg iz foldera objave, inače kadar na 1,5 s (ne crni prvi kadar).
        if (folder / "cover.jpg").exists():
            podaci["cover_url"] = javni_url(folder, "cover.jpg")
        else:
            podaci["thumb_offset"] = "1500"
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
    # Instagram zna odbiti s "media is not ready" (2207027), a ponekad ipak objavi. Zato prije
    # svakog ponovnog pokušaja provjeri je li kontejner već objavljen, da ne nastane duplikat.
    for pokusaj in range(6):
        try:
            return api(baza, f"{ig}/media_publish", token, {"creation_id": kontejner}).get("id")
        except RuntimeError as e:
            if "2207027" not in str(e) or pokusaj == 5:
                raise
            print(f"  IG medij nije spreman, pokušaj {pokusaj + 2} za 20 s...")
            time.sleep(20)
            status = api(baza, kontejner, token, {"fields": "status_code"}, metoda="GET").get("status_code")
            if status == "PUBLISHED":
                print("  IG je objavu ipak primio, ne šaljem ponovo.")
                zadnja = api(baza, f"{ig}/media", token, {"fields": "id", "limit": "1"}, metoda="GET")
                return (zadnja.get("data") or [{}])[0].get("id", f"kontejner {kontejner}")


def token_za(nalog, mreza):
    # IG može imati poseban token (Instagram Login) kad nije vezan za FB stranicu.
    ime_tokena = nalog.get("ig_token_env", nalog["token_env"]) if mreza == "ig" else nalog["token_env"]
    token = os.environ.get(ime_tokena)
    if not token:
        raise RuntimeError(f"Nema tokena {ime_tokena}.")
    return token


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
        token = token_za(nalog, mreza)
        funkcija = objavi_fb if mreza == "fb" else objavi_ig
        rezultat[mreza] = funkcija(nalog, token, objava, folder)
        print(f"  {biznis}: {folder.name} objavljeno na {mreza} (id {rezultat[mreza]})")


def sacuvaj(putanja, objava):
    putanja.write_text(json.dumps(objava, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def zakazano_vrijeme(objava):
    return datetime.fromisoformat(f"{objava['datum']}T{objava['vrijeme']}")


def obradi(putanja, sad, proba, odmah=False):
    objava = json.loads(putanja.read_text(encoding="utf-8"))
    if objava.get("status") != "odobreno":
        return
    biznis = putanja.parent.parent.parent.name
    zakazano = zakazano_vrijeme(objava)
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


def postoji(mreza, nalog, token, id_objave, tekst):
    """Da li je objava i dalje na profilu. Greška koja nije "ne postoji" (npr. token) ide dalje."""
    baza = "facebook" if mreza == "fb" else nalog.get("ig_api", nalog["api"])
    try:
        api(baza, id_objave, token, {"fields": "id"}, metoda="GET")
        return True
    except RuntimeError as e:
        if '"code":100' not in str(e):
            raise
    if mreza == "ig":
        # Instagram ponekad vrati drugi id nego što objava ima; potraži istu objavu po tekstu.
        zadnje = api(baza, f"{nalog['ig_id']}/media", token, {"fields": "caption", "limit": "5"}, metoda="GET")
        return any((m.get("caption") or "").strip() == tekst.strip() for m in zadnje.get("data", []))
    return False


def provjeri(putanja, sad):
    """10 min nakon objave provjeri da je objava stvarno na profilu; ako nije, objavi ponovo (jednom)."""
    objava = json.loads(putanja.read_text(encoding="utf-8"))
    if objava.get("status") != "objavljeno" or objava.get("provjereno") or not objava.get("objavljeno_u"):
        return
    proslo = sad - datetime.fromisoformat(objava["objavljeno_u"])
    if not PROVJERA_NAKON <= proslo <= PROVJERA_DO:
        return
    biznis, ime = putanja.parent.parent.parent.name, putanja.parent.name
    nalog = NALOZI[biznis]
    nema = []
    for mreza, id_objave in objava.get("rezultat", {}).items():
        tekst = objava.get(f"tekst_{mreza}") or objava.get("tekst_fb") or objava.get("tekst_ig", "")
        try:
            if not postoji(mreza, nalog, token_za(nalog, mreza), id_objave, tekst):
                nema.append(mreza)
        except Exception as e:  # noqa: BLE001 - ne znamo stanje, pokušaj u sljedećem krugu
            print(f"  {biznis}: {ime} provjera na {mreza} nije uspjela ({e}), pokušavam kasnije.")
            return
    if not nema:
        print(f"  {biznis}: {ime} provjereno, objava je na profilu ({', '.join(objava.get('rezultat', {}))}).")
        objava["provjereno"] = sad.isoformat(timespec="minutes")
    elif objava.get("ponovljeno"):
        print(f"  {biznis}: {ime} i dalje nije na {', '.join(nema)} ni nakon ponovne objave.")
        objava["provjereno"] = sad.isoformat(timespec="minutes")
        objava["greska"] = f"Objava nije vidljiva na {', '.join(nema)} ni nakon ponovne objave."
    else:
        print(f"  {biznis}: {ime} NIJE na {', '.join(nema)}, objavljujem ponovo.")
        for mreza in nema:
            objava["rezultat"].pop(mreza)
        objava["ponovljeno"] = nema
        try:
            objavi(biznis, putanja.parent, objava, False)
            objava["objavljeno_u"] = sad.isoformat(timespec="minutes")  # nova provjera za 10 min
        except Exception as e:  # noqa: BLE001
            print(f"  {biznis}: {ime} GREŠKA pri ponovnoj objavi: {e}")
            objava["greska"] = str(e)
            objava["status"] = "greska"
    sacuvaj(putanja, objava)


def sljedeci_dogadjaj(putanje, sad, granica):
    """Najbliže vrijeme (do granice) kad je neka objava na redu za objavu ili provjeru."""
    vremena = []
    for p in putanje:
        o = json.loads(p.read_text(encoding="utf-8"))
        if o.get("status") == "odobreno":
            vremena.append(zakazano_vrijeme(o))
        elif o.get("status") == "objavljeno" and not o.get("provjereno") and o.get("objavljeno_u"):
            vremena.append(datetime.fromisoformat(o["objavljeno_u"]) + PROVJERA_NAKON)
    return min((v for v in vremena if sad < v <= granica), default=None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proba", action="store_true", help="ništa ne šalje, samo ispisuje")
    parser.add_argument("--sad", help="objavi odmah ovu objavu (put do foldera ili objava.json)")
    parser.add_argument("--cekaj", type=int, default=0, metavar="MIN",
                        help="ako je odobrena objava na redu u narednih MIN minuta, sačekaj je "
                             "(GitHub zna kasniti s pokretanjem, pa se pokrećemo ranije)")
    args = parser.parse_args()
    sad = sarajevo_sad()
    print(f"Vrijeme (Sarajevo): {sad:%Y-%m-%d %H:%M}")
    if args.sad:
        putanja = Path(args.sad).resolve()
        obradi(putanja if putanja.suffix == ".json" else putanja / "objava.json", sad, args.proba, odmah=True)
        return
    putanje = sorted(BIZNISI.glob("*/red/*/objava.json"))
    def krug(sad):
        for putanja in putanje:
            obradi(putanja, sad, args.proba)
            if not args.proba:
                provjeri(putanja, sad)

    krug(sad)
    if args.cekaj and not args.proba:
        granica = sad + timedelta(minutes=args.cekaj)
        while vrijeme := sljedeci_dogadjaj(putanje, sarajevo_sad(), granica):
            pauza = (vrijeme - sarajevo_sad()).total_seconds()
            print(f"Čekam do {vrijeme:%H:%M} (objava ili provjera, {int(pauza // 60)} min)...", flush=True)
            time.sleep(max(pauza, 0) + 5)
            krug(sarajevo_sad())


if __name__ == "__main__":
    sys.exit(main())
