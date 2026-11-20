import sys
cmd = sys.argv[1]
sys.argv = ["gen", "x"]
from gen import render

FADE_B = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.5) 0%,rgba(8,7,6,0) 16%,rgba(8,7,6,0) 58%,rgba(8,7,6,.94) 80%,rgba(8,7,6,1) 100%)"></div>'
FADE_T = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.94) 0%,rgba(8,7,6,.76) 26%,rgba(8,7,6,0) 46%,rgba(8,7,6,0) 88%,rgba(8,7,6,.45) 100%)"></div>'
LOGO = '<div class=logo style="left:44px;top:36px;width:190px;height:84px;background-position:left"></div>'
CIJENA = 'display:inline-block;border:1.5px solid #d8b26c;border-radius:40px;padding:8px 26px;font-family:Manrope,sans-serif;font-weight:600;font-size:34px;color:#f3dca4;letter-spacing:.04em'
INFO = ["Prekinute mladosti 8, Tuzla", "Certifikat uz svaki komad", "Dostava u cijeloj BiH · pouzećem"]


def slajd(name, img, n, uk, naslov, opis, cijena, gore=False, pos="center"):
    blok = f'''<div class="serif it"><span class=gold style="font-size:100px">{naslov}</span></div>
      <div class=hair style="margin:22px 0 18px"></div>
      <div class=sans style="font-size:23px;margin-bottom:22px">{opis}</div>
      <div style="{CIJENA}">{cijena}</div>'''
    mjesto = "top:140px" if gore else "bottom:60px"
    render(name, f'''<div class=ph style="background-image:url({img});background-position:{pos}"></div>{FADE_T if gore else FADE_B}{LOGO}
    <div class="a sans" style="right:48px;top:64px;font-size:20px">{n} / {uk}</div>
    <div class=a style="left:64px;right:64px;{mjesto}">{blok}</div>''')


def kolaz(name, slike, naslov, pod):
    w = 1080 // len(slike)
    panels = "".join(f'<div class=a style="left:{i*w}px;top:0;width:{w}px;height:1350px;background:url({s}) {p}/cover;border-right:2px solid #0b0a09"></div>' for i, (s, p) in enumerate(slike))
    render(name, f'''{panels}<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.94) 0%,rgba(8,7,6,.78) 28%,rgba(8,7,6,0) 48%,rgba(8,7,6,0) 82%,rgba(8,7,6,.82) 100%)"></div>
    <div class=logo style="left:0;right:0;top:36px;height:120px"></div>
    <div class="a serif it" style="left:0;right:0;top:185px;text-align:center"><span class=gold style="font-size:{130 if len(naslov) < 16 else 108}px">{naslov}</span></div>
    <div class="a sans" style="left:0;right:0;top:370px;text-align:center;font-size:25px">{pod}</div>
    <div class="a sans" style="left:0;right:0;bottom:44px;text-align:center;font-size:22px;color:#f3dca4">Listajte →</div>''')


def cta(name, naslov, linije, poruka):
    li = "<br>".join(linije)
    render(name, f'''<div class=a style="inset:0;background:radial-gradient(ellipse at 50% 35%,#2a1f12,#0b0a09 70%)"></div>
    <div class=logo style="left:190px;right:190px;top:130px;height:300px"></div>
    <div class="a serif it" style="left:0;right:0;top:500px;text-align:center"><span class=gold style="font-size:92px">{naslov}</span></div>
    <div class=a style="left:110px;right:110px;top:650px;text-align:center"><div class=body style="font-size:35px">{poruka}</div></div>
    <div class=a style="left:0;right:0;top:880px;text-align:center"><div class=sans style="font-size:25px;line-height:2.1">{li}</div></div>
    <div class="a serif it" style="left:0;right:0;bottom:70px;text-align:center"><span class=gold style="font-size:44px">emazlatoisrebro.com</span></div>''')


if cmd == "pon":
    kolaz("n1", [("w_m_pecat2.jpg", "45% 60%"), ("w_m_tigar.jpg", "60% 30%"), ("w_m_zeleni.jpg", "45% 55%"), ("w_sat_hrono.jpg", "75% 40%")],
          "Poklon za njega", "Muško srebrno prstenje i satovi · Tuzla")
    slajd("n2", "w_m_pecat2.jpg", 1, 5, "Pečatnjak", "Srebrni prsten · grčki ornament", "110 KM", True, "center bottom")
    slajd("n3", "w_m_tigar.jpg", 2, 5, "Tigrovo oko", "Muški srebrni prsten", "90 KM", False, "center 30%")
    slajd("n4", "w_m_zeleni.jpg", 3, 5, "Zeleni kamen", "Srebrni prsten · ovalni kamen", "81 KM", True, "center bottom")
    slajd("n5", "w_m_crni.jpg", 4, 5, "Crni kamen", "Srebrni prsten · grčki ornament", "92 KM", False, "center 30%")
    slajd("n6", "w_sat_hrono.jpg", 5, 5, "Hronograf", "Muški sat · crni brojčanik · metalna narukvica", "187 KM", False, "center 25%")
    cta("n7", "Šta biste mu poklonili?", ["Prekinute mladosti 8, Tuzla", "Srebrno prstenje · satovi", "Dostava u cijeloj BiH · pouzećem"], "Napišite broj u komentar, ili pošaljite ovo nekome kome treba ideja za poklon.")
if cmd == "pet":
    kolaz("d1", [("w_dj1.jpg", "35% center"), ("w_dj2.jpg", "60% center"), ("w_dj5.jpg", "45% 70%"), ("w_dj_crna.jpg", "70% center")],
          "Djetelina za sreću", "Srebrne narukvice s pozlatom · Tuzla")
    slajd("d2", "w_dj1.jpg", 1, 4, "Jedna djetelina", "Narukvica s pozlatom · bijeli sedef", "30 KM", False, "center 40%")
    slajd("d3", "w_dj2.jpg", 2, 4, "Dvije djeteline", "Narukvica s pozlatom · bijeli sedef", "65 KM", True, "center bottom")
    slajd("d4", "w_dj5.jpg", 3, 4, "Pet djetelina", "Narukvica s pozlatom · bijeli sedef", "98 KM", True, "center bottom")
    slajd("d5", "w_dj_crna.jpg", 4, 4, "Crna djetelina", "Srebrna narukvica s pozlatom", "33 KM", False, "center 40%")
    cta("d6", "Koja je vaša?", INFO, "Napišite 1, 2, 5 ili crna u komentar. Lijep sitni poklon pred praznike.")
