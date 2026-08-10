#!/usr/bin/env python3
"""Clipuri verticale 1080x1920 pentru TikTok — teme orientate spre vânzare.

Motor generic: fiecare clip este o listă de „momente" (text + stil + secunda
la care apare). Așezarea se calculează o singură dată și se auto-scalează
până când tot conținutul încape în zona sigură, deci textele pot fi
schimbate fără să se strice compoziția.

Fără sunet — se adaugă din aplicație.
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
Y_TOP, Y_BOT = 250, 1500

_fc = {}


def fnt(p, s):
    k = (p, int(s))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(p, max(10, int(s)))
    return _fc[k]


def th(f):
    return f.getbbox("Ághșț")[3] - f.getbbox("Ághșț")[1]


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
    e = ease((t - start) / dur)
    return e, (1 - e) * 26


# stil: (font, dimensiune de bază, culoare, spațiu după)
STIL = {
    "head": (SERIF_B, 60, INK, 48),
    "sub": (SANS, 38, GREY, 30),
    "fact": (SANS, 38, INK, 30),
    "name": (SERIF_B, 84, BURGUNDY, 34),
    "name_sm": (SERIF_B, 62, BURGUNDY, 18),
    "cta": (SANS_B, 42, BURGUNDY, 0),
}


def masoara(d, momente, s):
    """calculează pozițiile verticale și înălțimea totală"""
    poz, y = [], 0.0
    for m in momente:
        path, size, col, gap = STIL[m["stil"]]
        f = fnt(path, size * s)
        lines = wrap(d, m["text"], f, XW)
        lh = th(f) * 1.28
        poz.append((lines, f, col, y, lh))
        y += len(lines) * lh + gap * s
    return poz, y


def chrome(d, bg, t, dur, dark, kicker=True):
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


def scena_principala(momente, t, scale):
    bg = CREAM
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    poz, _ = masoara(d, momente, scale)
    for m, (lines, f, col, y0, lh) in zip(momente, poz):
        a, dy = appear(t, m["la"])
        if a <= 0:
            continue
        for i, ln in enumerate(lines):
            d.text((X0, Y_TOP + y0 + i * lh + dy), ln, font=f, fill=mix(bg, col, a))
    return img


def scena_final(text, t):
    bg = BURGUNDY
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    f_q = fnt(SERIF_B, 76)
    lines = wrap(d, text, f_q, XW)
    lh = th(f_q) * 1.3
    a, dy = appear(t, 0.15, 0.7)
    y = (H - len(lines) * lh) / 2 - 60
    for i, ln in enumerate(lines):
        d.text((X0, y + i * lh + dy), ln, font=f_q, fill=mix(bg, CREAM, a))
    f_b = fnt(SANS_B, 34)
    a2, d2 = appear(t, 1.0)
    d.text((X0, y + len(lines) * lh + 70 + d2), "CRAMELE ODOBEȘTI",
           font=f_b, fill=mix(bg, GOLD_L, a2))
    return img


FADE = 0.35


def construieste(clip):
    """întoarce funcția frame(t, dur) pentru un clip definit ca date"""
    momente = clip["momente"]
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    scale = 1.0
    while scale > 0.5:
        _, tot = masoara(probe, momente, scale)
        if tot <= (Y_BOT - Y_TOP):
            break
        scale -= 0.02
    if scale < 0.99:
        print(f"    (scalat la {scale:.2f})")

    cut = clip.get("cut")
    final = clip.get("final")

    def frame(t, dur):
        if cut is None or t < cut:
            img = scena_principala(momente, t, scale)
            d = ImageDraw.Draw(img)
            chrome(d, CREAM, t, dur, dark=False)
            if cut is not None and t > cut - FADE:
                b = scena_final(final, 0.0)
                db = ImageDraw.Draw(b)
                chrome(db, BURGUNDY, t, dur, dark=True, kicker=False)
                return Image.blend(img, b, (t - (cut - FADE)) / FADE)
            return img
        img = scena_final(final, t - cut)
        d = ImageDraw.Draw(img)
        chrome(d, BURGUNDY, t, dur, dark=True, kicker=False)
        return img

    return frame


# --------------------------------------------------------------- clipurile
CLIPURI = [
    {
        "id": "03-vin-la-sarmale",
        "dur": 13.0,
        "momente": [
            {"stil": "head", "text": "Ce vin pui lângă sarmale?", "la": 0.3},
            {"stil": "sub", "text": "Nu unul puternic. Nu unul dulce.", "la": 2.2},
            {"stil": "name", "text": "Băbească Neagră", "la": 3.9},
            {"stil": "fact", "text": "Aciditate vie, taninuri blânde. Taie grăsimea, nu acoperă mâncarea.", "la": 6.0},
            {"stil": "fact", "text": "Se servește la 16 grade. Nu de la calorifer.", "la": 8.4},
            {"stil": "cta", "text": "Link în bio", "la": 10.4},
        ],
    },
    {
        "id": "04-cadou-la-masa",
        "dur": 14.0,
        "momente": [
            {"stil": "head", "text": "Ești invitat la masă. Ce duci?", "la": 0.3},
            {"stil": "sub", "text": "O sticlă e alegerea sigură. Dar care?", "la": 2.1},
            {"stil": "fact", "text": "Nu cel mai ieftin de la raft.", "la": 3.6},
            {"stil": "fact", "text": "Nu unul pe care nu l-ai gustat niciodată.", "la": 5.0},
            {"stil": "fact", "text": "Ci un soi românesc pe care gazda nu-l are.", "la": 6.6},
            {"stil": "name_sm", "text": "Fetească Neagră", "la": 8.4},
            {"stil": "name_sm", "text": "Busuioacă de Bohotin", "la": 9.2},
            {"stil": "name_sm", "text": "Zghihara", "la": 10.0},
            {"stil": "cta", "text": "Link în bio", "la": 11.4},
        ],
    },
    {
        "id": "05-de-ce-costa-mai-mult",
        "dur": 14.5,
        "cut": 10.6,
        "final": "Costă mai mult să lucrezi așa.",
        "momente": [
            {"stil": "head", "text": "„De ce e mai scump vinul vostru?”", "la": 0.3},
            {"stil": "sub", "text": "Întrebare corectă. Răspuns scurt:", "la": 2.0},
            {"stil": "fact", "text": "Stropim minimul necesar — și pierdem producție.", "la": 3.4},
            {"stil": "fact", "text": "Culegem manual, ciorchine cu ciorchine.", "la": 5.0},
            {"stil": "fact", "text": "Macerate de plante, nu chimie de sinteză.", "la": 6.5},
            {"stil": "fact", "text": "Certificare verificată în fiecare an, de altcineva.", "la": 8.0},
        ],
    },
    {
        "id": "06-pachet-descoperire",
        "dur": 12.5,
        "momente": [
            {"stil": "head", "text": "Nu știți cu ce să începeți?", "la": 0.3},
            {"stil": "sub", "text": "Am ales noi în locul dumneavoastră.", "la": 2.0},
            {"stil": "name", "text": "Șase soiuri", "la": 3.4},
            {"stil": "fact", "text": "Fiecare sticlă vine cu o fișă: ce soi este, la ce temperatură se bea, cu ce se potrivește.", "la": 5.2},
            {"stil": "fact", "text": "Gustați șase, aflați care e al dumneavoastră.", "la": 7.8},
            {"stil": "cta", "text": "Detalii în bio", "la": 9.8},
        ],
    },
    {
        "id": "07-degustare-la-crama",
        "dur": 12.0,
        "cut": 8.4,
        "final": "Rezervări în bio.",
        "momente": [
            {"stil": "head", "text": "Se poate veni la cramă.", "la": 0.3},
            {"stil": "fact", "text": "Grupuri mici, cu programare.", "la": 2.0},
            {"stil": "fact", "text": "Vizităm crama, gustăm din butoi, povestim.", "la": 3.6},
            {"stil": "fact", "text": "În pivniță e aceeași temperatură tot anul.", "la": 5.4},
        ],
    },
]


def encode(fn, dur, path):
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        pr.stdin.write(fn(i / FPS, dur).tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit(f"ffmpeg a esuat pentru {path}")
    print(f"  {path}  {dur:.0f}s  {os.path.getsize(path)/1e6:.1f} MB")


if __name__ == "__main__":
    out = os.environ.get("OUT_DIR", "video")
    os.makedirs(out, exist_ok=True)
    for c in CLIPURI:
        print(f"  {c['id']}...")
        encode(construieste(c), c["dur"], os.path.join(out, c["id"] + ".mp4"))
    print("Gata.")
