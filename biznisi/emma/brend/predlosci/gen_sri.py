import sys
sys.argv = ["gen", "x"]
from gen import render, L
from PIL import Image

# (slika, veličina kvadrata u px kadra, centar x 0-1, odsječeno odozgo u px)
KADROVI = {"b0": ("c00_1.jpg", 1480, .50, 0), "b1": ("c00_0.jpg", 2050, .50, 560), "b2": ("c05_1.jpg", 1480, .50, 0),
           "b3": ("c05_0.jpg", 2000, .50, 620), "b4": ("i08.jpg", 1750, .32, 200), "b5": ("c06_1.jpg", 1560, .50, 60)}
for n, (src, S, cx, oy) in KADROVI.items():
    im = Image.open(L / src).convert("RGB").resize((S * 2, S * 2), Image.LANCZOS)
    x = int(min(max(cx * S * 2 - 1080, 0), S * 2 - 2160))
    im = im.crop((x, oy * 2, x + 2160, min(oy * 2 + 3840, S * 2)))
    c = Image.new("RGB", (2160, 3840), (11, 10, 9)); c.paste(im, (0, 0)); c.save(L / f"{n}.jpg", quality=95)

for i, t in enumerate(["Jedan detalj", "mijenja sve", "Za posebne večeri", "i za svaki dan", "Topli zlatni sjaj", "Blizu srca"]):
    render(f"t{i}", f'''<div class=a style="left:0;right:0;top:0;height:230px;background:linear-gradient(180deg,rgba(8,7,6,.6),rgba(8,7,6,0))"></div>
    <div class=a style="left:0;right:0;top:1230px;height:280px;background:linear-gradient(180deg,rgba(11,10,9,0),#0b0a09)"></div>
    <div class=a style="left:0;right:0;top:1500px;bottom:0;background:#0b0a09"></div>
    <div class=logo style="left:44px;top:56px;width:210px;height:92px;background-position:left"></div>
    <div class="a serif it" style="left:20px;right:20px;top:1450px;text-align:center"><span class=gold style="font-size:{112 if len(t) < 14 else 92}px">{t}</span></div>''',
           1080, 1920, transparent=True)

render("cover", '''<div class=ph style="background-image:url(b0.jpg);background-size:100% 100%"></div>
<div class=a style="left:0;right:0;top:0;height:230px;background:linear-gradient(180deg,rgba(8,7,6,.6),rgba(8,7,6,0))"></div>
<div class=a style="left:0;right:0;top:1230px;height:280px;background:linear-gradient(180deg,rgba(11,10,9,0),#0b0a09)"></div>
<div class=a style="left:0;right:0;top:1500px;bottom:0;background:#0b0a09"></div>
<div class=logo style="left:44px;top:56px;width:210px;height:92px;background-position:left"></div>
<div class="a serif it" style="left:20px;right:20px;top:1440px;text-align:center"><span class=gold style="font-size:118px">Jedan detalj<br>mijenja sve</span></div>''', 1080, 1920)
