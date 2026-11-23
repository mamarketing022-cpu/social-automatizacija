"""Automatski odgovor na komentar "KATALOG" (FB i IG).

Za svaki biznis koji ima biznisi/<biznis>/katalog/postavke.json:
pregleda komentare na objavama iz zadnjih dana i na svaki novi komentar s ključnom
riječi (npr. "katalog", "Katalog!", "KATALOG molim"):
  1. javno odgovori ispod komentara jednom od verzija iz postavki
     (verzije se vrte izmiješano, sve dođu na red i nikad ista dvaput zaredom);
  2. ako je u postavkama uključena "privatna_poruka", pošalje katalog u inbox
     (Meta Private Replies; traži odobrene dozvole pages_messaging / instagram_manage_messages).
Obrađene komentare pamti u katalog/stanje.json (samo ID komentara, bez imena i teksta,
jer je repozitorij javan). Prije odgovora još provjeri da stranica nije već odgovorila,
pa isti komentar nikad ne dobije dva odgovora.

Pokretanje:
    python alat/katalog.py                      # jedan krug za sve biznise
    python alat/katalog.py zlatarna-korzo       # samo taj biznis
    python alat/katalog.py --proba              # ništa ne šalje, samo ispiše šta bi uradio
    python alat/katalog.py --minuta 9 --pauza 60  # krug svake minute, 9 minuta (GitHub Actions)

Token: TOKEN_<BIZNIS> (token FB stranice) iz alat/nalozi.json, kao za objave.
"""

import argparse
import json
import os
import random
import re
import sys
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from objavi import BIZNISI, KORIJEN, NALOZI, api  # noqa: E402

PAMTI_DANA = 30          # koliko dugo se čuvaju ID-jevi obrađenih komentara
NAJVISE_POKUSAJA = 3     # odgovor koji ne uspije pokušava se još nekoliko puta, pa odustaje
PRIVATNA_ROK = timedelta(days=7)  # Meta dozvoljava privatni odgovor samo 7 dana od komentara


# ---------- vrijeme ----------

def utc_sad():
    return datetime.now(timezone.utc)


def u_sarajevo(utc):
    """UTC -> lokalno vrijeme u Sarajevu (CET/CEST), bez zavisnosti od tzdata."""
    def zadnja_nedjelja(godina, mjesec):
        d = datetime(godina, mjesec + 1, 1, 1, tzinfo=timezone.utc) - timedelta(days=1)
        return d - timedelta(days=(d.weekday() + 1) % 7)
    ljeto = zadnja_nedjelja(utc.year, 3) <= utc < zadnja_nedjelja(utc.year, 10)
    return (utc + timedelta(hours=2 if ljeto else 1)).replace(tzinfo=None)


