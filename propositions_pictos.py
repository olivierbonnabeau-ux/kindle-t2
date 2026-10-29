"""Planche de propositions de pictos (200×200, niveaux de gris) pour Cam et Oliv.
Génère propositions_pictos.png (planche) et pictos_propositions/<style>/<cam|oliv>.png."""
import math
from pathlib import Path

from PIL import Image, ImageDraw

from render import font

HERE = Path(__file__).resolve().parent
OUT = HERE / "pictos_propositions"
S = 200
W, B = 255, 0


def canvas():
    im = Image.new("L", (S, S), W)
    return im, ImageDraw.Draw(im)


# ---------------------------------------------------------------- 1. Initiales
def style_initiale(name):
    im, d = canvas()
    d.ellipse((10, 10, S - 10, S - 10), fill=B)
    d.text((S / 2, S / 2 + 4), name[0].upper(), fill=W, font=font(120, bold=True), anchor="mm")
    return im


# ---------------------------------------------------------------- 2. Marcheur (signalétique)
def style_marcheur(name, female):
    im, d = canvas()
    cx = S / 2
    d.ellipse((cx - 22, 14, cx + 22, 58), fill=B)                       # tête
    # torse incliné vers l'avant
    d.line((cx - 2, 60, cx + 14, 118), fill=B, width=26)
    if female:  # jupe trapèze
        d.polygon([(cx - 30, 118), (cx + 42, 118), (cx + 48, 128), (cx - 36, 128)], fill=B)
    # jambes en marche
    d.line((cx + 12, 116, cx - 24, 170), fill=B, width=20)
    d.line((cx - 24, 170, cx - 14, 192), fill=B, width=20)
    d.line((cx + 14, 116, cx + 46, 160), fill=B, width=20)
    d.line((cx + 46, 160, cx + 70, 150), fill=B, width=18)
    # bras
    d.line((cx + 4, 76, cx + 44, 104), fill=B, width=18)
    d.line((cx + 2, 76, cx - 34, 92), fill=B, width=18)
    d.line((cx - 34, 92, cx - 26, 118), fill=B, width=16)
    return im


# ---------------------------------------------------------------- 3. Badge tram
def style_badge(name):
    im, d = canvas()
    d.rounded_rectangle((8, 8, S - 8, S - 8), radius=36, outline=B, width=8)
    # petit tram
    tx, ty = S / 2, 68
    d.rounded_rectangle((tx - 56, ty - 34, tx + 56, ty + 26), radius=14, fill=B)
    d.rectangle((tx - 44, ty - 24, tx - 6, ty - 2), fill=W)
    d.rectangle((tx + 6, ty - 24, tx + 44, ty - 2), fill=W)
    d.ellipse((tx - 42, ty + 20, tx - 22, ty + 40), fill=B)
    d.ellipse((tx + 22, ty + 20, tx + 42, ty + 40), fill=B)
    d.line((tx, ty - 34, tx, ty - 52), fill=B, width=5)
    d.line((tx - 14, ty - 52, tx + 14, ty - 52), fill=B, width=5)
    d.text((S / 2, 150), name, fill=B, font=font(52, bold=True), anchor="mm")
    return im


# ---------------------------------------------------------------- 4. Visage minimal (traits fins, expressions)
def style_minimal(name, female, mood="neutre"):
    im, d = canvas()
    c = S / 2
    d.ellipse((c - 70, c - 60, c + 70, c + 80), outline=B, width=7)
    if female:
        d.arc((c - 78, c - 72, c + 78, c + 40), 190, 350, fill=B, width=16)
        d.line((c - 74, c - 20, c - 74, c + 50), fill=B, width=14)
        d.line((c + 74, c - 20, c + 74, c + 50), fill=B, width=14)
    else:
        d.arc((c - 72, c - 66, c + 72, c + 30), 195, 345, fill=B, width=14)
    d.ellipse((c - 34, c - 10, c - 20, c + 4), fill=B)
    d.ellipse((c + 20, c - 10, c + 34, c + 4), fill=B)
    if mood == "sourire":
        d.arc((c - 30, c + 10, c + 30, c + 52), 15, 165, fill=B, width=6)
    elif mood == "endormi":
        d.line((c - 36, c - 4, c - 18, c - 4), fill=B, width=6)
        d.line((c + 18, c - 4, c + 36, c - 4), fill=B, width=6)
        d.line((c - 14, c + 36, c + 14, c + 36), fill=B, width=6)
        d.text((c + 60, c - 70), "z", fill=B, font=font(28, bold=True), anchor="mm")
        d.text((c + 82, c - 92), "Z", fill=B, font=font(34, bold=True), anchor="mm")
    else:
        d.line((c - 18, c + 36, c + 18, c + 36), fill=B, width=6)
    return im


