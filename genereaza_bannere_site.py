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


def lumina(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def banner(spec):
    ph = Image.open(os.path.join(SRC, spec["foto"])).convert("RGB")
    baza = fundal(ph)
    deschis = lumina(baza) > 140

    # pe fond închis coborâm puțin fundalul, ca textul să respire;
    # pe fond deschis îl lăsăm aproape neatins, altfel apare cusătura
    k = 0.985 if deschis else 0.82
    ground = tuple(max(0, min(255, int(c * k))) for c in baza)

    if deschis:
        c_titlu, c_text, c_eb = (34, 30, 24), (104, 96, 84), GOLD_D
        c_btn, c_btn_txt, c_sub = (34, 30, 24), (247, 243, 236), (140, 132, 120)
    else:
        c_titlu, c_text, c_eb = CREAM, MUTED, GOLD
        c_btn, c_btn_txt, c_sub = GOLD, (28, 22, 16), (140, 132, 120)

    img = Image.new("RGB", (W, H), ground)
    d = ImageDraw.Draw(img)

    # gradient vertical discret
    for y in range(H):
        g = 1.0 - (0.06 if deschis else 0.18) * (y / H)
        d.line([(0, y), (W, y)], fill=tuple(min(255, int(c * g)) for c in ground))

    if spec.get("layout") == "fundal":
        # fotografia acoperă tot bannerul; textul stă peste ea
        sc = max(W / ph.width, H / ph.height)
        big = ph.resize((int(ph.width * sc) + 1, int(ph.height * sc) + 1), Image.LANCZOS)
        img.paste(big, (0, 0))
        d = ImageDraw.Draw(img)
    else:
        _compune_foto(img, ph, spec)
        d = ImageDraw.Draw(img)

    # ---- coloana de text
    _scrie_text(d, spec, c_titlu, c_text, c_eb, c_btn, c_btn_txt, c_sub)

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, spec["id"] + ".jpg")
    img.save(p, "JPEG", quality=92, optimize=True)
    print(f"  {p}")
    return p


def _compune_foto(img, ph, spec):
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


def _scrie_text(d, spec, c_titlu, c_text, c_eb, c_btn, c_btn_txt, c_sub):
    x0 = 68
    colw = spec.get("colw", 470)

    f_eb = fnt(SANS_B, 15)
    y = spec.get("ytop", 92)
    spaced(d, (x0, y), spec.get("eyebrow", "VINURI PURE ROMÂNEȘTI"), f_eb, c_eb, 3.2)
    y += th(f_eb) + 26

    f_h = fnt(SERIF_B, spec.get("hsize", 44))
    hl = wrap(d, spec["titlu"], f_h, colw)
    for ln in hl:
        d.text((x0, y), ln, font=f_h, fill=c_titlu)
        y += th(f_h) * 1.24
    y += 16

    f_b = fnt(SANS, 17)
    for ln in wrap(d, spec["text"], f_b, colw):
        d.text((x0, y), ln, font=f_b, fill=c_text)
        y += th(f_b) * 1.55
    y += 26

    # buton
    f_c = fnt(SANS_B, 17)
    et = spec.get("cta", "Comandă pe site")
    bw = int(d.textlength(et, font=f_c)) + 52
    bh = 48
    d.rectangle([x0, y, x0 + bw, y + bh], fill=c_btn)
    d.text((x0 + 26, y + (bh - th(f_c)) / 2 - 2), et, font=f_c, fill=c_btn_txt)
    y += bh + 24

    # semnătura de jos
    f_s = fnt(SANS, 13)
    d.text((x0, H - 54), spec.get("subsol", "Casa Neacșu · vin din struguri ecologici · Consumă responsabil 18+"),
           font=f_s, fill=c_sub)


BANNERE = [
    {
        "id": "01-private-reserve",
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
        "id": "02-grui",
        "foto": "grui.jpeg",
        "eyebrow": "SERIA GRUI",
        "titlu": "Vinul poartă numele dealului din care vine",
        "text": "Grui — dealul pe care crește via. Fetească Neagră și Sauvignon Blanc, "
                "din soiuri lucrate ecologic, cu stropiri reduse la minimul necesar.",
        "cta": "Descoperă Grui",
        "hsize": 40,
        "colw": 420,
    },
    {
        "id": "03-hereditas",
        "foto": "hereditas.jpeg",
        "eyebrow": "HEREDITAS · GAMĂ ECOLOGICĂ",
        "titlu": "Ce moștenim, ce lăsăm mai departe",
        "text": "Băbească Neagră, Chardonnay și Riesling Italian, din Însurăței. Pe etichetă, "
                "dropul de pe Terasele Dunării — pasărea locului, semnul legăturii dintre om și pământ.",
        "cta": "Descoperă Hereditas",
        "hsize": 42,
        "colw": 430,
    },
    {
        "id": "04-glia",
        "foto": "glia-a.jpeg",
        "eyebrow": "SERIA GLIA · ȘARBĂ",
        "titlu": "Glie: pământ roditor",
        "text": "Șarba se simte acasă la Odobești și aproape nicăieri altundeva. Gama de vârf a "
                "soiurilor românești, învechită minimum trei ani la sticlă.",
        "cta": "Comandă Glia",
        "hsize": 46,
        "colw": 400,
        "fade": 200,
    },
    {
        "id": "05-casa-neacsu",
        "foto": "casa-neacsu-pachet.jpeg",
        "eyebrow": "CASA NEACȘU · PACHET DE COLECȚIE",
        "titlu": "Trei albe într-o cutie de colecție",
        "text": "Sauvignon Blanc & Riesling Italian, Muscat Ottonel și Crâmpoșie. Rădăcina de pe "
                "etichetă spune tot: aceleași soiuri, același deal, lucrate ecologic. "
                "Cadou gata făcut sau primul pas prin gamele casei.",
        "cta": "Comandă pachetul",
        "hsize": 42,
        "colw": 560,
        "fade": 220,
    },
    {
        "id": "06-transport-gratuit",
        "foto": "inima-a.jpeg",
        "eyebrow": "COMANDĂ DIRECT DE LA CRAMĂ",
        "titlu": "Transport gratuit peste [VALOARE] lei",
        "text": "Vinul pleacă din cramă și ajunge la tine în [NR] zile lucrătoare. "
                "Fără intermediari, fără drum până la Odobești.",
        "cta": "Cumpără acum",
        "hsize": 42,
        "colw": 430,
        "fade": 230,
    },
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for b in BANNERE:
        banner(b)
    print(f"Gata — {len(BANNERE)} bannere in {OUT}/")
