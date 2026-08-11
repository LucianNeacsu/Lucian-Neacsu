#!/usr/bin/env python3
"""Bannere pentru magazinul online Casa Neacșu.

Construite pe fotografiile reale de produs. Fundalul fiecărui banner se
extrage din fotografie, astfel încât imaginea și tipografia să stea în
aceeași lumină, fără cusătură vizibilă.

Format: 1200x628 — dimensiunea standard pentru banner de site, card de
categorie și previzualizare la distribuire.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "brand/produse"
OUT = os.environ.get("OUT_DIR", "bannere")
W, H = 1200, 628

CREAM = (243, 238, 230)
GOLD = (201, 165, 78)
GOLD_D = (150, 118, 42)
MUTED = (176, 168, 156)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

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


def spaced(d, xy, text, f, fill, sp):
    """text cu spațiere între litere"""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + sp
    return x


def fundal(photo):
    """culoarea dominantă din marginea de sus-stânga a fotografiei"""
    px = photo.convert("RGB").resize((40, 40), Image.LANCZOS)
    zona = [px.getpixel((x, y)) for x in range(0, 10) for y in range(0, 14)]
    n = len(zona)
    return tuple(sum(c[i] for c in zona) // n for i in range(3))


def banner(spec):
    ph = Image.open(os.path.join(SRC, spec["foto"])).convert("RGB")
    baza = fundal(ph)
    # ușor mai închis, ca textul să respire
    ground = tuple(max(0, int(c * 0.82)) for c in baza)

    img = Image.new("RGB", (W, H), ground)
    d = ImageDraw.Draw(img)

    # gradient vertical discret
    for y in range(H):
        k = 1.0 - 0.18 * (y / H)
        d.line([(0, y), (W, y)], fill=tuple(int(c * k) for c in ground))

    # fotografia, în dreapta, scalată pe înălțime
    scale = H / ph.height
    nw, nh = int(ph.width * scale), H
    ph2 = ph.resize((nw, nh), Image.LANCZOS)
    px = W - nw + spec.get("shift", 0)

    # mască orizontală: marginea stângă a fotografiei se stinge în fundal
    fade = spec.get("fade", 270)
    masca = Image.new("L", (nw, nh), 255)
    md = ImageDraw.Draw(masca)
    for x in range(fade):
        md.line([(x, 0), (x, nh)], fill=int(255 * (x / fade) ** 1.4))
    masca = masca.filter(ImageFilter.GaussianBlur(2))
    img.paste(ph2, (px, 0), masca)

    d = ImageDraw.Draw(img)

    # ---- coloana de text
    x0 = 68
    colw = spec.get("colw", 470)

    f_eb = fnt(SANS_B, 15)
    y = 92
    spaced(d, (x0, y), spec.get("eyebrow", "VINURI PURE ROMÂNEȘTI"), f_eb, GOLD, 3.2)
    y += th(f_eb) + 26

    f_h = fnt(SERIF_B, spec.get("hsize", 44))
    hl = wrap(d, spec["titlu"], f_h, colw)
    for ln in hl:
        d.text((x0, y), ln, font=f_h, fill=CREAM)
        y += th(f_h) * 1.24
    y += 16

    f_b = fnt(SANS, 17)
    for ln in wrap(d, spec["text"], f_b, colw):
        d.text((x0, y), ln, font=f_b, fill=MUTED)
        y += th(f_b) * 1.55
    y += 26

    # buton
    f_c = fnt(SANS_B, 17)
    et = spec.get("cta", "Comandă pe site")
    bw = int(d.textlength(et, font=f_c)) + 52
    bh = 48
    d.rectangle([x0, y, x0 + bw, y + bh], fill=GOLD)
    d.text((x0 + 26, y + (bh - th(f_c)) / 2 - 2), et, font=f_c, fill=(28, 22, 16))
    y += bh + 24

    # semnătura de jos
    f_s = fnt(SANS, 13)
    d.text((x0, H - 54), spec.get("subsol", "Casa Neacșu · vin din struguri ecologici · Consumă responsabil 18+"),
           font=f_s, fill=(140, 132, 120))

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, spec["id"] + ".jpg")
    img.save(p, "JPEG", quality=92, optimize=True)
    print(f"  {p}")
    return p


BANNERE = [
    {
        "id": "01-hero-vinuri-de-poveste",
        "foto": "vinuri-de-poveste.jpeg",
        "eyebrow": "VINURI PURE ROMÂNEȘTI",
        "titlu": "Basmele românești, îmbuteliate",
        "text": "Balaur, Sânziana și Prâslea — trei vinuri, trei personaje, trei volume numerotate. "
                "Din soiuri românești pure, lucrate ecologic din 2010.",
        "cta": "Vezi colecția",
        "hsize": 46,
        "colw": 450,
    },
    {
        "id": "02-koson",
        "foto": "koson.jpeg",
        "eyebrow": "VINURI DE AUR",
        "titlu": "Poartă numele unei monede de aur dacice",
        "text": "Koson — Cabernet Sauvignon, Rosé și Fetească Albă. "
                "Aceeași grijă în vie ca la vinurile de colecție, la un preț de fiecare zi.",
        "cta": "Comandă Koson",
        "hsize": 40,
        "colw": 412,
    },
    {
        "id": "03-omnia-bio",
        "foto": "omnia.jpeg",
        "eyebrow": "VIN DIN STRUGURI ECOLOGICI",
        "titlu": "Omnia mea mecum porto",
        "text": "Tot ce am, port cu mine. Gama ecologică a casei, din 2010: Fetească Neagră, "
                "Băbească Neagră, Riesling Italian. Fără erbicide, fără insecticide, fără îngrășăminte de sinteză.",
        "cta": "Descoperă Omnia",
        "hsize": 44,
        "colw": 430,
    },
    {
        "id": "04-private-reserve",
        "foto": "private-reserve.jpeg",
        "eyebrow": "PRIVATE RESERVE",
        "titlu": "Cadoul care nu ajunge în sertar",
        "text": "Fetească Neagră în cutie de colecție, cu ambalaj textil și etichetă numerotată. "
                "Se personalizează pentru firme, de la [CANTITATE] pachete.",
        "cta": "Comandă cadoul",
        "hsize": 43,
        "colw": 430,
    },
    {
        "id": "05-inima",
        "foto": "inima-b.jpeg",
        "eyebrow": "SERIA INIMA",
        "titlu": "Soiuri românești pure, fără ocolișuri",
        "text": "Roșu, rosé și alb din struguri ecologici. Vinul de masă de duminică, "
                "făcut cu aceeași metodă ca vinurile de colecție.",
        "cta": "Vezi seria Inima",
        "hsize": 41,
        "colw": 430,
        "fade": 230,
    },
    {
        "id": "06-hereditas",
        "foto": "hereditas.jpeg",
        "eyebrow": "HEREDITAS · GAMĂ ECOLOGICĂ",
        "titlu": "Ce moștenim, ce lăsăm mai departe",
        "text": "Fetească Albă și Băbească Neagră, lucrate ecologic. Două soiuri românești "
                "care erau aici înaintea noastră și vor fi și după.",
        "cta": "Descoperă Hereditas",
        "hsize": 42,
        "colw": 430,
    },
    {
        "id": "07-transport-gratuit",
        "foto": "grui.jpeg",
        "eyebrow": "COMANDĂ DIRECT DE LA CRAMĂ",
        "titlu": "Transport gratuit peste [VALOARE] lei",
        "text": "Vinul pleacă din cramă și ajunge la tine în [NR] zile lucrătoare. "
                "Fără intermediari, fără drum până la Odobești.",
        "cta": "Cumpără acum",
        "hsize": 42,
        "colw": 430,
    },
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for b in BANNERE:
        banner(b)
    print(f"Gata — {len(BANNERE)} bannere in {OUT}/")