# ---------------------------------------------------------------- 5. Animal totem (chat / renard)
def style_animal(kind):
    im, d = canvas()
    c = S / 2
    if kind == "chat":
        d.polygon([(c - 70, c + 10), (c - 62, c - 70), (c - 20, c - 34)], fill=B)
        d.polygon([(c + 70, c + 10), (c + 62, c - 70), (c + 20, c - 34)], fill=B)
        d.ellipse((c - 72, c - 40, c + 72, c + 80), fill=B)
        d.ellipse((c - 40, c - 2, c - 16, c + 18), fill=W)
        d.ellipse((c + 16, c - 2, c + 40, c + 18), fill=W)
        d.ellipse((c - 31, c + 2, c - 25, c + 16), fill=B)
        d.ellipse((c + 25, c + 2, c + 31, c + 16), fill=B)
        d.polygon([(c - 8, c + 30), (c + 8, c + 30), (c, c + 40)], fill=W)
        for y in (c + 34, c + 44):
            d.line((c - 90, y, c - 40, y + 2), fill=B, width=4)
            d.line((c + 40, y + 2, c + 90, y), fill=B, width=4)
    else:  # renard
        d.polygon([(c - 76, c - 20), (c - 70, c - 80), (c - 26, c - 40)], fill=B)
        d.polygon([(c + 76, c - 20), (c + 70, c - 80), (c + 26, c - 40)], fill=B)
        d.polygon([(c - 78, c - 24), (c + 78, c - 24), (c, c + 84)], fill=B)
        d.polygon([(c - 52, c - 24), (c, c + 62), (c + 52, c - 24)], fill=W)
        d.ellipse((c - 30, c - 16, c - 14, c + 0), fill=B)
        d.ellipse((c + 14, c - 16, c + 30, c + 0), fill=B)
        d.ellipse((c - 9, c + 30, c + 9, c + 48), fill=B)
    return im


# ---------------------------------------------------------------- 6. Météo + initiale (varie selon le temps)
def style_meteo(name, weather):
    im, d = canvas()
    c = S / 2
    if weather == "soleil":
        d.ellipse((c - 38, c - 38, c + 38, c + 38), outline=B, width=10)
        for i in range(12):
            a = i * math.pi / 6
            d.line((c + 52 * math.cos(a), c + 52 * math.sin(a), c + 78 * math.cos(a), c + 78 * math.sin(a)), fill=B, width=9)
    elif weather == "pluie":
        d.pieslice((c - 80, c - 90, c + 80, c + 70), 180, 360, fill=B)
        d.rectangle((c - 80, c - 10, c + 80, c + 0), fill=B)
        d.line((c, c - 10, c, c + 70), fill=B, width=9)
        d.arc((c - 2, c + 50, c + 34, c + 86), 0, 180, fill=B, width=9)
        for x in (-60, -30, 30, 60):
            d.line((c + x, c + 30, c + x - 8, c + 60), fill=B, width=6)
    else:  # neige / froid
        for i in range(6):
            a = i * math.pi / 3
            d.line((c, c, c + 76 * math.cos(a), c + 76 * math.sin(a)), fill=B, width=9)
            for t in (0.55,):
                px, py = c + 76 * t * math.cos(a), c + 76 * t * math.sin(a)
                for s in (-1, 1):
                    b = a + s * math.pi / 5
                    d.line((px, py, px + 22 * math.cos(b), py + 22 * math.sin(b)), fill=B, width=7)
    # cartouche initiale
    d.ellipse((S - 70, S - 70, S - 8, S - 8), fill=B)
    d.text((S - 39, S - 36), name[0].upper(), fill=W, font=font(40, bold=True), anchor="mm")
    return im


def main():
    styles = [
        ("1 Initiale", lambda p: style_initiale(p)),
        ("2 Marcheur", lambda p: style_marcheur(p, p == "Cam")),
        ("3 Badge tram", lambda p: style_badge(p)),
        ("4 Visage minimal", lambda p: style_minimal(p, p == "Cam", "sourire" if p == "Oliv" else "neutre")),
        ("5 Animal totem", lambda p: style_animal("chat" if p == "Cam" else "renard")),
        ("6 Météo + initiale", lambda p: style_meteo(p, "soleil" if p == "Cam" else "pluie")),
    ]
    cols, rows = 2, len(styles)
    pad, label_w = 24, 300
    sheet = Image.new("L", (label_w + cols * (S + pad) + pad, rows * (S + pad) + pad), W)
    d = ImageDraw.Draw(sheet)
    for r, (label, fn) in enumerate(styles):
        y = pad + r * (S + pad)
        d.text((pad, y + S / 2), label, fill=B, font=font(26, bold=True), anchor="lm")
        for ci, p in enumerate(("Cam", "Oliv")):
            im = fn(p)
            x = label_w + pad + ci * (S + pad)
            sheet.paste(im, (x, y))
            d.rectangle((x, y, x + S - 1, y + S - 1), outline=200)
            key = label.split(" ", 1)[1].lower().replace(" ", "_").replace("+", "et")
            folder = OUT / key / p.lower()
            folder.mkdir(parents=True, exist_ok=True)
            im.save(folder / "base.png")
    # variantes humeur / météo pour les styles 4 et 6
    for p in ("Cam", "Oliv"):
        f = OUT / "visage_minimal" / p.lower()
        for mood in ("neutre", "sourire", "endormi"):
            style_minimal(p, p == "Cam", mood).save(f / f"{mood}.png")
        f = OUT / "météo_et_initiale" / p.lower()
        for wx in ("soleil", "pluie", "neige"):
            style_meteo(p, wx).save(f / f"{wx}.png")
    sheet.save(HERE / "propositions_pictos.png")
    print("planche :", HERE / "propositions_pictos.png")


if __name__ == "__main__":
    main()
