import sys
cmd = sys.argv[1]
sys.argv = ["gen", "x"]
from gen import render, L
import shutil

G = L.parent / "w4" / "g"
for f in G.glob("*.jpg"):
    shutil.copy(f, L / f.name)
FADE_B = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.5) 0%,rgba(8,7,6,0) 16%,rgba(8,7,6,0) 64%,rgba(8,7,6,.94) 83%,rgba(8,7,6,1) 100%)"></div>'
FADE_T = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.9) 0%,rgba(8,7,6,.7) 24%,rgba(8,7,6,0) 44%,rgba(8,7,6,0) 88%,rgba(8,7,6,.45) 100%)"></div>'
LOGO = '<div class=logo style="left:44px;top:36px;width:190px;height:84px;background-position:left"></div>'


def slajd(name, img, n, uk, naslov, opis, gore=False, pos="center"):
    if gore:
        txt = f'''<div class="a serif it" style="left:64px;right:40px;top:150px"><span class=gold style="font-size:92px">{naslov}</span></div>
        <div class=a style="left:66px;right:64px;top:270px"><div class=hair></div></div>
        <div class="a sans" style="left:66px;top:294px;font-size:23px">{opis}</div>'''
    else:
        txt = f'''<div class="a serif it" style="left:64px;right:40px;bottom:150px"><span class=gold style="font-size:92px">{naslov}</span></div>
        <div class=a style="left:66px;right:64px;bottom:126px"><div class=hair></div></div>
        <div class="a sans" style="left:66px;bottom:70px;font-size:23px">{opis}</div>'''
    render(name, f'''<div class=ph style="background-image:url({img});background-position:{pos}"></div>{FADE_T if gore else FADE_B}{LOGO}
    <div class="a sans" style="right:48px;top:64px;font-size:20px">{n} / {uk}</div>{txt}''')


def kolaz(name, slike, naslov, pod):
    w = 1080 // len(slike)
    panels = "".join(f'<div class=a style="left:{i*w}px;top:0;width:{w}px;height:1350px;background:url({s}) center/cover;border-right:2px solid #0b0a09"></div>' for i, s in enumerate(slike))
    render(name, f'''{panels}<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.92) 0%,rgba(8,7,6,.75) 26%,rgba(8,7,6,0) 46%,rgba(8,7,6,0) 82%,rgba(8,7,6,.8) 100%)"></div>
    <div class=logo style="left:0;right:0;top:36px;height:120px"></div>
    <div class="a serif it" style="left:0;right:0;top:185px;text-align:center"><span class=gold style="font-size:{140 if len(naslov) < 14 else 96}px">{naslov}</span></div>
    <div class="a sans" style="left:0;right:0;top:375px;text-align:center;font-size:25px">{pod}</div>
    <div class="a sans" style="left:0;right:0;bottom:44px;text-align:center;font-size:22px;color:#f3dca4">Listajte →</div>''')


def cta(name, naslov, linije, poruka):
    li = "<br>".join(linije)
    render(name, f'''<div class=a style="inset:0;background:radial-gradient(ellipse at 50% 35%,#2a1f12,#0b0a09 70%)"></div>
    <div class=logo style="left:190px;right:190px;top:130px;height:300px"></div>
    <div class="a serif it" style="left:0;right:0;top:500px;text-align:center"><span class=gold style="font-size:100px">{naslov}</span></div>
    <div class=a style="left:110px;right:110px;top:650px;text-align:center"><div class=body style="font-size:35px">{poruka}</div></div>
    <div class=a style="left:0;right:0;top:880px;text-align:center"><div class=sans style="font-size:25px;line-height:2.1">{li}</div></div>
    <div class="a serif it" style="left:0;right:0;bottom:70px;text-align:center"><span class=gold style="font-size:44px">emazlatoisrebro.com</span></div>''')


if cmd == "pon":
    kolaz("z1", ["krugovi_a.jpg", "krug_b.jpg", "srce_b.jpg"], "Zlatni setovi", "Lančić i minđuše od zlata · Tuzla")
    slajd("z2", "krugovi_b.jpg", 1, 3, "Dva kruga", "Zlatni set · lančić i minđuše", False, "center 40%")
    slajd("z3", "krug_a.jpg", 2, 3, "Krug sa cirkonima", "Zlatni set · lančić i minđuše", True, "center bottom")
    slajd("z4", "srce_a.jpg", 3, 3, "Srce", "Zlatni set · lančić i minđuše", False, "center top")
    cta("z5", "Koji je vaš?", ["Prekinute mladosti 8, Tuzla", "Certifikat uz svaki komad", "Dostava u cijeloj BiH · pouzećem"], "Napišite nam u komentaru, ili sačuvajte za poklon.")
if cmd == "pet":
    kolaz("k1", ["dvj_a.jpg", "ddip_a.jpg", "drod_a.jpg", "d50_a.jpg"], "Dukat za poseban dan", "Vjenčanje · diploma · rođendan · godišnjica")
    slajd("k2", "dvj_a.jpg", 1, 4, "Sretno vjenčanje", "Zlatni dukat · poklon za mladence", True, "center bottom")
    slajd("k3", "ddip_a.jpg", 2, 4, "Čestitamo na diplomi", "Zlatni dukat · za diplomu ili maturu", False, "center 30%")
    slajd("k4", "drod_a.jpg", 3, 4, "Sretan rođendan", "Zlatni dukat · trajan poklon", True, "center bottom")
    slajd("k5", "d50_a.jpg", 4, 4, "50.", "Za 50. rođendan ili zlatnu godišnjicu", True, "center bottom")
    cta("k6", "Popust na veći dukat", ["−5% na dukat od 4 g · −10% na dukat od 5 g", "Certifikat uz svaki komad", "Prekinute mladosti 8, Tuzla"], "Motiv i gravuru dogovaramo s vama u radnji ili na WhatsApp.")
