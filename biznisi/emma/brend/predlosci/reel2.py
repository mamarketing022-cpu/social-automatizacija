import sys, subprocess, pathlib
OUT, MUSIC = sys.argv[1], sys.argv[2]
sys.argv = ["gen", "x"]
from gen import render, L

C = L.parent / "veo" / "clips"
SHOTS = [("prsten.mp4", "Novo u radnji", "Srebrni prsten · smaragd-rez cirkon"),
         ("nar.mp4", "Srce i strijela", "Srebrna narukvica s pozlatom"),
         ("set.mp4", "Okrugli cirkon", "Srebrni set u zlatnoj boji")]
for i, (_, t, s) in enumerate(SHOTS):
    render(f"r{i}", f'''<div class=a style="left:0;right:0;top:0;height:230px;background:linear-gradient(180deg,rgba(8,7,6,.6),rgba(8,7,6,0))"></div>
    <div class=a style="left:0;right:0;top:1180px;bottom:0;background:linear-gradient(180deg,rgba(8,7,6,0),rgba(8,7,6,.85) 40%,rgba(8,7,6,.9))"></div>
    <div class=logo style="left:44px;top:56px;width:210px;height:92px;background-position:left"></div>
    <div class="a serif it" style="left:20px;right:20px;top:1380px;text-align:center"><span class=gold style="font-size:112px">{t}</span></div>
    <div class="a sans" style="left:0;right:0;top:1530px;text-align:center;font-size:27px">{s}</div>''', 1080, 1920, transparent=True)
render("kraj2", '''<div class=a style="inset:0;background:radial-gradient(ellipse at 50% 40%,#2a1f12,#0b0a09 70%)"></div>
<div class=logo style="left:140px;right:140px;top:430px;height:370px"></div>
<div class="a serif it" style="left:0;right:0;top:860px;text-align:center"><span class=gold style="font-size:90px">Koji je vaš favorit?</span></div>
<div class=a style="left:0;right:0;top:1000px;text-align:center"><div class=sans style="font-size:28px;line-height:2">Prekinute mladosti 8, Tuzla<br>Certifikat uz svaki komad<br>Dostava u cijeloj BiH</div></div>
<div class="a serif it" style="left:0;right:0;top:1250px;text-align:center"><span class=gold style="font-size:46px">emazlatoisrebro.com</span></div>''', 1080, 1920)


def run(a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, check=True)


seg = L / "seg2"; seg.mkdir(exist_ok=True); parts = []
D = 5.8
for i, (clip, _, _) in enumerate(SHOTS):
    o = seg / f"c{i}.mp4"
    run(["-ss", "0.4", "-t", str(D), "-i", str(C / clip), "-loop", "1", "-framerate", "30", "-t", str(D), "-i", str(L / "out" / f"r{i}.png"),
         "-filter_complex", f"[0:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1[b];[1:v]format=rgba,fade=t=in:st=0.15:d=0.4:alpha=1[t];[b][t]overlay=0:0,trim=duration={D},setpts=PTS-STARTPTS,format=yuv420p[v]",
         "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-color_range", "tv", str(o)])
    parts.append(o)
o = seg / "c9.mp4"
run(["-loop", "1", "-framerate", "30", "-t", "2.8", "-i", str(L / "out" / "kraj2.png"), "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p,fade=t=in:st=0:d=0.35",
     "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-color_range", "tv", str(o)])
parts.append(o)
(seg / "list.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
T = 3 * D + 2.8
run(["-f", "concat", "-safe", "0", "-i", str(seg / "list.txt"), "-ss", "47", "-t", str(T), "-i", MUSIC,
     "-af", f"afade=t=in:st=0:d=0.4,afade=t=out:st={T-1.6}:d=1.6", "-map", "0:v", "-map", "1:a", "-t", str(T),
     "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_range", "tv", "-r", "30",
     "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", OUT])
# naslovna
render("cover2", '''<div class=ph style="background-image:url(v_pr_a.jpg);background-position:center top"></div>
<div class=a style="left:0;right:0;top:0;height:230px;background:linear-gradient(180deg,rgba(8,7,6,.6),rgba(8,7,6,0))"></div>
<div class=a style="left:0;right:0;top:1180px;bottom:0;background:linear-gradient(180deg,rgba(8,7,6,0),rgba(8,7,6,.85) 40%,rgba(8,7,6,.9))"></div>
<div class=logo style="left:44px;top:56px;width:210px;height:92px;background-position:left"></div>
<div class="a serif it" style="left:20px;right:20px;top:1330px;text-align:center"><span class=gold style="font-size:128px">Novo u radnji</span></div>
<div class="a sans" style="left:0;right:0;top:1500px;text-align:center;font-size:28px">Emma's Jewelry · Tuzla</div>''', 1080, 1920)
print(T)
