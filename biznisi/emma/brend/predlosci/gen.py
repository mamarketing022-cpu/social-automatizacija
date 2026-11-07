import pathlib, subprocess, sys
L = pathlib.Path(__file__).parent.resolve(); OUT = L / "out"; OUT.mkdir(exist_ok=True)
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
BASE = """<!doctype html><meta charset=utf-8><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&family=Manrope:wght@400;500;600&display=block" rel=stylesheet><style>
*{margin:0;padding:0;box-sizing:border-box}html,body{width:%dpx;height:%dpx;overflow:hidden;background:%s}
.a{position:absolute}.ph{position:absolute;inset:0;background-size:cover;background-position:center}
.serif{font-family:'Playfair Display',serif;font-weight:400;line-height:1.08;letter-spacing:-.015em}
.it{font-style:italic}.gold{background:linear-gradient(100deg,#b98f4e 0%%,#f6e2ad 45%%,#c9a15c 100%%);-webkit-background-clip:text;background-clip:text;color:transparent;padding:.08em .06em .14em;margin:-.08em -.06em -.14em;-webkit-box-decoration-break:clone}
.sans{font-family:Manrope,sans-serif;font-weight:500;letter-spacing:.24em;text-transform:uppercase;color:#efe6d3}
.body{font-family:Manrope,sans-serif;font-weight:400;color:#efe6d3;line-height:1.5}
.hair{height:1px;background:linear-gradient(90deg,#d8b26c,rgba(216,178,108,0))}
.logo{position:absolute;background:url(logo.png) center/contain no-repeat}
</style>"""


def render(name, body, w=1080, h=1350, bg="#0b0a09", transparent=False):
    f = L / f"_{name}.html"
    f.write_text((BASE % (w, h, "transparent" if transparent else bg)) + body, encoding="utf-8")
    a = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}", "--force-device-scale-factor=1",
         "--virtual-time-budget=8000", f"--screenshot={OUT / (name + '.png')}", f.as_uri()]
    if transparent:
        a.insert(2, "--default-background-color=00000000")
    subprocess.run(a, capture_output=True, timeout=120)
    assert (OUT / (name + ".png")).exists(), name


GRAD = '<div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.55) 0%,rgba(8,7,6,0) 22%,rgba(8,7,6,0) 62%,rgba(8,7,6,1) 78%,rgba(8,7,6,1) 100%)"></div>'


def set_slide(name, img, n, naslov, opis, pos="center top", size="100% auto"):
    render(name, f'''<div class=ph style="background-image:url({img});background-position:{pos};background-size:{size};background-repeat:no-repeat"></div>{GRAD}
    <div class=logo style="left:44px;top:36px;width:190px;height:84px;background-position:left"></div>
    <div class="a sans" style="right:48px;top:64px;font-size:20px">{n} / 4</div>
    <div class="a serif it" style="left:64px;right:40px;bottom:150px"><span class=gold style="font-size:94px">{naslov}</span></div>
    <div class=a style="left:66px;right:64px;bottom:126px"><div class=hair></div></div>
    <div class="a sans" style="left:66px;bottom:70px;font-size:24px">{opis}</div>''')


def usluga(name, img, n, naslov, stavke):
    li = "".join(f'<div class=body style="font-size:34px;padding:15px 0;border-bottom:1px solid rgba(216,178,108,.28)">{s}</div>' for s in stavke)
    render(name, f'''<div class=ph style="background-image:url({img});bottom:auto;height:760px"></div>
    <div class=a style="left:0;right:0;top:420px;height:345px;background:linear-gradient(180deg,rgba(11,10,9,0),#0b0a09)"></div>
    <div class=logo style="left:44px;top:36px;width:190px;height:84px;background-position:left"></div>
    <div class="a serif it" style="right:56px;top:44px"><span class=gold style="font-size:56px">{n}</span></div>
    <div class="a serif it" style="left:64px;top:630px"><span class=gold style="font-size:102px">{naslov}</span></div>
    <div class=a style="left:66px;right:66px;top:790px">{li}</div>
    <div class="a sans" style="left:66px;bottom:58px;font-size:21px">Prekinute mladosti 8 · Tuzla</div>''')


c = sys.argv[1]
if c == "pon":
    render("p1", '''<div class=ph style="background-image:url(ai_plavi.png);background-position:center bottom"></div>
    <div class=a style="inset:0;background:linear-gradient(180deg,rgba(6,8,14,.35),rgba(6,8,14,0) 45%,rgba(6,8,14,0) 72%,rgba(6,8,14,.75))"></div>
    <div class=logo style="left:0;right:0;top:40px;height:120px"></div>
    <div class="a serif it" style="left:0;right:0;top:205px;text-align:center"><span class=gold style="font-size:141px">Koja je vaša?</span></div>
    <div class="a sans" style="left:0;right:0;top:400px;text-align:center;font-size:25px">Srebrni setovi · lančić i minđuše</div>
    <div class="a sans" style="left:0;right:0;bottom:50px;text-align:center;font-size:22px;color:#e8c98a">Listajte →</div>''')
    set_slide("p2", "ai_plavi.png", 1, "Tamnoplava", "Srebrni set u zlatnoj boji", "62% 72%", "150% auto")
    set_slide("p3", "c05_0.jpg", 2, "Smaragdno zelena", "Srebrni set")
    set_slide("p4", "c00_0.jpg", 3, "Baget u zlatnoj boji", "Srebrni set")
    set_slide("p5", "c00_4.jpg", 4, "Čisti sjaj", "Srebrni set · baget cirkon")
    render("p6", '''<div class=ph style="background-image:url(c05_1.jpg);opacity:.5;background-position:center 20%"></div>
    <div class=a style="inset:0;background:linear-gradient(180deg,rgba(11,10,9,.2),rgba(11,10,9,.97) 62%)"></div>
    <div class="a serif it" style="left:64px;right:64px;top:600px"><span class=gold style="font-size:96px">Napišite koju<br>biste izabrali</span></div>
    <div class=a style="left:66px;right:66px;top:885px"><div class=hair></div>
      <div class=body style="font-size:34px;padding-top:30px">Sačuvajte za poklon ili pošaljite nekome kome treba ideja.</div>
      <div class=sans style="font-size:22px;padding-top:36px;line-height:1.9">Prekinute mladosti 8, Tuzla<br>Dostava u cijeloj BiH · pouzećem</div></div>
    <div class=logo style="left:0;right:0;bottom:26px;height:92px"></div>''')
