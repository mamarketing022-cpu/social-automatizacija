import sys
cmd = sys.argv[1]
sys.argv = ["gen", "x"]
from gen import render, L
import shutil, pathlib

G = pathlib.Path(r"C:/Users/Armin/AppData/Local/Temp/claude/0c29064aaab8358e/49fd4859-e4c4-4441-8191-14ca2cb4a1cd/scratchpad/w5/g")
for f in G.glob("*.jpg"):
    shutil.copy(f, L / f"w5_{f.name}")
FADE_B = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.5) 0%,rgba(8,7,6,0) 16%,rgba(8,7,6,0) 60%,rgba(8,7,6,.94) 82%,rgba(8,7,6,1) 100%)"></div>'
FADE_T = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.94) 0%,rgba(8,7,6,.76) 26%,rgba(8,7,6,0) 46%,rgba(8,7,6,0) 88%,rgba(8,7,6,.45) 100%)"></div>'
LOGO = '<div class=logo style="left:44px;top:36px;width:190px;height:84px;background-position:left"></div>'
CIJENA = 'display:inline-block;border:1.5px solid #d8b26c;border-radius:40px;padding:8px 26px;font-family:Manrope,sans-serif;font-weight:600;font-size:34px;color:#f3dca4;letter-spacing:.04em'


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
    panels = "".join(f'<div class=a style="left:{i*w}px;top:0;width:{w}px;height:1350px;background:url({s}) center/cover;border-right:2px solid #0b0a09"></div>' for i, s in enumerate(slike))
    render(name, f'''{panels}<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.94) 0%,rgba(8,7,6,.78) 28%,rgba(8,7,6,0) 48%,rgba(8,7,6,0) 82%,rgba(8,7,6,.82) 100%)"></div>
    <div class=logo style="left:0;right:0;top:36px;height:120px"></div>
    <div class="a serif it" style="left:0;right:0;top:185px;text-align:center"><span class=gold style="font-size:{130 if len(naslov) < 16 else 104}px">{naslov}</span></div>
    <div class="a sans" style="left:0;right:0;top:370px;text-align:center;font-size:25px">{pod}</div>
    <div class="a sans" style="left:0;right:0;bottom:44px;text-align:center;font-size:22px;color:#f3dca4">Listajte →</div>''')


def cta(name, naslov, linije, poruka):
    li = "<br>".join(linije)
    render(name, f'''<div class=a style="inset:0;background:radial-gradient(ellipse at 50% 35%,#2a1f12,#0b0a09 70%)"></div>
    <div class=logo style="left:190px;right:190px;top:130px;height:300px"></div>
    <div class="a serif it" style="left:0;right:0;top:500px;text-align:center"><span class=gold style="font-size:96px">{naslov}</span></div>
    <div class=a style="left:110px;right:110px;top:650px;text-align:center"><div class=body style="font-size:35px">{poruka}</div></div>
    <div class=a style="left:0;right:0;top:880px;text-align:center"><div class=sans style="font-size:25px;line-height:2.1">{li}</div></div>
    <div class="a serif it" style="left:0;right:0;bottom:70px;text-align:center"><span class=gold style="font-size:44px">emazlatoisrebro.com</span></div>''')


if cmd == "pon":
    kolaz("l1", ["w5_mama_b.jpg", "w5_supruga.jpg", "w5_sestra.jpg", "w5_prijateljica.jpg"], "Lista želja za nju", "Poklon za svaku važnu ženu · Tuzla")
    slajd("l2", "w5_mama_b.jpg", 1, 5, "Za mamu", "Srebrni set u zlatnoj boji · zeleni kamen", "98 KM", True, "center bottom")
    slajd("l3", "w5_supruga.jpg", 2, 5, "Za suprugu", "Srebrni set · ovalni cirkon", "111 KM", False, "center 35%")
    slajd("l4", "w5_sestra.jpg", 3, 5, "Za sestru", "Srebrne minđuše · roza kamen", "38 KM", True, "70% center")
    slajd("l5", "w5_prijateljica.jpg", 4, 5, "Za prijateljicu", "Srebrni lančić leptir · više boja", "60 KM", True, "center bottom")
    slajd("l6", "w5_sebe.jpg", 5, 5, "Za sebe", "Srebrni prsten soliter", "71 KM", True, "center bottom")
    cta("l7", "Kome biste poklonili?", ["Prekinute mladosti 8, Tuzla", "Certifikat uz svaki komad", "Dostava u cijeloj BiH · pouzećem"], "Označite u komentaru za koga je vaš poklon, ili sačuvajte listu za kasnije.")
if cmd == "pet":
    render("j1", '''<div class=a style="left:0;top:0;width:540px;height:1350px;background:url(w5_jedn.jpg) center/cover"></div>
    <div class=a style="left:540px;top:0;width:540px;height:1350px;background:url(w5_bogato.jpg) center/cover;border-left:3px solid #0b0a09"></div>
    <div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.94) 0%,rgba(8,7,6,.7) 26%,rgba(8,7,6,0) 44%,rgba(8,7,6,0) 74%,rgba(8,7,6,.92) 92%)"></div>
    <div class=logo style="left:0;right:0;top:36px;height:120px"></div>
    <div class="a serif it" style="left:0;right:0;top:185px;text-align:center"><span class=gold style="font-size:82px">Jednostavno ili raskošno?</span></div>
    <div class="a sans" style="left:0;right:0;top:320px;text-align:center;font-size:25px">Napišite A ili B u komentar</div>
    <div class="a serif it" style="left:0;width:540px;bottom:70px;text-align:center"><span class=gold style="font-size:120px">A</span></div>
    <div class="a serif it" style="left:540px;width:540px;bottom:70px;text-align:center"><span class=gold style="font-size:120px">B</span></div>''')
    slajd("j2", "w5_jedn.jpg", "A", "B", "Jednostavno", "Srebrni prsten soliter · tanki", "41 KM", False, "center 40%")
    slajd("j3", "w5_bogato.jpg", "B", "B", "Raskošno", "Srebrni prsten sa velikim cirkonom", "63 KM", False, "center 40%")
    cta("j4", "Vi ste A ili B?", ["Prekinute mladosti 8, Tuzla", "Certifikat uz svaki komad", "Dostava u cijeloj BiH · pouzećem"], "Napišite nam u komentaru. Veličinu prilagođavamo u radnji.")
