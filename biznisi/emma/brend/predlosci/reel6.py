import sys, subprocess
OUT, MUSIC, SS = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["gen", "x"]
from gen import render, L

C = L.parent / "clips"
TOP = '<div class=a style="left:0;right:0;top:0;height:230px;background:linear-gradient(180deg,rgba(8,7,6,.6),rgba(8,7,6,0))"></div>'
BOT = '<div class=a style="left:0;right:0;top:1160px;bottom:0;background:linear-gradient(180deg,rgba(8,7,6,0),rgba(8,7,6,.85) 40%,rgba(8,7,6,.92))"></div>'
LOGO = '<div class=logo style="left:44px;top:56px;width:210px;height:92px;background-position:left"></div>'
CIJENA = 'display:inline-block;border:1.5px solid #d8b26c;border-radius:40px;padding:8px 28px;font-family:Manrope,sans-serif;font-weight:600;font-size:36px;color:#f3dca4;letter-spacing:.04em'

render("v0", f'''{TOP}{BOT}{LOGO}
<div class="a serif it" style="left:20px;right:20px;top:1390px;text-align:center"><span class=gold style="font-size:118px">Izvini, tata…</span></div>
<div class="a sans" style="left:0;right:0;top:1545px;text-align:center;font-size:27px">ove godine je mama prva</div>''', 1080, 1920, transparent=True)
render("v1", f'''{TOP}{BOT}{LOGO}
<div class="a serif it" style="left:20px;right:20px;top:1360px;text-align:center"><span class=gold style="font-size:104px">Set romb</span></div>
<div class="a sans" style="left:0;right:0;top:1500px;text-align:center;font-size:27px">Srebrni set · rubin kamenčići</div>
<div class=a style="left:0;right:0;top:1575px;text-align:center"><div style="{CIJENA}">75 KM</div></div>''', 1080, 1920, transparent=True)
render("kraj6", '''<div class=a style="inset:0;background:radial-gradient(ellipse at 50% 40%,#2a1f12,#0b0a09 70%)"></div>
<div class=logo style="left:140px;right:140px;top:430px;height:370px"></div>
<div class="a serif it" style="left:0;right:0;top:860px;text-align:center"><span class=gold style="font-size:92px">Za mamu, s ljubavlju.</span></div>
<div class=a style="left:0;right:0;top:1000px;text-align:center"><div class=sans style="font-size:28px;line-height:2">Prekinute mladosti 8, Tuzla<br>Certifikat uz svaki komad<br>Dostava u cijeloj BiH</div></div>
<div class="a serif it" style="left:0;right:0;top:1250px;text-align:center"><span class=gold style="font-size:46px">emazlatoisrebro.com</span></div>''', 1080, 1920)
render("cover6", f'''<div class=ph style="background-image:url(x_romb_mama.jpg);background-position:center top"></div>{TOP}{BOT}{LOGO}
<div class="a serif it" style="left:20px;right:20px;top:1370px;text-align:center"><span class=gold style="font-size:128px">Izvini, tata…</span></div>
<div class="a sans" style="left:0;right:0;top:1540px;text-align:center;font-size:30px">ove godine je mama prva</div>''', 1080, 1920)


def run(a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, check=True)


seg = L / "seg6"; seg.mkdir(exist_ok=True); parts = []
SHOTS = [("kutija.mp4", 0.0, 3.9), ("mama.mp4", 0.2, 7.7)]
for i, (clip, ss, d) in enumerate(SHOTS):
    o = seg / f"c{i}.mp4"
    run(["-ss", str(ss), "-t", str(d / 1.5 if i == 0 else d), "-i", str(C / clip), "-loop", "1", "-framerate", "30", "-t", str(d), "-i", str(L / "out" / f"v{i}.png"),
         "-filter_complex", f"[0:v]"+("setpts=1.5*PTS," if i == 0 else "")+f"fps=30,scale=1080:1920:flags=lanczos,setsar=1[b];[1:v]format=rgba,fade=t=in:st={0.0 if i == 0 else 0.2}:d=0.35:alpha=1[t];[b][t]overlay=0:0,trim=duration={d},setpts=PTS-STARTPTS,format=yuv420p[v]",
         "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-color_range", "tv", str(o)])
    parts.append(o)
o = seg / "c9.mp4"
run(["-loop", "1", "-framerate", "30", "-t", "3.4", "-i", str(L / "out" / "kraj6.png"), "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p,fade=t=in:st=0:d=0.35",
     "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-color_range", "tv", str(o)])
parts.append(o)
(seg / "list.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
T = sum(d for _, _, d in SHOTS) + 3.4
run(["-f", "concat", "-safe", "0", "-i", str(seg / "list.txt"), "-ss", SS, "-t", str(T), "-i", MUSIC,
     "-af", f"afade=t=in:st=0:d=0.4,afade=t=out:st={T-1.6}:d=1.6", "-map", "0:v", "-map", "1:a", "-t", str(T),
     "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_range", "tv", "-r", "30",
     "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", OUT])
print(T)
