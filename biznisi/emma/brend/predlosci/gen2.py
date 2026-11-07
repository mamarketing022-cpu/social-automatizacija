import sys
cmd = sys.argv[1]
sys.argv = ["gen", "x"]
from gen import render, L
import shutil, pathlib

G = L.parent / "veo" / "g"
for f in G.glob("*.jpg"):
    shutil.copy(f, L / f.name)
FADE_B = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.5) 0%,rgba(8,7,6,0) 16%,rgba(8,7,6,0) 66%,rgba(8,7,6,.94) 84%,rgba(8,7,6,1) 100%)"></div>'
FADE_T = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.9) 0%,rgba(8,7,6,.72) 24%,rgba(8,7,6,0) 44%,rgba(8,7,6,0) 90%,rgba(8,7,6,.4) 100%)"></div>'
LOGO = '<div class=logo style="left:44px;top:36px;width:190px;height:84px;background-position:left"></div>'


def proizvod(name, img, n, naslov, opis, gore=False, pos="center"):
    if gore:
        txt = f'''<div class="a serif it" style="left:64px;right:40px;top:150px"><span class=gold style="font-size:94px">{naslov}</span></div>
        <div class=a style="left:66px;right:64px;top:272px"><div class=hair></div></div>
        <div class="a sans" style="left:66px;top:296px;font-size:23px">{opis}</div>'''
    else:
        txt = f'''<div class="a serif it" style="left:64px;right:40px;bottom:150px"><span class=gold style="font-size:94px">{naslov}</span></div>
        <div class=a style="left:66px;right:64px;bottom:126px"><div class=hair></div></div>
        <div class="a sans" style="left:66px;bottom:70px;font-size:23px">{opis}</div>'''
    render(name, f'''<div class=ph style="background-image:url({img});background-position:{pos}"></div>{FADE_T if gore else FADE_B}{LOGO}
    <div class="a sans" style="right:48px;top:64px;font-size:20px">{n} / 4</div>{txt}''')


if cmd == "pon":
    render("n1", f'''<div class=ph style="background-image:url(set_a.jpg);background-position:center bottom"></div>{FADE_T}
    <div class=logo style="left:0;right:0;top:36px;height:120px"></div>
    <div class="a serif it" style="left:0;right:0;top:185px;text-align:center"><span class=gold style="font-size:150px">Novo u radnji</span></div>
    <div class="a sans" style="left:0;right:0;top:372px;text-align:center;font-size:25px">Tuzla · četiri nova komada</div>
    <div class="a sans" style="left:0;right:0;bottom:44px;text-align:center;font-size:22px;color:#f3dca4">Listajte →</div>''')
    proizvod("n2", "prsten_b.jpg", 1, "Smaragd-rez cirkon", "Srebrni prsten · 3,3 g", True, "center bottom")
    proizvod("n3", "nar_b.jpg", 2, "Srce i strijela", "Srebrna narukvica s pozlatom · 6,5 g", False, "center top")
    proizvod("n4", "lancic_a.jpg", 3, "Zeleni privjesak", "Srebrni lančić · 2,4 g", False, "center top")
    proizvod("n5", "set_b.jpg", 4, "Okrugli cirkon", "Srebrni set u zlatnoj boji · 7,28 g", True, "center bottom")
    render("n6", '''<div class=a style="inset:0;background:radial-gradient(ellipse at 50% 35%,#2a1f12,#0b0a09 70%)"></div>
    <div class=logo style="left:190px;right:190px;top:130px;height:300px"></div>
    <div class="a serif it" style="left:0;right:0;top:500px;text-align:center"><span class=gold style="font-size:104px">Koji je vaš favorit?</span></div>
    <div class=a style="left:120px;right:120px;top:660px;text-align:center"><div class=body style="font-size:36px">Napišite nam u komentaru, ili sačuvajte za poklon.</div></div>
    <div class=a style="left:0;right:0;top:880px;text-align:center"><div class=sans style="font-size:25px;line-height:2.1">Prekinute mladosti 8, Tuzla<br>Certifikat uz svaki komad<br>Dostava u cijeloj BiH · pouzećem</div></div>
    <div class="a serif it" style="left:0;right:0;bottom:70px;text-align:center"><span class=gold style="font-size:44px">emazlatoisrebro.com</span></div>''')
