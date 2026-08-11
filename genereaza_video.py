#!/usr/bin/env python3
"""Generează clipuri verticale 1080x1920 pentru TikTok — grafică animată.

Nu sunt filmări: sunt clipuri tipografice, de tipul „text pe fundal", care
se postează ca atare sau se folosesc ca deschidere/închidere pentru filmări
reale. Fără sunet — sunetul se adaugă din aplicație.
"""
import os
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30

CREAM = (251, 247, 243)
BURGUNDY = (94, 16, 38)
GOLD = (154, 123, 39)
GOLD_L = (198, 168, 90)
INK = (38, 38, 38)
GREY = (110, 110, 110)
MUTED_D = (214, 194, 186)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

# zonă sigură: dreapta are pictogramele aplicației, jos are descrierea
X0, XW = 100, 760
Y_TOP, Y_BOT = 250, 1520

_fc = {}


def fnt(p, s):
    k = (p, int(s))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]


def th(f):
    b = f.getbbox("Ághșț")
    return b[3] - b[1]


def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


def mix(bg, fg, a):
    a = max(0.0, min(1.0, a))
    return tuple(int(bg[i] + (fg[i] - bg[i]) * a) for i in range(3))


def appear(t, start, dur=0.55):
    """întoarce (alpha, deplasare verticală) pentru un element care intră"""
    e = ease((t - start) / dur)
    return e, (1 - e) * 26


def block(d, bg, lines, font, color, x, y, alpha, dy, lead=1.28):
    lh = th(font) * lead
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh + dy), ln, font=font, fill=mix(bg, color, alpha))
    return y + len(lines) * lh


def chrome(d, bg, t, dur, dark, kicker=True):
    """kicker sus, mențiune jos, bară de progres"""
    if kicker:
        a, dy = appear(t, 0.15)
        f_k = fnt(SANS_B, 30)
        d.text((X0, 150 + dy), "CRAMELE ODOBEȘTI", font=f_k,
               fill=mix(bg, GOLD if not dark else GOLD_L, a))
        kw = d.textlength("CRAMELE ODOBEȘTI", font=f_k)
        d.line([(X0, 150 + th(f_k) + 20 + dy), (X0 + kw * a, 150 + th(f_k) + 20 + dy)],
               fill=mix(bg, GOLD if not dark else GOLD_L, a), width=3)

    f_f = fnt(SANS, 27)
    a2, _ = appear(t, 0.6)
    d.text((X0, 1640), "Consumă responsabil · 18+", font=f_f,
           fill=mix(bg, MUTED_D if dark else GREY, a2 * 0.9))

    p = max(0.0, min(1.0, t / dur))
    d.line([(0, H - 8), (W * p, H - 8)], fill=mix(bg, GOLD_L if dark else GOLD, 1.0), width=8)


# ---------------------------------------------------------------- clipul 1
def frame_soiuri(t, dur):
    bg = CREAM
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    chrome(d, bg, t, dur, dark=False)

    f_h = fnt(SERIF_B, 60)
    a, dy = appear(t, 0.3)
    y = block(d, bg, wrap(d, "Soiuri pe care aproape nimeni nu le mai lucrează", f_h, XW),
              f_h, INK, X0, Y_TOP, a, dy)

    f_n = fnt(SERIF_B, 86)
    nume = [("Zghihara", 2.4), ("Crâmpoșie", 3.7), ("Băbească Gri", 5.0), ("Cadarcă", 6.3)]
    ny = y + 90
    for i, (nm, st) in enumerate(nume):
        an, dn = appear(t, st)
        if an > 0:
            d.text((X0, ny + i * 128 + dn), nm, font=f_n, fill=mix(bg, BURGUNDY, an))

    f_c = fnt(SANS, 40)
    a3, d3 = appear(t, 8.2)
    cy = ny + 4 * 128 + 60
    clines = wrap(d, "Le lucrăm pe toate. Ecologic, din 2010.", f_c, XW)
    if a3 > 0:
        block(d, bg, clines, f_c, INK, X0, cy, a3, d3)

    a4, d4 = appear(t, 10.2)
    if a4 > 0:
        f_l = fnt(SANS_B, 42)
        ly = cy + len(clines) * th(f_c) * 1.28 + 46
        d.text((X0, ly + d4), "Link în bio", font=f_l, fill=mix(bg, BURGUNDY, a4))
    return img


