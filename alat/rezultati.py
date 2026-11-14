"""Mjeri kako su prošle naše objave i piše biznisi/<biznis>/trendovi/rezultati.md.

Za svaku objavljenu objavu (status "objavljeno", IG ID u "rezultat") uzima s Instagrama
broj lajkova i komentara, pa rangira objave i tipove (post/karusel/reels)
i posebno pokazuje kako su prošli trend-eksperimenti (polje "trend" u objava.json).
Biznisi označeni "ISKLJUČEN IZ PLANA" u profil.md se preskaču. Facebook brojke se ne
čitaju: za to aplikaciji treba dozvola pages_read_user_content, koju nema.

Pokretanje:
    python alat/rezultati.py              # svi aktivni biznisi
    python alat/rezultati.py natasa       # samo jedan

Tokeni se čitaju iz okruženja ili iz .env (isto ime kao u alat/nalozi.json).
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from objavi import BIZNISI, KORIJEN, NALOZI, api, sarajevo_sad, token_za  # noqa: E402


def ucitaj_env():
    env = KORIJEN / ".env"
    if env.exists():
        for red in env.read_text(encoding="utf-8").splitlines():
            if "=" in red and not red.startswith("#"):
                kljuc, vrijednost = red.split("=", 1)
                os.environ.setdefault(kljuc.strip(), vrijednost.strip())


def aktivan(biznis):
    profil = BIZNISI / biznis / "profil.md"
    return profil.exists() and "ISKLJUČEN IZ PLANA" not in profil.read_text(encoding="utf-8")[:400]


def ig_brojke(nalog, id_objave):
    baza = nalog.get("ig_api", nalog["api"])
    podaci = api(baza, id_objave, token_za(nalog, "ig"), {"fields": "like_count,comments_count"}, metoda="GET")
    return {"ig_lajk": podaci.get("like_count", 0), "ig_kom": podaci.get("comments_count", 0)}


def bodovi(red):
    # Komentar vrijedi više od lajka (jači signal algoritmu).
    return red.get("ig_lajk", 0) + 3 * red.get("ig_kom", 0)


def prikupi(biznis):
    nalog = NALOZI[biznis]
    redovi = []
    for putanja in sorted((BIZNISI / biznis / "red").glob("*/objava.json")):
        objava = json.loads(putanja.read_text(encoding="utf-8"))
        if objava.get("status") != "objavljeno":
            continue
        red = {"folder": putanja.parent.name, "tip": objava.get("tip", "?"),
               "trend": objava.get("trend", ""), "naslov": (objava.get("tekst_ig") or objava.get("tekst_fb") or "").split("\n")[0][:60]}
        id_objave = objava.get("rezultat", {}).get("ig")
        if not id_objave or "ig" not in nalog["mreze"]:
            continue
        try:
            red.update(ig_brojke(nalog, str(id_objave)))
        except RuntimeError:
            continue  # objava obrisana s profila (npr. duplikat)
        red["bodovi"] = bodovi(red)
        redovi.append(red)
    return redovi


def izvjestaj(biznis, redovi):
    def prosjek(lista):
        return round(sum(r["bodovi"] for r in lista) / len(lista), 1) if lista else 0

    sve = prosjek(redovi)
    tekst = [f"# Rezultati objava – {biznis}", "",
             f"Ažurirano: {sarajevo_sad():%d.%m.%Y. %H:%M}. Instagram; bodovi = lajkovi + 3×komentari.",
             f"Prosjek svih objava: **{sve}** bodova ({len(redovi)} objava).", "", "## Po tipu objave", ""]
    for tip in sorted({r["tip"] for r in redovi}):
        lista = [r for r in redovi if r["tip"] == tip]
        tekst.append(f"- {tip}: prosjek {prosjek(lista)} ({len(lista)} objava)")
    eksperimenti = [r for r in redovi if r["trend"]]
    tekst += ["", "## Trend-eksperimenti", ""]
    if eksperimenti:
        for r in eksperimenti:
            ocjena = "BOLJE od prosjeka" if r["bodovi"] > sve else "slabije od prosjeka"
            tekst.append(f"- {r['folder']} – {r['trend']}: {r['bodovi']} bodova ({ocjena})")
    else:
        tekst.append("- još nema (polje \"trend\" u objava.json)")
    tekst += ["", "## Sve objave (najbolje prve)", "",
              "| Objava | Tip | Bodovi | ♥ | 💬 | Trend | Prvi red teksta |",
              "|---|---|---|---|---|---|---|"]
    for r in sorted(redovi, key=lambda r: -r["bodovi"]):
        tekst.append(f"| {r['folder']} | {r['tip']} | {r['bodovi']} | {r['ig_lajk']} | {r['ig_kom']} | {r['trend']} | "
                     f"{r['naslov'].replace('|', '/')} |")
    folder = BIZNISI / biznis / "trendovi"
    folder.mkdir(exist_ok=True)
    (folder / "rezultati.md").write_text("\n".join(tekst) + "\n", encoding="utf-8")
    return sve


def main():
    ucitaj_env()
    biznisi = sys.argv[1:] or [b for b in NALOZI if not b.startswith("_") and aktivan(b)]
    for biznis in biznisi:
        redovi = prikupi(biznis)
        sve = izvjestaj(biznis, redovi)
        najbolja = max(redovi, key=lambda r: r["bodovi"], default=None)
        print(f"{biznis}: {len(redovi)} objava, prosjek {sve}"
              + (f", najbolja {najbolja['folder']} ({najbolja['bodovi']})" if najbolja else ""))


if __name__ == "__main__":
    main()