if c == "pet":
    render("f1", '''<div class=ph style="background-image:url(radnja4.jpg);background-position:62% center"></div>
    <div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.85) 0%,rgba(8,7,6,.8) 42%,rgba(8,7,6,.15) 70%,rgba(8,7,6,.9) 100%)"></div>
    <div class=logo style="left:0;right:0;top:40px;height:120px"></div>
    <div class="a serif it" style="left:30px;right:30px;top:195px;text-align:center"><span class=gold style="font-size:110px">Pukao lančić?</span></div>
    <div class="a serif it" style="left:30px;right:30px;top:340px;text-align:center"><span class=gold style="font-size:110px">Prsten ne pristaje?</span></div>
    <div class="a sans" style="left:0;right:0;bottom:60px;text-align:center;font-size:24px">3 stvari koje radimo u radnji u Tuzli →</div>''')
    usluga("f2", "popravka.jpg", "01", "Popravka", ["Promjena veličine prstena", "Lemljenje lančića i narukvica", "Zamjena kopči i zatvarača", "Čišćenje i poliranje"])
    usluga("f3", "graviranje.jpg", "02", "Graviranje", ["Imena, inicijali i datumi", "Burme i zaručničko prstenje", "Privjesci i pločice", "Savjet o fontu i rasporedu"])
    usluga("f4", "busenje.jpg", "03", "Bušenje ušiju", ["Za djecu i odrasle", "Sterilan, higijenski postupak", "Minđuše za osjetljivu kožu", "Upute za njegu nakon bušenja"])
    render("f5", '''<div class=ph style="background-image:url(radnja3.jpg);background-position:center 60%;bottom:auto;height:800px"></div>
    <div class=a style="left:0;right:0;top:480px;height:325px;background:linear-gradient(180deg,rgba(11,10,9,0),#0b0a09)"></div>
    <div class="a serif it" style="left:64px;top:690px"><span class=gold style="font-size:102px">Gdje nas naći</span></div>
    <div class=a style="left:66px;right:66px;top:845px"><div class=hair></div>
    <div class=body style="font-size:40px;padding-top:30px">Prekinute mladosti 8, Tuzla</div><div class=body style="font-size:32px;opacity:.8">Ponedjeljak – subota</div>
    <div class=body style="font-size:40px;padding-top:20px;color:#e8c98a">WhatsApp 066 033-011</div>
    <div class=sans style="font-size:21px;padding-top:32px">Sačuvajte za kad zatreba</div></div>
    <div class=logo style="left:0;right:0;bottom:24px;height:80px"></div>''')
if c == "sri":
    shots = [("Jedan detalj", None), ("mijenja sve", None), ("Za posebne večeri", None), ("i za svaki dan", None), ("Topli zlatni sjaj", None), ("Blizu srca", None)]
    for i, (t, _) in enumerate(shots):
        render(f"t{i}", f'''<div class=a style="left:0;right:0;bottom:0;height:900px;background:linear-gradient(180deg,rgba(8,7,6,0),rgba(8,7,6,.82) 62%,rgba(8,7,6,.92))"></div>
        <div class="a serif it" style="left:30px;right:30px;top:1310px;text-align:center"><span class=gold style="font-size:{124 if len(t) < 14 else 100}px">{t}</span></div>
        <div class=logo style="left:0;right:0;top:70px;height:120px"></div>''', 1080, 1920, transparent=True)
    render("kraj", '''<div class=ph style="background-image:url(c00_0.jpg);opacity:.32;filter:blur(3px)"></div>
    <div class=a style="inset:0;background:radial-gradient(ellipse at center,rgba(11,10,9,.35),rgba(11,10,9,.95))"></div>
    <div class=logo style="left:140px;right:140px;top:430px;height:370px"></div>
    <div class="a serif it" style="left:0;right:0;top:850px;text-align:center"><span class=gold style="font-size:74px">Koji komad je vaš?</span></div>
    <div class=a style="left:0;right:0;top:985px;text-align:center"><div class=sans style="font-size:28px;line-height:2">Prekinute mladosti 8, Tuzla<br>Dostava u cijeloj BiH<br>Certifikat uz svaki komad</div></div>''', 1080, 1920)
    render("cover", '''<div class=ph style="background-image:url(c00_1.jpg);background-size:auto 100%"></div>
    <div class=a style="inset:0;background:linear-gradient(180deg,rgba(8,7,6,.5),rgba(8,7,6,0) 22%,rgba(8,7,6,0) 58%,rgba(8,7,6,.9) 80%)"></div>
    <div class=logo style="left:0;right:0;top:70px;height:130px"></div>
    <div class="a serif it" style="left:30px;right:30px;top:1240px;text-align:center"><span class=gold style="font-size:136px">Jedan detalj<br>mijenja sve</span></div>''', 1080, 1920)
