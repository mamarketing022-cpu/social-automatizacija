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
    kolaz("m1", [("x_ciklama.jpg", "55% 45%"), ("x_zvijezda.jpg", "50% 55%"), ("x_srce_dupli.jpg", "50% 60%"), ("x_kap.jpg", "60% 50%")],
          "Pokloni do 60 KM", "Srebrni lančići · Tuzla")
    slajd("m2", "x_ciklama.jpg", 1, 5, "Ciklama", "Srebrni lančić · ciklama privjesak", "39 KM", False, "center 35%")
    slajd("m3", "x_plavi.jpg", 2, 5, "Tamnoplavi", "Srebrni lančić · plavi privjesak", "32 KM", False, "center 35%")
    slajd("m4", "x_zvijezda.jpg", 3, 5, "Zvijezda", "Srebrni lančić Zvijezda", "39 KM", False, "center 30%")
    slajd("m5", "x_srce_dupli.jpg", 4, 5, "Dupli sa srcem", "Srebrni dupli lančić sa srcem", "53 KM", False, "center 30%")
    slajd("m6", "x_kap.jpg", 5, 5, "Kap", "Srebrni lančić Kap", "59 KM", False, "center 30%")
    cta("m7", "Koji je vaš?", INFO, "Napišite broj u komentar, ili sačuvajte listu za poklon.")
if cmd == "pet":
    kolaz("t1", [("x_r_plava.jpg", "40% 60%"), ("x_r_baget.jpg", "50% 60%"), ("x_r_krugovi.jpg", "55% 55%")],
          "Tri prstena, tri stila", "Srebrno prstenje do 45 KM · Tuzla")
    slajd("t2", "x_r_plava.jpg", 1, 3, "Tri plava srca", "Srebrni prsten", "27 KM", True, "center bottom")
    slajd("t3", "x_r_baget.jpg", 2, 3, "Baget cirkon", "Srebrni prsten s pozlatom", "44 KM", True, "center bottom")
    slajd("t4", "x_r_krugovi.jpg", 3, 3, "Cirkonski krugovi", "Srebrni prsten", "36 KM", True, "center bottom")
    cta("t5", "Koji stil ste vi?", INFO, "Napišite 1, 2 ili 3 u komentar. Veličinu prilagođavamo u radnji.")