# ---------------------------------------------------------------- clipul 2
def scene_bio_a(t):
    bg = CREAM
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    f_h = fnt(SERIF_B, 58)
    a, dy = appear(t, 0.3)
    y = block(d, bg, wrap(d, "Am trecut via în sistem ecologic în", f_h, XW),
              f_h, INK, X0, Y_TOP, a, dy)

    # numărul urcă de la 1996 la 2010, apoi se așază
    f_big = fnt(SERIF_B, 250)
    an, _ = appear(t, 1.1, 0.4)
    if an > 0:
        p = max(0.0, min(1.0, (t - 1.4) / 1.3))
        val = int(1996 + (2010 - 1996) * ease(p))
        d.text((X0, y + 50), str(val), font=f_big, fill=mix(bg, BURGUNDY, an))

    f_c = fnt(SANS, 38)
    cy = y + 50 + th(f_big) + 70
    for i, (txt, st) in enumerate([
        ("Printre primii din România care au convertit suprafețe de peste 15 hectare.", 3.6),
        ("Fără erbicide. Fără insecticide. Fără îngrășăminte de sinteză.", 5.8),
        ("Stropim doar minimul necesar, cu macerate de plante.", 7.8),
    ]):
        aa, dd = appear(t, st)
        if aa > 0:
            cy = block(d, bg, wrap(d, txt, f_c, XW), f_c, INK if i == 0 else GREY,
                       X0, cy, aa, dd) + 26
        else:
            cy += len(wrap(d, txt, f_c, XW)) * th(f_c) * 1.28 + 26
    return img


def scene_bio_b(t):
    """finalul, pe burgundy"""
    bg = BURGUNDY
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    f_q = fnt(SERIF_B, 76)
    a, dy = appear(t, 0.15, 0.7)
    lines = wrap(d, "Ne doare pe noi capul, ca să nu fie nevoie de scurtături.", f_q, XW)
    lh = th(f_q) * 1.3
    y = (H - len(lines) * lh) / 2 - 60
    for i, ln in enumerate(lines):
        d.text((X0, y + i * lh + dy), ln, font=f_q, fill=mix(bg, CREAM, a))
    f_b = fnt(SANS_B, 34)
    a2, d2 = appear(t, 1.1)
    d.text((X0, y + len(lines) * lh + 70 + d2), "CRAMELE ODOBEȘTI",
           font=f_b, fill=mix(bg, GOLD_L, a2))
    return img


CUT = 10.6
FADE = 0.35


def frame_bio(t, dur):
    if t < CUT:
        img = scene_bio_a(t)
        d = ImageDraw.Draw(img)
        chrome(d, CREAM, t, dur, dark=False)
        if t > CUT - FADE:
            b = scene_bio_b(0.0)
            db = ImageDraw.Draw(b)
            chrome(db, BURGUNDY, t, dur, dark=True, kicker=False)
            return Image.blend(img, b, (t - (CUT - FADE)) / FADE)
        return img
    img = scene_bio_b(t - CUT)
    d = ImageDraw.Draw(img)
    chrome(d, BURGUNDY, t, dur, dark=True, kicker=False)
    return img


# ---------------------------------------------------------------- encodare
def encode(fn, dur, path):
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(dur * FPS)
    for i in range(n):
        pr.stdin.write(fn(i / FPS, dur).tobytes())
    pr.stdin.close()
    rc = pr.wait()
    if rc != 0:
        raise SystemExit(f"ffmpeg a esuat pentru {path}")
    mb = os.path.getsize(path) / 1e6
    print(f"  {path}  {dur:.0f}s  {n} cadre  {mb:.1f} MB")


if __name__ == "__main__":
    out = os.environ.get("OUT_DIR", "video")
    os.makedirs(out, exist_ok=True)
    encode(frame_soiuri, 13.0, os.path.join(out, "01-soiuri-rare.mp4"))
    encode(frame_bio, 14.0, os.path.join(out, "02-bio-din-2010.mp4"))
    print("Gata.")
