# Social Automatizacija

Automatsko pravljenje i zakazivanje objava za Facebook i Instagram, za više biznisa.
Svaki biznis ima svoj chat (sesiju) i svoj folder u `biznisi/`.

## Pravila rasporeda (važe za sve biznise, osim ako profil biznisa kaže drugačije)

- **Ponedjeljak** – vizual (post: slika ili karusel)
- **Srijeda** – video (reels)
- **Petak** – vizual (post: slika ili karusel)
- Objava ide na **FB i IG** istovremeno, s tekstom prilagođenim svakoj mreži.
- Vrijeme objave: iz profila biznisa (`vrijeme_objave`), zadano 18:00 (Europe/Sarajevo).

## Kako radi

1. Sadržaj se pravi unaprijed za cijelu sedmicu (ili čim stignu materijali).
2. Ako je korisnik poslao slike/materijale, koristiti **njih** (urediti ih, napraviti vizual ili video).
   Ako nema materijala, napraviti sadržaj iz `profil.md` i `materijali/` biznisa.
3. Svaka objava ide u `biznisi/<biznis>/red/` kao folder `GGGG-MM-DD_tip/` sa:
   - medij (`.jpg`/`.png` ili `.mp4`, reels 9:16 1080x1920, post 4:5 1080x1350)
   - `objava.json` (tekst FB, tekst IG, hashtagovi, vrijeme, status)
4. Korisnik pregleda svaku objavu prije objavljivanja (status ide `nacrt` → `odobreno` → `objavljeno`).
   - Nova objava uvijek ima status `nacrt`; poslati korisniku pregled (medij + tekst).
   - Tek kad korisnik odobri ("odobreno", "može", "ok"), status postaje `odobreno`.
   - Ako traži izmjene, ispraviti i ponovo poslati pregled; status ostaje `nacrt`.
5. Alat za objavu (`alat/`) objavljuje u zakazano vrijeme **samo** objave sa statusom `odobreno`
   i mijenja status u `objavljeno`. Neodobrena objava se ne objavljuje; korisnika podsjetiti.

## Izmjene od korisnika – imaju prednost

- "Ovo ide danas" / "umjesto toga" → zamijeniti zakazanu objavu za taj dan novom.
  Staru ne brisati, nego prebaciti u `biznisi/<biznis>/arhiva/` sa statusom `zamijenjeno`.
- Korisnik uvijek ima zadnju riječ; njegova uputa važi i za buduće objave ako tako kaže,
  i tada je zapisati u `profil.md` tog biznisa.

## Rad u chatu biznisa (svaki biznis ima svoju sesiju)

- Radi SAMO u folderu svog biznisa (`biznisi/<biznis>/`). Ne diraj tuđe foldere, `alat/` ni `.github/`
  (to se mijenja iz glavnog chata).
- Pregled za odobrenje: pošalji korisniku medij (SendUserFile) + tekst FB i IG u poruci.
- Kad korisnik odobri: status `odobreno`, pa `git add biznisi/<biznis>` + commit + `git pull --rebase` + `git push`.
  Bez push-a GitHub ne vidi objavu i neće je objaviti.
- Ako korisnik kaže "objavi odmah": učitaj `.env` u okruženje, postavi
  `MEDIA_BASE_URL=https://raw.githubusercontent.com/mamarketing022-cpu/social-automatizacija/main`,
  prvo push-aj medij, pa `python alat/objavi.py --sad biznisi/<biznis>/red/<folder>`, pa push statusa.
- Materijali koje korisnik pošalje idu u `biznisi/<biznis>/materijali/` (originali, ne mijenjati ih).
- Alati za medije: Python + Pillow (vizuali), ffmpeg (reels od slika/videa, 1080x1920, 15–30 s),
  fontovi iz C:/Windows/Fonts. Uvijek pogledaj gotov vizual (Read) prije slanja korisniku.
- Bez materijala: možeš koristiti vlastite starije fotografije biznisa s njihovog IG-a
  (Graph API `/{ig_id}/media?fields=media_url,media_type,caption`, token iz `.env`) kao podlogu za novi dizajn,
  ali ne objavljuj istu sliku ponovo bez obrade.

## Pravila sadržaja

- Jezik i ton iz profila biznisa. Bez izmišljenih cijena, akcija, rokova ili tvrdnji
  koje nisu u profilu ili materijalima.
- Muzika u reelsima samo bez autorskih prava (API ne može koristiti Instagram muzičku biblioteku).
- Logo, boje i fontovi iz `biznisi/<biznis>/brend/`.
