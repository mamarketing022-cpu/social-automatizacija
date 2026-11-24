# Slanje kataloga za Crni petak u privatne poruke (Zlatarna Korzo)

Zakazani zadatak `korzo-katalog-poruke` ovo radi svaki dan u **9:00 i 19:00**, od 25.11. do 30.11.2026.
Javne odgovore ispod komentara radi GitHub (`alat/katalog.py`), ne ovaj zadatak.

## Fajlovi (lokalno, NE idu na GitHub – folder `privatno/` je u .gitignore)

- PDF: `D:\Social Automatizacija\biznisi\zlatarna-korzo\katalog\privatno\Katalog_Crni_petak_Zlatarna_Korzo.pdf`
- Stranice kao slike (za Instagram, PDF tamo ne prolazi): `...\katalog\privatno\stranice\00.jpg` … `16.jpg` (2,8 MB, sve u jednom slanju)
- Spisak kome je šta poslano: `...\katalog\privatno\poslano.json`

`poslano.json` je lista zapisa:
`{"ime": "Ime Prezime", "kanal": "messenger|instagram|fb_komentar|ig_komentar", "status": "katalog|pozdrav|isteklo|preskoceno", "vrijeme": "2026-11-25 09:12", "napomena": ""}`
- `katalog` = dobio/la katalog (PDF ili slike). Više mu/joj ne slati ništa.
- `pozdrav` = poslana privatna poruka na komentar (bez fajla), čeka da odgovori.
- `isteklo` = Meta više ne dozvoljava poruku (stariji od 7 dana i sl.).
- Ista osoba (isto ime) dobija katalog **samo jednom**, bez obzira na kanal.

## Tok (Claude in Chrome)

0. Ako je sada poslije **30.11.2026. u 17:00** (Sarajevo): ne šalji ništa, javi korisniku da je akcija gotova i da zadatak `korzo-katalog-poruke` može ugasiti.
1. Pročitaj `poslano.json` (ako ne postoji, kreni od prazne liste `[]`).
2. `tabs_context_mcp`, pa novi tab (`tabs_create_mcp`), pa
   `https://business.facebook.com/latest/inbox/all?asset_id=439647812890409` (stranica Zlatarna Korzo Tuzla).
   Ako traži prijavu ili Chrome/ekstenzija nije povezana: stani i javi korisniku. Lozinke nikad ne unositi.
3. **Messenger** tab: svaki razgovor u kojem je kupac napisao nešto s riječju „katalog" (bilo kako napisano),
   a osoba nije `katalog` u spisku:
   - pošalji pozdravnu poruku (jedna od verzija A, ne ista kao prethodnom kupcu),
   - priloži PDF: `find` → file input u composeru razgovora, `file_upload` s putanjom PDF-a, pa pošalji,
   - provjeri na ekranu da se PDF pojavio u razgovoru, upiši `katalog`.
   Ako je osoba u spisku kao `pozdrav` i u međuvremenu je odgovorila: pošalji poruku C + PDF, upiši `katalog`.
4. **Instagram** tab: isto kao Messenger, ali umjesto PDF-a priloži sve slike iz `privatno\stranice\` (00–16).
5. **Facebook comments** tab: za svaku objavu, svaki komentar od 23.11.2026. nadalje s riječju „katalog",
   čija osoba nije u spisku:
   - klikni „Send message" ispod komentara → upiši privatni odgovor (jedna od verzija B) → „Send message",
   - zatim otvori Messenger razgovor s tom osobom i probaj priložiti PDF; ako Meta dozvoli i PDF se vidi → `katalog`,
     ako ne dozvoli → `pozdrav` (PDF ide u nekom od idućih krugova kad osoba odgovori).
   - Ako je „Send message" već iskorišten/siv (već poslano ranije), upiši `pozdrav` i idi dalje.
6. **Instagram comments** tab: isto kao 5, a umjesto PDF-a slike iz `privatno\stranice\`.
7. Između dvije osobe pauza 5–10 s. Verzije poruka vrti, nikad ista dvaput zaredom.
8. `poslano.json` sačuvaj poslije **svake** osobe (da prekid ne izazove dupla slanja).
9. Na kraju zatvori svoj tab i ukratko javi: koliko je dobilo katalog, koliko čeka odgovor (`pozdrav`),
   šta nije uspjelo, i ko je postavio pitanje koje traži čovjeka (cijena drugog artikla, dostava, rezervacija…).

## Nikad

- Ne odgovaraj na pitanja kupaca svojim riječima osim ovih poruka; samo ih navedi u izvještaju.
- Ne šalji ništa ljudima koji katalog nisu tražili, niti dvaput istoj osobi.
- Ne briši, ne skrivaj, ne označavaj kao spam, ne mijenjaj podešavanja, ne klikaj Boost, ne odjavljuj se.
- Ne izmišljaj cijene, popuste ni rokove; sve što treba je u katalogu i ovim porukama.

## Poruke

### A – Messenger / Instagram poruke (prije priloga)
1. Dobar dan! 🖤 Hvala vam na interesovanju za Crni petak u Zlatarni Korzo. U prilogu vam šaljemo katalog: svaki artikal ima redni broj, staru i novu cijenu. Sniženje vrijedi od petka 27.11. do ponedjeljka 30.11. do 17 h, ili do isteka zaliha. Javite nam redni broj artikla koji vam se sviđa i rezervišemo ga za vas ✨
2. Pozdrav i hvala što ste nam se javili! ✨ Šaljemo vam katalog za Crni petak u Zlatarni Korzo. Odabrani komadi zlatnog nakita su sniženi od petka 27.11. do ponedjeljka 30.11. do 17 h, ili do isteka zaliha. Ako vam se nešto svidi, pošaljite nam redni broj i rezervišemo ga za vas 🖤
3. Dobar dan, drago nam je što vas zanima naš katalog! 💛 U nastavku je katalog za Crni petak, sa starom i novom cijenom za svaki artikal. Akcija traje od petka 27.11. do ponedjeljka 30.11. do 17 h. Za rezervaciju nam samo javite redni broj artikla.

### B – privatni odgovor na komentar (samo tekst)
1. Dobar dan! 🖤 Hvala vam što ste komentarisali KATALOG. Pripremili smo katalog za Crni petak u Zlatarni Korzo: odabrani zlatni nakit je snižen od petka 27.11. do ponedjeljka 30.11. do 17 h. Šaljemo vam ga ovdje u poruci, a ako ga ne vidite, samo odgovorite na ovu poruku i odmah stiže ✨
2. Pozdrav iz Zlatarne Korzo! ✨ Hvala na interesovanju za naš katalog za Crni petak. Akcija traje od petka 27.11. do ponedjeljka 30.11. do 17 h. Katalog vam stiže u ovom razgovoru, a ako ga ne vidite, odgovorite nam bilo čime i šaljemo ga odmah 💛
3. Dobar dan, hvala na komentaru! 💛 Katalog za Crni petak u Zlatarni Korzo vam šaljemo ovdje u poruci. Sniženje vrijedi od petka 27.11. do ponedjeljka 30.11. do 17 h. Ako katalog ne stigne, samo odgovorite na ovu poruku 🖤

### C – kad osoba odgovori na privatni odgovor (uz PDF ili slike)
Evo kataloga 🖤 Javite nam redni broj artikla koji vam se sviđa i rezervišemo ga za vas.
