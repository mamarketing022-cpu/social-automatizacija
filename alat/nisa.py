"""Prati uspješne tuđe Instagram naloge iz niše biznisa i piše biznisi/<biznis>/trendovi/nisa.md.

Nalozi koje pratimo su u biznisi/<biznis>/trendovi/uzori.txt (jedno korisničko ime po redu,
# za komentar). Moraju biti Business ili Creator nalozi. Za svaki nalog uzima zadnjih 25
objava preko Instagram Business Discovery i traži objave koje su prošle mnogo bolje od
uobičajenog za taj nalog ("iskakanje" = angažman objave / medijan naloga). To su trendovi:
format, hook (prvi red teksta), hashtagovi.

Pokretanje:
    python alat/nisa.py              # svi biznisi koji imaju uzori.txt
    python alat/nisa.py natasa       # samo jedan

Token: TREND_TOKEN u .env – Facebook USER token s dozvolama instagram_basic,
instagram_manage_insights, pages_read_engagement (Page tokeni ne rade). Traje 60 dana.
"""

import os
import re
import statistics
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from objavi import BIZNISI, NALOZI, api, sarajevo_sad  # noqa: E402
from rezultati import aktivan, ucitaj_env  # noqa: E402

# Upit ide s našeg IG naloga povezanog s FB stranicom (MA Marketing).
IG_UPITNIK = NALOZI["ma-marketing"]["ig_id"]
DANA = 30
POLJA = ("business_discovery.username({ime}){{username,followers_count,"
         "media.limit(25){{caption,media_type,media_product_type,like_count,comments_count,"
         "view_count,timestamp,permalink}}}}")


def uzori(biznis):
    fajl = BIZNISI / biznis / "trendovi" / "uzori.txt"
    if not fajl.exists():
        return []
    return [red.split("#")[0].strip().lstrip("@") for red in fajl.read_text(encoding="utf-8").splitlines()
            if red.split("#")[0].strip()]


def angazman(objava):
    return objava.get("like_count", 0) + 3 * objava.get("comments_count", 0)


def nalog(ime, token):
    podaci = api("facebook", IG_UPITNIK, token, {"fields": POLJA.format(ime=ime)}, metoda="GET")
    return podaci["business_discovery"]


def prikupi(biznis, token):
    granica = datetime.now(timezone.utc) - timedelta(days=DANA)
    objave, pregled = [], []
    for ime in uzori(biznis):
        try:
            podaci = nalog(ime, token)
        except RuntimeError as e:
            pregled.append(f"- @{ime}: nije dostupan ({'nije Business/Creator ili ne postoji' if 'Invalid user' in str(e) or '110' in str(e) else str(e)[:80]})")
            continue
        sve = podaci.get("media", {}).get("data", [])
        medijan = statistics.median([angazman(o) for o in sve]) if sve else 0
        nove = [o for o in sve if datetime.strptime(o["timestamp"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc) >= granica]
        pregled.append(f"- @{ime}: {podaci.get('followers_count', '?')} pratilaca, {len(nove)} objava u {DANA} dana, medijan {medijan:g}")
        for o in nove:
            o["nalog"] = ime
            o["iskakanje"] = round(angazman(o) / max(medijan, 1), 1)
            objave.append(o)
    return objave, pregled


def izvjestaj(biznis, objave, pregled):
    def format_(o):
        return {"REELS": "reels", "FEED": {"CAROUSEL_ALBUM": "karusel"}.get(o.get("media_type"), "slika")}.get(
            o.get("media_product_type"), o.get("media_type", "?").lower())

    najbolje = sorted(objave, key=lambda o: -o["iskakanje"])[:15]
    tekst = [f"# Trendovi u niši – {biznis}", "",
             f"Ažurirano: {sarajevo_sad():%d.%m.%Y. %H:%M}. Zadnjih {DANA} dana, nalozi iz `uzori.txt`.",
             "Iskakanje = angažman objave / uobičajeni (medijan) angažman tog naloga; 3× znači 3 puta bolje od njihovog prosjeka.",
             "", "## Praćeni nalozi", ""] + pregled
    tekst += ["", "## Koji format iskače", ""]
    for f in sorted({format_(o) for o in objave}):
        lista = [o["iskakanje"] for o in objave if format_(o) == f]
        tekst.append(f"- {f}: prosječno iskakanje {round(sum(lista) / len(lista), 1)}× ({len(lista)} objava)")
    oznake = Counter(h.lower() for o in najbolje for h in re.findall(r"#\w+", o.get("caption", "")))
    tekst += ["", "## Hashtagovi u najboljim objavama", "",
              ", ".join(f"{h} ({n})" for h, n in oznake.most_common(15)) or "–"]
    tekst += ["", "## Objave koje su najviše iskočile (ideje, ne kopirati)", "",
              "| Iskakanje | Nalog | Format | ♥ | 💬 | Pregledi | Hook (prvi red) | Link |", "|---|---|---|---|---|---|---|---|"]
    for o in najbolje:
        hook = (o.get("caption") or "").strip().split("\n")[0][:80].replace("|", "/")
        tekst.append(f"| {o['iskakanje']}× | @{o['nalog']} | {format_(o)} | {o.get('like_count', 0)} | "
                     f"{o.get('comments_count', 0)} | {o.get('view_count', '–')} | {hook} | [otvori]({o['permalink']}) |")
    (BIZNISI / biznis / "trendovi" / "nisa.md").write_text("\n".join(tekst) + "\n", encoding="utf-8")
    return najbolje


def main():
    ucitaj_env()
    token = os.environ.get("TREND_TOKEN")
    if not token:
        sys.exit("Nema TREND_TOKEN u .env (Facebook user token s instagram_manage_insights).")
    biznisi = sys.argv[1:] or [b for b in NALOZI if not b.startswith("_") and aktivan(b) and uzori(b)]
    for biznis in biznisi:
        objave, pregled = prikupi(biznis, token)
        najbolje = izvjestaj(biznis, objave, pregled)
        print(f"{biznis}: {len(pregled)} naloga, {len(objave)} objava"
              + (f", najviše iskočila @{najbolje[0]['nalog']} {najbolje[0]['iskakanje']}×" if najbolje else ""))


if __name__ == "__main__":
    main()