if cmd == "pet":
    render("u1", f'''<div class=ph style="background-image:url(us_pop_b.jpg);background-position:center bottom"></div>
    <div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.92) 0%,rgba(8,7,6,.78) 36%,rgba(8,7,6,0) 58%,rgba(8,7,6,.2) 86%,rgba(8,7,6,.85) 100%)"></div>
    <div class=logo style="left:0;right:0;top:36px;height:120px"></div>
    <div class="a serif it" style="left:30px;right:30px;top:195px;text-align:center"><span class=gold style="font-size:110px">Pukao lančić?</span></div>
    <div class="a serif it" style="left:30px;right:30px;top:330px;text-align:center"><span class=gold style="font-size:110px">Prsten ne pristaje?</span></div>
    <div class="a sans" style="left:0;right:0;bottom:50px;text-align:center;font-size:24px">3 stvari koje radimo u radnji u Tuzli →</div>''')
    for name, img, n, naslov, stavke, pos in [("u2", "us_pop_a.jpg", "01", "Popravka", ["Promjena veličine prstena", "Lemljenje lančića i narukvica", "Zamjena kopči i zatvarača", "Čišćenje i poliranje"], "center 70%"),
                                              ("u3", "us_grav_a.jpg", "02", "Graviranje", ["Imena, inicijali i datumi", "Burme i zaručničko prstenje", "Privjesci i pločice", "Savjet o fontu i rasporedu"], "center 75%"),
                                              ("u4", "us_uho_a.jpg", "03", "Bušenje ušiju", ["Za djecu i odrasle", "Sterilan, higijenski postupak", "Minđuše za osjetljivu kožu", "Upute za njegu nakon bušenja"], "center 60%")]:
        li = "".join(f'<div class=body style="font-size:33px;padding:13px 0;border-bottom:1px solid rgba(216,178,108,.28)">{s}</div>' for s in stavke)
        render(name, f'''<div class=ph style="background-image:url({img});bottom:auto;height:800px;background-position:{pos}"></div>
        <div class=a style="left:0;right:0;top:500px;height:305px;background:linear-gradient(180deg,rgba(11,10,9,0),#0b0a09)"></div>{LOGO}
        <div class="a serif it" style="right:56px;top:44px"><span class=gold style="font-size:56px">{n}</span></div>
        <div class="a serif it" style="left:64px;top:650px"><span class=gold style="font-size:102px">{naslov}</span></div>
        <div class=a style="left:66px;right:66px;top:800px">{li}</div>
        <div class="a sans" style="left:66px;bottom:52px;font-size:21px">Prekinute mladosti 8 · Tuzla</div>''')
    render("u5", '''<div class=a style="inset:0;background:radial-gradient(ellipse at 50% 35%,#2a1f12,#0b0a09 70%)"></div>
    <div class=logo style="left:190px;right:190px;top:130px;height:300px"></div>
    <div class="a serif it" style="left:0;right:0;top:500px;text-align:center"><span class=gold style="font-size:112px">Gdje nas naći</span></div>
    <div class=a style="left:0;right:0;top:670px;text-align:center"><div class=body style="font-size:42px">Prekinute mladosti 8, Tuzla</div><div class=body style="font-size:34px;opacity:.8;padding-top:6px">Ponedjeljak – subota</div>
    <div class=body style="font-size:42px;padding-top:40px;color:#e8c98a">WhatsApp 066 033-011</div></div>
    <div class="a sans" style="left:0;right:0;bottom:80px;text-align:center;font-size:24px">Sačuvajte za kad zatreba</div>''')