def iz_api_vremena(tekst):
    # Graph API: "2026-11-26T18:03:11+0000"
    return datetime.strptime(tekst, "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)


def lokalno(tekst):
    return datetime.strptime(tekst, "%Y-%m-%d %H:%M") if tekst else None


# ---------- ključne riječi ----------

def bez_kvacica(tekst):
    tekst = tekst.replace("đ", "dj").replace("Đ", "Dj")
    return "".join(z for z in unicodedata.normalize("NFKD", tekst) if not unicodedata.combining(z)).lower()


def sadrzi_kljucnu(tekst, kljucne):
    """Riječ koja POČINJE ključnom riječi: katalog, KATALOG!, kataloga, katalogg; ne 'prekatalog'."""
    tekst = bez_kvacica(tekst or "")
    return any(re.search(rf"(?<![a-z0-9]){re.escape(bez_kvacica(k))}", tekst) for k in kljucne)


# ---------- rotacija verzija ----------

def sljedeca_verzija(stanje, broj_verzija):
    """Izmiješan red svih verzija; kad se potroši, novi red (ne počinje onom koja je bila zadnja)."""
    red = [i for i in stanje.get("red_verzija", []) if i < broj_verzija]
    if not red:
        red = list(range(broj_verzija))
        random.shuffle(red)
        if broj_verzija > 1 and red[0] == stanje.get("zadnja_verzija"):
            red.append(red.pop(0))
    izbor = red.pop(0)
    stanje["red_verzija"] = red
    stanje["zadnja_verzija"] = izbor
    return izbor


# ---------- stanje ----------

def ucitaj(putanja, zadano):
    return json.loads(putanja.read_text(encoding="utf-8")) if putanja.exists() else zadano


def sacuvaj(putanja, podaci):
    putanja.write_text(json.dumps(podaci, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ocisti_staro(stanje, sad):
    granica = (sad - timedelta(days=PAMTI_DANA)).isoformat()
    stanje["obradjeno"] = {k: v for k, v in stanje.get("obradjeno", {}).items() if v.get("vrijeme", "") >= granica}


# ---------- Graph API ----------

def stranice(putanja, token, parametri, najvise=10):
    """GET s listanjem kroz 'paging.next' (najviše nekoliko stranica)."""
    parametri = dict(parametri)
    for _ in range(najvise):
        odgovor = api("facebook", putanja, token, parametri, metoda="GET")
        yield from odgovor.get("data", [])
        sljedeca = odgovor.get("paging", {}).get("cursors", {}).get("after")
        if not sljedeca or not odgovor.get("paging", {}).get("next"):
            return
        parametri["after"] = sljedeca


def fb_komentari(nalog, token, od_utc):
    stranica = nalog["page_id"]
    # Reklame su boost postojećih objava, pa su njihovi komentari na istim objavama.
    objave = []
    for o in stranice(f"{stranica}/published_posts", token, {"fields": "id,created_time", "limit": "50"}, najvise=3):
        if iz_api_vremena(o["created_time"]) < od_utc:
            break
        objave.append(o["id"])
    for id_objave in objave:
        for k in stranice(f"{id_objave}/comments", token,
                          {"fields": "id,message,created_time,from{id}", "filter": "toplevel",
                           "order": "reverse_chronological", "limit": "100"}):
            vrijeme = iz_api_vremena(k["created_time"])
            if vrijeme < od_utc:
                break
            if (k.get("from") or {}).get("id") == stranica:
                continue  # komentar same stranice
            yield {"id": k["id"], "tekst": k.get("message", ""), "vrijeme": vrijeme, "mreza": "fb"}


def ig_komentari(nalog, token, od_utc, svoje_ime):
    for m in stranice(f"{nalog['ig_id']}/media", token, {"fields": "id,timestamp", "limit": "50"}, najvise=3):
        if iz_api_vremena(m["timestamp"]) < od_utc:
            break
        for k in stranice(f"{m['id']}/comments", token, {"fields": "id,text,timestamp,username", "limit": "50"}):
            vrijeme = iz_api_vremena(k["timestamp"])
            if vrijeme < od_utc or k.get("username") == svoje_ime:
                continue
            yield {"id": k["id"], "tekst": k.get("text", ""), "vrijeme": vrijeme, "mreza": "ig"}


def vec_odgovoreno(nalog, token, komentar, svoje_ime):
    """Sigurnosna provjera: je li stranica već odgovorila na ovaj komentar (npr. stanje se nije sačuvalo)."""
    if komentar["mreza"] == "fb":
        odgovori = api("facebook", f"{komentar['id']}/comments", token, {"fields": "from{id}", "limit": "50"}, metoda="GET")
        return any((o.get("from") or {}).get("id") == nalog["page_id"] for o in odgovori.get("data", []))
    odgovori = api("facebook", f"{komentar['id']}/replies", token, {"fields": "username", "limit": "50"}, metoda="GET")
    return any(o.get("username") == svoje_ime for o in odgovori.get("data", []))


def javno_odgovori(token, komentar, tekst):
    putanja = f"{komentar['id']}/comments" if komentar["mreza"] == "fb" else f"{komentar['id']}/replies"
    return api("facebook", putanja, token, {"message": tekst}).get("id")


def privatno_posalji(nalog, token, komentar, tekst):
    # Private Replies: i za FB i za IG (preko Facebook Login) ide na /{page_id}/messages.
    return api("facebook", f"{nalog['page_id']}/messages", token, {
        "recipient": json.dumps({"comment_id": komentar["id"]}),
        "message": json.dumps({"text": tekst}, ensure_ascii=False),
    }).get("message_id")


# ---------- glavni krug ----------

def obradi_biznis(biznis, proba):
    """Vraća None ako automatika za biznis sada ne radi (isključena, van termina, nema tokena)."""
    folder = BIZNISI / biznis / "katalog"
    postavke = ucitaj(folder / "postavke.json", None)
    if not postavke or not postavke.get("ukljuceno", True):
        return None
    nalog = NALOZI.get(biznis)
    if not nalog:
        print(f"  ! {biznis}: nema ga u alat/nalozi.json")
        return None
    token = os.environ.get(nalog["token_env"])
    if not token:
        print(f"  ! {biznis}: nema tokena {nalog['token_env']} (preskačem)")
        return None

    sad = utc_sad()
    sad_lokalno = u_sarajevo(sad)
    pocetak, kraj = lokalno(postavke.get("aktivno_od")), lokalno(postavke.get("aktivno_do"))
    if (pocetak and sad_lokalno < pocetak) or (kraj and sad_lokalno > kraj):
        print(f"  {biznis}: automatika nije aktivna sada ({postavke.get('aktivno_od')} – {postavke.get('aktivno_do') or 'bez kraja'})")
        return None

    od_utc = sad - timedelta(days=postavke.get("dana_unazad", 14))
    kljucne = postavke["kljucne_rijeci"]
    verzije = postavke["javni_odgovori"]
    privatna = postavke.get("privatna_poruka", {})
    mreze = [m for m in postavke.get("mreze", ["fb", "ig"]) if m in nalog["mreze"]]

    stanje_put = folder / "stanje.json"
    stanje = ucitaj(stanje_put, {"obradjeno": {}})
    ocisti_staro(stanje, sad)
    obradjeno = stanje["obradjeno"]
    promjena = False

    svoje_ime = None
    if "ig" in mreze:
        svoje_ime = api("facebook", nalog["ig_id"], token, {"fields": "username"}, metoda="GET").get("username")

    komentari = []
    for mreza in mreze:
        try:
            komentari += list(fb_komentari(nalog, token, od_utc) if mreza == "fb"
                              else ig_komentari(nalog, token, od_utc, svoje_ime))
        except RuntimeError as e:
            print(f"  ! {biznis} {mreza}: ne mogu čitati komentare: {str(e)[:300]}")

    for k in sorted(komentari, key=lambda x: x["vrijeme"]):
        zapis = obradjeno.get(k["id"], {})
        if zapis.get("gotovo"):
            continue
        if pocetak and u_sarajevo(k["vrijeme"]) < pocetak:
            continue  # komentar prije početka akcije
        if not sadrzi_kljucnu(k["tekst"], kljucne):
            continue

        if proba:
            print(f"  [proba] {biznis} {k['mreza']} komentar {k['id']}: odgovorio bih")
            continue

        try:
            if vec_odgovoreno(nalog, token, k, svoje_ime):
                obradjeno[k["id"]] = {"vrijeme": sad.isoformat(), "mreza": k["mreza"], "gotovo": True,
                                      "javno": "već odgovoreno"}
                promjena = True
                continue
        except RuntimeError as e:
            print(f"    ! provjera odgovora za {k['id']} nije uspjela: {str(e)[:200]}")

        zapis.update({"vrijeme": sad.isoformat(), "mreza": k["mreza"]})
        promjena = True

        if privatna.get("ukljuceno") and not zapis.get("dm") and sad - k["vrijeme"] < PRIVATNA_ROK:
            try:
                privatno_posalji(nalog, token, k, privatna["tekst"].replace("{link}", privatna.get("link", "")))
                zapis["dm"] = "poslano"
                print(f"  {biznis} {k['mreza']} {k['id']}: katalog poslan u inbox")
            except RuntimeError as e:
                zapis["dm_greska"] = str(e)[:300]
                print(f"    ! privatna poruka za {k['id']} nije poslana: {str(e)[:300]}")

        verzija = sljedeca_verzija(stanje, len(verzije))
        try:
            javno_odgovori(token, k, verzije[verzija])
            zapis.update({"javno": "poslano", "verzija": verzija + 1, "gotovo": True})
            zapis.pop("greska", None)
            print(f"  {biznis} {k['mreza']} {k['id']}: javni odgovor (verzija {verzija + 1})")
        except RuntimeError as e:
            stanje["red_verzija"] = [verzija] + stanje.get("red_verzija", [])  # verzija nije potrošena
            zapis["pokusaja"] = zapis.get("pokusaja", 0) + 1
            zapis["greska"] = str(e)[:300]
            if zapis["pokusaja"] >= NAJVISE_POKUSAJA:
                zapis["gotovo"] = True
            print(f"    ! javni odgovor za {k['id']} nije uspio ({zapis['pokusaja']}. put): {str(e)[:300]}")
        obradjeno[k["id"]] = zapis

    if promjena and not proba:
        sacuvaj(stanje_put, stanje)
    return promjena


def ucitaj_env():
    """Lokalno pokretanje: tokeni iz .env (na GitHubu dolaze iz Secrets)."""
    env = KORIJEN / ".env"
    if env.exists():
        for red in env.read_text(encoding="utf-8").splitlines():
            if "=" in red and not red.startswith("#"):
                kljuc, vrijednost = red.split("=", 1)
                os.environ.setdefault(kljuc.strip(), vrijednost.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("biznisi", nargs="*")
    parser.add_argument("--proba", action="store_true", help="ništa ne šalje, samo ispisuje")
    parser.add_argument("--minuta", type=int, default=0, help="ponavljaj krugove ovoliko minuta")
    parser.add_argument("--pauza", type=int, default=60, help="sekundi između krugova")
    args = parser.parse_args()
    ucitaj_env()
    biznisi = args.biznisi or sorted(p.parent.parent.name for p in BIZNISI.glob("*/katalog/postavke.json"))

    kraj = time.monotonic() + args.minuta * 60
    while True:
        print(f"Krug {u_sarajevo(utc_sad()):%Y-%m-%d %H:%M:%S} (Sarajevo)", flush=True)
        aktivnih = 0
        for biznis in biznisi:
            try:
                aktivnih += obradi_biznis(biznis, args.proba) is not None
            except RuntimeError as e:
                aktivnih += 1  # aktivan, samo je API zakazao; pokušaj opet u idućem krugu
                print(f"  ! {biznis}: {str(e)[:300]}")
        if not aktivnih:
            print("Nijedna katalog automatika sada nije aktivna, kraj.")
            break
        if time.monotonic() + args.pauza >= kraj:
            break
        time.sleep(args.pauza)


if __name__ == "__main__":
    main()
