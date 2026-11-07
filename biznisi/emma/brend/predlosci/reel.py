import pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
L = pathlib.Path(__file__).parent.resolve()
OUT, MUSIC = pathlib.Path(sys.argv[1]), sys.argv[2]
seg = L / "seg"; seg.mkdir(exist_ok=True)
FPS = 30

# dijagonalni odsjaj
b = Image.new("L", (2200, 1920), 0)
ImageDraw.Draw(b).polygon([(900, 0), (1250, 0), (950, 1920), (600, 1920)], fill=120)
b = b.filter(ImageFilter.GaussianBlur(70))
band = Image.new("RGBA", b.size, (255, 244, 214, 0)); band.putalpha(b); band.save(L / "band.png")

# (slika, tekst, trajanje, zoom od, zoom do, y-pomak kroz sliku 0-1)
SHOTS = [("b0.jpg", "t0", 2.4, 1.00, 1.07, .30), ("b1.jpg", "t1", 2.2, 1.00, 1.09, .30),
         ("b2.jpg", "t2", 2.4, 1.00, 1.07, .30), ("b3.jpg", "t3", 2.2, 1.00, 1.09, .30),
         ("b4.jpg", "t4", 2.4, 1.00, 1.07, .30), ("b5.jpg", "t5", 2.4, 1.00, 1.07, .30)]


def run(a):
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, capture_output=True, text=True)
    r.check_returncode()


parts = []
for i, (img, txt, d, z0, z1, fy) in enumerate(SHOTS):
    n = round(d * FPS); o = seg / f"s{i}.mp4"
    z = f"{z0}+({z1}-{z0})*on/{n}"
    f = (f"[0:v]zoompan=z='{z}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*{fy}':d={n}:s=1080x1920:fps={FPS},setsar=1,format=rgba[b];"
         f"[1:v]format=rgba[bd];[b][bd]overlay=x='-2200+(t/{d})*3300':y=0[s];"
         f"[2:v]format=rgba,fade=t=in:st=0.12:d=0.3:alpha=1[t];[s][t]overlay=0:0:shortest=0,trim=duration={d},setpts=PTS-STARTPTS,scale=in_range=pc:out_range=tv,format=yuv420p[v]")
    run(["-loop", "1", "-t", str(d), "-i", str(L / img), "-loop", "1", "-framerate", str(FPS), "-t", str(d), "-i", str(L / "band.png"),
         "-loop", "1", "-framerate", str(FPS), "-t", str(d), "-i", str(L / "out" / f"{txt}.png"), "-filter_complex", f, "-map", "[v]",
         "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-color_range", "tv", str(o)])
    parts.append(o)

d = 3.0; n = round(d * FPS); o = seg / "s9.mp4"
run(["-loop", "1", "-framerate", str(FPS), "-t", str(d), "-i", str(L / "out" / "kraj.png"), "-vf",
     f"scale=in_range=pc:out_range=tv,format=yuv420p,fade=t=in:st=0:d=0.35", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "17",
     "-pix_fmt", "yuv420p", "-color_range", "tv", str(o)])
parts.append(o)
(seg / "list.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
T = sum(s[2] for s in SHOTS) + d
run(["-f", "concat", "-safe", "0", "-i", str(seg / "list.txt"), "-ss", "30", "-t", str(T), "-i", MUSIC, "-af", f"afade=t=in:st=0:d=0.3,afade=t=out:st={T-1.5}:d=1.5",
     "-map", "0:v", "-map", "1:a", "-t", str(T), "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_range", "tv",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(OUT)])
print(T)
