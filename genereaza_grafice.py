#!/usr/bin/env python3
"""Generează grafice gata de postat pentru Cramele Odobești.

Formate: Facebook 1080x1350 și TikTok/Reels 1080x1920.
Fără fotografii — doar tipografie, în paleta cramei.
Layoutul se auto-scalează până când tot conținutul încape în cadru.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.environ.get("OUT_DIR", "grafice")

CREAM = (251, 247, 243)
BURGUNDY = (94, 16, 38)
GOLD = (154, 123, 39)
INK = (38, 38, 38)
GREY = (110, 110, 110)
LIGHT = (222, 211, 200)
DARK_RULE = (126, 62, 78)
DARK_MUTED = (214, 194, 186)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

_fc = {}


def fnt(path, size):
    k = (path, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, max(10, int(size)))
    return _fc[k]


def th(f):
    b = f.getbbox("Ághșț")
    return b[3] - b[1]


def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def body_layout(draw, d, inner, s, x0, y0, paint):
    """Măsoară (și opțional desenează) blocul de conținut. Întoarce înălțimea."""
    kind = d["kind"]
    fg, accent, muted, rule = d["_fg"], d["_accent"], d["_muted"], d["_rule"]
    y = y0

    if kind == "pairs":
        f_l, f_r = fnt(SANS, 34 * s), fnt(SANS_B, 37 * s)
        for i, (left, right) in enumerate(d["items"]):
            for ln in wrap(draw, left, f_l, inner):
                if paint:
                    draw.text((x0, y), ln, font=f_l, fill=muted)
                y += th(f_l) + 11 * s
            for ln in wrap(draw, right, f_r, inner):
                if paint:
                    draw.text((x0, y), ln, font=f_r, fill=accent)
                y += th(f_r) + 8 * s
            if i < len(d["items"]) - 1:
                if paint:
                    draw.line([(x0, y + 14 * s), (x0 + inner, y + 14 * s)], fill=rule, width=2)
                y += 36 * s

    elif kind == "numbered":
        f_n, f_t, f_b = fnt(SERIF_B, 52 * s), fnt(SANS_B, 40 * s), fnt(SANS, 33 * s)
        ind = 92 * s
        for i, (title, body) in enumerate(d["items"], 1):
            if paint:
                draw.text((x0, y), str(i), font=f_n, fill=GOLD)
                draw.text((x0 + ind, y + 6 * s), title, font=f_t, fill=accent)
            y += max(th(f_n), th(f_t)) + 16 * s
            for ln in wrap(draw, body, f_b, inner - ind):
                if paint:
                    draw.text((x0 + ind, y), ln, font=f_b, fill=muted)
                y += th(f_b) + 12 * s
            if i < len(d["items"]):
                y += 42 * s

    elif kind == "checks":
        f = fnt(SANS, 40 * s)
        ind = 74 * s
        for i, it in enumerate(d["items"]):
            if paint:
                cy = y + th(f) * 0.55
                draw.line([(x0 + 4 * s, cy), (x0 + 20 * s, cy + 14 * s)], fill=GOLD, width=max(3, int(6 * s)))
                draw.line([(x0 + 20 * s, cy + 14 * s), (x0 + 46 * s, cy - 16 * s)], fill=GOLD, width=max(3, int(6 * s)))
            for ln in wrap(draw, it, f, inner - ind):
                if paint:
                    draw.text((x0 + ind, y), ln, font=f, fill=fg)
                y += th(f) + 12 * s
            if i < len(d["items"]) - 1:
                y += 28 * s

    elif kind == "big":
        f_big, f_sub = fnt(SERIF_B, 270 * s), fnt(SANS, 39 * s)
        if paint:
            draw.text((x0, y), d["big"], font=f_big, fill=accent)
        y += th(f_big) + 44 * s
        for ln in wrap(draw, d["sub"], f_sub, inner):
            if paint:
                draw.text((x0, y), ln, font=f_sub, fill=fg)
            y += th(f_sub) + 13 * s

    elif kind == "quote":
        f_q = fnt(SERIF_B, 76 * s)
        for ln in wrap(draw, d["quote"], f_q, inner):
            if paint:
                draw.text((x0, y), ln, font=f_q, fill=fg)
            y += th(f_q) + 26 * s

    elif kind == "words":
        f_w = fnt(SERIF_B, 88 * s)
        for i, it in enumerate(d["items"]):
            if paint:
                draw.text((x0, y), it, font=f_w, fill=accent)
            y += th(f_w) + (32 * s if i < len(d["items"]) - 1 else 0)

    return y - y0


def compose(draw, d, W, H, s, paint):
    """Așază toate elementele la scara s. Întoarce True dacă încape."""
    margin = 92 * s
    inner = W - 2 * margin
    fg, accent, muted, rule = d["_fg"], d["_accent"], d["_muted"], d["_rule"]

    f_k = fnt(SANS_B, 26 * s)
    kick_y = margin + 14 * s
    top = kick_y + th(f_k) + 66 * s

    f_h = fnt(SERIF_B, d.get("hsize", 74) * s)
    hlines = wrap(draw, d["headline"], f_h, inner) if d.get("headline") else []
    head_h = sum(th(f_h) + 20 * s for _ in hlines)

    f_s2 = fnt(SANS, 33 * s)
    slines = wrap(draw, d["kicker2"], f_s2, inner) if d.get("kicker2") else []
    sub_h = (sum(th(f_s2) + 11 * s for _ in slines) + 20 * s) if slines else 0

    f_f = fnt(SANS, 25 * s)
    foot_y = H - margin - th(f_f) - 14 * s

    body_h = body_layout(draw, d, inner, s, margin, 0, False)

    gap = 50 * s
    total = head_h + sub_h + (gap if (hlines or slines) else 0) + body_h
    avail_bot = foot_y - 52 * s
    if total > (avail_bot - top):
        return False
    if not paint:
        return True

    # grupul întreg (titlu + subtitlu + conținut) se centrează vertical
    top = top + max(0, (avail_bot - top - total) / 2)

    # kicker
    draw.text((margin, kick_y), "CRAMELE ODOBEȘTI", font=f_k, fill=GOLD)
    kw = draw.textlength("CRAMELE ODOBEȘTI", font=f_k)
    draw.line([(margin, kick_y + th(f_k) + 18 * s), (margin + kw, kick_y + th(f_k) + 18 * s)],
              fill=GOLD, width=max(2, int(3 * s)))

    y = top
    for ln in hlines:
        draw.text((margin, y), ln, font=f_h, fill=fg)
        y += th(f_h) + 20 * s
    if slines:
        y += 20 * s
        for ln in slines:
            draw.text((margin, y), ln, font=f_s2, fill=muted)
            y += th(f_s2) + 11 * s

    body_layout(draw, d, inner, s, margin, y + (gap if (hlines or slines) else 0), True)

    draw.line([(margin, foot_y - 24 * s), (W - margin, foot_y - 24 * s)], fill=rule, width=2)
    draw.text((margin, foot_y), d.get("footer", "Consumă responsabil · 18+"), font=f_f, fill=muted)
    return True


def render(design, W, H, path):
    dark = design.get("dark", False)
    d = dict(design)
    d["_fg"] = CREAM if dark else INK
    d["_accent"] = GOLD if dark else BURGUNDY
    d["_muted"] = DARK_MUTED if dark else GREY
    d["_rule"] = DARK_RULE if dark else LIGHT

    img = Image.new("RGB", (W, H), BURGUNDY if dark else CREAM)
    draw = ImageDraw.Draw(img)

    s = 1.0
    while s > 0.42 and not compose(draw, d, W, H, s, False):
        s -= 0.02
    compose(draw, d, W, H, s, True)

    m = 92 * s
    draw.rectangle([m / 2, m / 2, W - m / 2, H - m / 2],
                   outline=(190, 160, 90) if dark else GOLD, width=max(2, int(3 * s)))

    img.save(path, "PNG", optimize=True)
    return round(s, 2)


DESIGNS = [
    {
        "id": "01-asociere-mancare",
        "headline": "Ce pui în pahar, după ce ai în farfurie",
        "kind": "pairs",
        "items": [
            ("Pește, fructe de mare, salate", "Șarbă · Fetească Regală"),
            ("Pui la cuptor, paste în sos alb", "Riesling Italian · Omnia"),
            ("Brânzeturi maturate, aperitive", "Fetească Albă"),
            ("Sarmale, friptură, grătar", "Băbească Neagră"),
            ("Vânat, carne roșie la cuptor", "Fetească Neagră · Occultus"),
            ("Deserturi cu fructe", "Busuioacă de Bohotin · Suav"),
        ],
    },
    {
        "id": "02-ce-inseamna-ecologic",
        "headline": "Ce înseamnă, concret, ecologic",
        "kicker2": "La noi, din 2010. Verificat anual de un organism independent.",
        "kind": "checks",
        "items": [
            "Fără erbicide pe rândul de viță",
            "Fără îngrășăminte de sinteză",
            "Fără insecticide",
            "Stropit doar minimul necesar",
            "Macerate de plante, preparate în cramă",
            "Cules manual, procesat în aceeași zi",
        ],
    },
    {
        "id": "03-trei-greseli",
        "headline": "Trei greșeli la servirea vinului",
        "kind": "numbered",
        "items": [
            ("Temperatura", "Alb 10–12°, roșu 16–18°. Roșul ținut la cameră caldă are nevoie de 15 minute la frigider."),
            ("Paharul plin", "Se umple o treime. Restul e loc pentru aromă — de aceea are paharul forma aceea."),
            ("Fără aerisire", "Un roșu tânăr are nevoie de 20 de minute în carafă sau măcar în pahar."),
        ],
    },
    {
        "id": "04-mesaj-semnatura",
        "headline": "",
        "kind": "quote",
        "quote": "Ne doare pe noi capul, ca să nu fie nevoie de scurtături.",
        "dark": True,
        "footer": "Cramele Odobești · Consumă responsabil · 18+",
    },
    {
        "id": "05-bio-din-2010",
        "headline": "Lucrăm ecologic din",
        "kind": "big",
        "big": "2010",
        "sub": "Printre primii din România care au convertit suprafețe de peste 15 hectare. Nu pentru că era la modă — atunci nu era.",
    },
    {
        "id": "06-soiuri-rare",
        "headline": "Soiuri pe care aproape nimeni nu le mai lucrează",
        "kind": "words",
        "items": ["Zghihara", "Crâmpoșie", "Băbească Gri", "Cadarcă"],
        "footer": "Gama Monșer · Consumă responsabil · 18+",
    },
    {
        "id": "07-citeste-eticheta",
        "headline": "Cum se citește o etichetă",
        "kind": "numbered",
        "items": [
            ("D.O.C.", "Denumire de Origine Controlată: strugurii vin dintr-o zonă delimitată și verificată."),
            ("Soiul și anul", "Dacă lipsesc, este cupaj de ani și de soiuri. Nu e rău — dar e bine să știți."),
            ("Sigla ecologică", "Frunza din stele nu se pune singură. Se obține prin control anual."),
        ],
    },
    {
        "id": "08-metoda",
        "headline": "Ce punem, de fapt, pe vie",
        "kicker2": "Macerate de plante, preparate în curtea cramei.",
        "kind": "checks",
        "items": [
            "Stropim doar când via are nevoie",
            "Nu preventiv, nu după calendar",
            "Macerate de plante în locul chimiei",
            "Pierdem din producție în fiecare an",
            "Este o alegere, nu un accident",
        ],
        "dark": True,
    },
]

FORMATE = [("fb", 1080, 1350), ("tiktok", 1080, 1920)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for d in DESIGNS:
        for tag, W, H in FORMATE:
            s = render(d, W, H, os.path.join(OUT, f"{d['id']}-{tag}.png"))
            n += 1
            if s < 0.99:
                print(f"  {d['id']}-{tag}: scalat la {s}")
    print(f"Generate {n} imagini in {OUT}/")
