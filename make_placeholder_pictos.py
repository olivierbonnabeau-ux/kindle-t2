"""Génère quelques pictos de secours (simples silhouettes) dans ./pictos/cam et
./pictos/oliv, pour que l'écran ait quelque chose à afficher tant que tu n'as pas
mis tes propres PNG. Remplace-les librement (PNG, idéalement ~200×200, fond
transparent ou blanc)."""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent


def face(size=200, hat=False, glasses=False, smile=True, hair="short"):
    im = Image.new("L", (size, size), 255)
    d = ImageDraw.Draw(im)
    c = size // 2
    d.ellipse((c - 70, c - 70, c + 70, c + 70), outline=0, width=6, fill=255)   # tête
    if hair == "long":
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=0)
        d.rectangle((c - 72, c - 20, c - 52, c + 60), fill=0)
        d.rectangle((c + 52, c - 20, c + 72, c + 60), fill=0)
    elif hair == "short":
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=0)
    if hat:
        d.rectangle((c - 60, c - 100, c + 60, c - 60), fill=0)
        d.rectangle((c - 85, c - 64, c + 85, c - 52), fill=0)
    d.ellipse((c - 32, c - 14, c - 16, c + 2), fill=0)                          # yeux
    d.ellipse((c + 16, c - 14, c + 32, c + 2), fill=0)
    if glasses:
        d.ellipse((c - 42, c - 24, c - 6, c + 12), outline=0, width=4)
        d.ellipse((c + 6, c - 24, c + 42, c + 12), outline=0, width=4)
        d.line((c - 6, c - 6, c + 6, c - 6), fill=0, width=4)
    if smile:
        d.arc((c - 30, c + 10, c + 30, c + 50), 10, 170, fill=0, width=5)
    else:
        d.line((c - 25, c + 35, c + 25, c + 35), fill=0, width=5)
    return im


def main():
    sets = {
        "cam": [("lundi", dict(hair="long")), ("soleil", dict(hair="long", glasses=True)),
                ("pluie", dict(hair="long", hat=True)), ("zen", dict(hair="long", smile=False))],
        "oliv": [("lundi", dict(hair="short")), ("soleil", dict(hair="short", glasses=True)),
                 ("pluie", dict(hair="short", hat=True)), ("zen", dict(hair="short", smile=False))],
    }
    for key, items in sets.items():
        folder = HERE / "pictos" / key
        folder.mkdir(parents=True, exist_ok=True)
        for name, kw in items:
            face(**kw).save(folder / f"{name}.png")
            print("écrit", folder / f"{name}.png")


if __name__ == "__main__":
    main()
