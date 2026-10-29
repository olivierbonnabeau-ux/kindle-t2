"""Visages paramétrables dans le style des pictos actuels (contour épais, cheveux en calotte).

    python make_pictos.py sheet   → planche variations_visages.png (toutes les variantes)
    python make_pictos.py build   → écrit les pictos retenus dans pictos/cam et pictos/oliv

Chaque variante = dict d'options : hair, eyes, mouth, glasses, hat, extra.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from render import font

HERE = Path(__file__).resolve().parent
S = 200
W, B = 255, 0


def face(hair="short", eyes="open", mouth="smile", glasses=None, hat=None, extra=None, beard=False):
    im = Image.new("L", (S, S), W)
    d = ImageDraw.Draw(im)
    c = S // 2
    # ---- tête
    d.ellipse((c - 70, c - 70, c + 70, c + 70), outline=B, width=6, fill=W)
    # ---- cheveux
    if hair == "long":
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=B)
        d.rectangle((c - 72, c - 20, c - 52, c + 60), fill=B)
        d.rectangle((c + 52, c - 20, c + 72, c + 60), fill=B)
    elif hair == "bob":  # carré court
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=B)
        d.rectangle((c - 72, c - 20, c - 54, c + 20), fill=B)
        d.rectangle((c + 54, c - 20, c + 72, c + 20), fill=B)
    elif hair == "bun":  # chignon
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        d.ellipse((c - 24, c - 112, c + 24, c - 64), fill=B)
    elif hair == "ponytail":
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        d.ellipse((c + 48, c - 50, c + 80, c + 50), fill=B)
    elif hair == "fringe":  # frange droite
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=B)
        d.rectangle((c - 72, c - 20, c - 52, c + 60), fill=B)
        d.rectangle((c + 52, c - 20, c + 72, c + 60), fill=B)
        d.rectangle((c - 50, c - 40, c + 50, c - 24), fill=B)
    elif hair == "short":
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
    elif hair == "spiky":
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for x in (-40, -14, 12, 38):
            d.polygon([(c + x - 12, c - 56), (c + x, c - 98), (c + x + 12, c - 56)], fill=B)
    elif hair == "curly":
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for i in range(7):
            a = math.pi + i * math.pi / 6
            d.ellipse((c + 66 * math.cos(a) - 14, c - 6 + 66 * math.sin(a) - 14,
                       c + 66 * math.cos(a) + 14, c - 6 + 66 * math.sin(a) + 14), fill=B)
    elif hair == "bald":
        pass
    # ---- cheveux en pétard (plusieurs degrés)
    elif hair == "petard":  # épis irréguliers tout autour du sommet
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for i, (x, h, w, lean) in enumerate(((-58, 30, 12, -10), (-40, 46, 14, -6), (-22, 38, 12, 4), (-4, 54, 14, 2),
                                            (14, 40, 12, 8), (32, 50, 14, 10), (50, 34, 12, 14))):
            d.polygon([(c + x - w, c - 60), (c + x + lean, c - 60 - h), (c + x + w, c - 60)], fill=B)
    elif hair == "petard_fou":  # mèches longues et désordonnées
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for x, y2, w in ((-64, -118, 10), (-46, -132, 12), (-26, -124, 10), (-8, -144, 12), (10, -128, 10),
                         (30, -140, 12), (48, -120, 10), (64, -108, 10), (-76, -96, 9), (78, -92, 9)):
            d.line((c + x * 0.8, c - 62, c + x, c + y2), fill=B, width=w)
            d.ellipse((c + x - w // 2, c + y2 - w // 2, c + x + w // 2, c + y2 + w // 2), fill=B)
    elif hair == "petard_reveil":  # touffes aplaties d'un côté, dressées de l'autre (oreiller)
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        d.line((c - 70, c - 50, c - 100, c - 30), fill=B, width=12)
        d.line((c - 60, c - 66, c - 96, c - 60), fill=B, width=12)
        for x, h in ((0, 40), (18, 58), (36, 48), (54, 36)):
            d.polygon([(c + x - 10, c - 62), (c + x + 6, c - 62 - h), (c + x + 12, c - 60)], fill=B)
    elif hair == "crete":  # crête iroquoise
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for x, h in ((-30, 40), (-18, 62), (-6, 78), (6, 84), (18, 74), (30, 56), (40, 36)):
            d.polygon([(c + x - 9, c - 62), (c + x, c - 62 - h), (c + x + 9, c - 62)], fill=B)
    elif hair == "boule":  # boule ébouriffée (gros nuage de cheveux)
        d.ellipse((c - 84, c - 128, c + 84, c - 10), fill=B)
        for i in range(10):
            a = math.pi + i * math.pi / 9
            x, y = c + 84 * math.cos(a), c - 69 + 60 * math.sin(a)
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=B)
        d.ellipse((c - 70, c - 70, c + 70, c + 70), outline=B, width=6, fill=W)
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
    elif hair == "herisson":  # courts mais hérissés partout (brosse)
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for i in range(11):
            a = math.pi + i * math.pi / 10
            x0, y0 = c + 64 * math.cos(a), c - 8 + 64 * math.sin(a)
            x1, y1 = c + 90 * math.cos(a), c - 8 + 92 * math.sin(a)
            d.line((x0, y0, x1, y1), fill=B, width=9)
    # ---- coiffures supplémentaires pour Camille
    elif hair == "wavy":  # longs et ondulés (bords festonnés)
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=B)
        for side in (-1, 1):
            for i, y in enumerate(range(c - 30, c + 70, 20)):
                r = 16 if i % 2 == 0 else 20
                d.ellipse((c + side * 64 - r, y - r, c + side * 64 + r, y + r), fill=B)
    elif hair == "braids":  # deux tresses
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for side in (-1, 1):
            x = c + side * 68
            for i, y in enumerate(range(c - 10, c + 90, 18)):
                r = 12 if i % 2 == 0 else 10
                d.ellipse((x - r, y - r, x + r, y + r), fill=B)
            d.polygon([(x - 8, c + 90), (x + 8, c + 90), (x + 4, c + 108), (x - 4, c + 108)], fill=B)
    elif hair == "halfup":  # demi-queue : longs + petit chignon au sommet
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=B)
        d.rectangle((c - 72, c - 20, c - 52, c + 60), fill=B)
        d.rectangle((c + 52, c - 20, c + 72, c + 60), fill=B)
        d.ellipse((c - 18, c - 104, c + 18, c - 68), fill=B)
    elif hair == "bun_loose":  # chignon flou avec mèches qui s'échappent
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        d.ellipse((c - 28, c - 116, c + 28, c - 62), fill=B)
        d.line((c - 60, c - 50, c - 84, c - 10), fill=B, width=7)
        d.line((c + 60, c - 50, c + 84, c - 10), fill=B, width=7)
        d.line((c - 10, c - 104, c - 40, c - 128), fill=B, width=6)
        d.line((c + 14, c - 108, c + 44, c - 126), fill=B, width=6)
    elif hair == "headband":  # longs avec bandeau clair
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=B)
        d.rectangle((c - 72, c - 20, c - 52, c + 60), fill=B)
        d.rectangle((c + 52, c - 20, c + 72, c + 60), fill=B)
        d.arc((c - 76, c - 84, c + 76, c + 20), 200, 340, fill=W, width=12)
        d.arc((c - 76, c - 84, c + 76, c + 20), 200, 340, fill=B, width=4)
    elif hair == "curly_long":  # longs et bouclés
        d.chord((c - 72, c - 80, c + 72, c + 40), 180, 360, fill=B)
        for side in (-1, 1):
            for i, y in enumerate(range(c - 40, c + 80, 16)):
                x = c + side * (62 + (8 if i % 2 else 0))
                d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=B)
    elif hair == "pixie":  # très court, mèche sur le front
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        d.chord((c - 74, c - 70, c + 20, c - 10), 150, 330, fill=B)
    elif hair == "petard_vent":  # tout penché d'un côté, comme dans le vent
        d.chord((c - 70, c - 76, c + 70, c + 10), 180, 360, fill=B)
        for x, h in ((-60, 26), (-44, 40), (-28, 50), (-12, 58), (4, 62), (20, 58), (36, 48)):
            d.polygon([(c + x - 10, c - 60), (c + x + 34, c - 60 - h), (c + x + 12, c - 60)], fill=B)
    if beard:
        d.chord((c - 56, c + 4, c + 56, c + 76), 20, 160, fill=B)
        d.ellipse((c - 22, c + 26, c + 22, c + 50), fill=W)
    # ---- yeux
    ey = c - 6
    if eyes == "open":
        d.ellipse((c - 32, ey - 8, c - 16, ey + 8), fill=B)
        d.ellipse((c + 16, ey - 8, c + 32, ey + 8), fill=B)
    elif eyes == "closed":
        d.arc((c - 36, ey - 10, c - 12, ey + 10), 20, 160, fill=B, width=5)
        d.arc((c + 12, ey - 10, c + 36, ey + 10), 20, 160, fill=B, width=5)
    elif eyes == "wink":
        d.ellipse((c - 32, ey - 8, c - 16, ey + 8), fill=B)
        d.arc((c + 12, ey - 10, c + 36, ey + 10), 20, 160, fill=B, width=5)
    elif eyes == "sleepy":
        d.line((c - 34, ey, c - 14, ey), fill=B, width=6)
        d.line((c + 14, ey, c + 34, ey), fill=B, width=6)
    elif eyes == "wide":
        d.ellipse((c - 36, ey - 12, c - 12, ey + 12), outline=B, width=5)
        d.ellipse((c + 12, ey - 12, c + 36, ey + 12), outline=B, width=5)
        d.ellipse((c - 28, ey - 4, c - 20, ey + 4), fill=B)
        d.ellipse((c + 20, ey - 4, c + 28, ey + 4), fill=B)
    elif eyes == "hearts":
        for x in (c - 24, c + 24):
            d.ellipse((x - 14, ey - 12, x, ey + 2), fill=B)
            d.ellipse((x, ey - 12, x + 14, ey + 2), fill=B)
            d.polygon([(x - 13, ey - 2), (x + 13, ey - 2), (x, ey + 14)], fill=B)
    elif eyes == "stars":
        for x in (c - 24, c + 24):
            pts = []
            for i in range(10):
                r = 14 if i % 2 == 0 else 6
                a = -math.pi / 2 + i * math.pi / 5
                pts.append((x + r * math.cos(a), ey + r * math.sin(a)))
            d.polygon(pts, fill=B)
    elif eyes == "angry":
        d.ellipse((c - 32, ey - 6, c - 16, ey + 10), fill=B)
        d.ellipse((c + 16, ey - 6, c + 32, ey + 10), fill=B)
        d.line((c - 40, ey - 22, c - 12, ey - 12), fill=B, width=6)
        d.line((c + 12, ey - 12, c + 40, ey - 22), fill=B, width=6)
    elif eyes == "raised":  # sourcil levé, perplexe
        d.ellipse((c - 32, ey - 8, c - 16, ey + 8), fill=B)
        d.ellipse((c + 16, ey - 8, c + 32, ey + 8), fill=B)
        d.arc((c - 42, ey - 30, c - 6, ey - 10), 200, 340, fill=B, width=5)
        d.line((c + 12, ey - 18, c + 38, ey - 18), fill=B, width=5)
    elif eyes == "happy":  # yeux plissés de rire ^^
        d.arc((c - 38, ey - 6, c - 10, ey + 14), 200, 340, fill=B, width=6)
        d.arc((c + 10, ey - 6, c + 38, ey + 14), 200, 340, fill=B, width=6)
    elif eyes == "patch":  # bandeau de pirate
        d.ellipse((c - 32, ey - 8, c - 16, ey + 8), fill=B)
        d.ellipse((c + 8, ey - 16, c + 40, ey + 16), fill=B)
        d.line((c - 70, ey - 34, c + 70, ey - 4), fill=B, width=5)
    # ---- bouche
    my = c + 22
    if mouth == "smile":
        d.arc((c - 30, my - 12, c + 30, my + 28), 10, 170, fill=B, width=5)
    elif mouth == "grin":
        d.chord((c - 30, my - 8, c + 30, my + 32), 0, 180, fill=B)
        d.rectangle((c - 24, my + 2, c + 24, my + 8), fill=W)
    elif mouth == "neutral":
        d.line((c - 22, my + 12, c + 22, my + 12), fill=B, width=5)
    elif mouth == "o":
        d.ellipse((c - 12, my + 2, c + 12, my + 28), outline=B, width=5)
    elif mouth == "yawn":
        d.ellipse((c - 18, my - 2, c + 18, my + 34), fill=B)
    elif mouth == "smirk":
        d.arc((c - 10, my - 12, c + 34, my + 28), 20, 150, fill=B, width=5)
    elif mouth == "laugh":  # grand rire, dents
        d.chord((c - 34, my - 10, c + 34, my + 36), 0, 180, fill=B)
        d.rectangle((c - 28, my + 2, c + 28, my + 12), fill=W)
    elif mouth == "whistle":
        d.ellipse((c + 4, my + 6, c + 20, my + 22), outline=B, width=5)
        for i, dx in enumerate((34, 46)):
            d.text((c + dx, my + 2 - i * 12), "♪", fill=B, font=font(26 + i * 6, bold=True), anchor="mm")
    elif mouth == "sad":
        d.arc((c - 26, my + 12, c + 26, my + 44), 190, 350, fill=B, width=5)
    elif mouth == "wavy":  # bouche en vague (gêné)
        for i, x in enumerate(range(c - 24, c + 24, 12)):
            d.arc((x, my + 4, x + 12, my + 16), 180 if i % 2 == 0 else 0, 360 if i % 2 == 0 else 180, fill=B, width=4)
    # ---- lunettes
    if glasses == "round":
        d.ellipse((c - 42, ey - 18, c - 6, ey + 18), outline=B, width=4)
        d.ellipse((c + 6, ey - 18, c + 42, ey + 18), outline=B, width=4)
        d.line((c - 6, ey, c + 6, ey), fill=B, width=4)
    elif glasses == "square":
        d.rounded_rectangle((c - 44, ey - 16, c - 6, ey + 16), radius=6, outline=B, width=4)
        d.rounded_rectangle((c + 6, ey - 16, c + 44, ey + 16), radius=6, outline=B, width=4)
        d.line((c - 6, ey, c + 6, ey), fill=B, width=4)
    elif glasses == "sun":
        d.rounded_rectangle((c - 46, ey - 16, c - 4, ey + 18), radius=8, fill=B)
        d.rounded_rectangle((c + 4, ey - 16, c + 46, ey + 18), radius=8, fill=B)
        d.line((c - 4, ey - 6, c + 4, ey - 6), fill=B, width=4)
        d.line((c - 46, ey - 8, c - 70, ey - 14), fill=B, width=4)
        d.line((c + 46, ey - 8, c + 70, ey - 14), fill=B, width=4)
    # ---- chapeaux
    if hat == "cap":
        d.chord((c - 72, c - 110, c + 72, c - 20), 180, 360, fill=B)
        d.rectangle((c - 72, c - 66, c + 72, c - 54), fill=B)
        d.rounded_rectangle((c - 10, c - 70, c + 100, c - 52), radius=8, fill=B)
    elif hat == "beanie":
        d.chord((c - 74, c - 116, c + 74, c - 10), 180, 360, fill=B)
        d.rounded_rectangle((c - 76, c - 70, c + 76, c - 48), radius=6, fill=B)
        d.ellipse((c - 16, c - 130, c + 16, c - 98), fill=B)
        for x in range(-60, 61, 20):
            d.line((c + x, c - 68, c + x, c - 50), fill=W, width=3)
    elif hat == "tophat":
        d.rectangle((c - 56, c - 140, c + 56, c - 62), fill=B)
        d.rectangle((c - 84, c - 68, c + 84, c - 56), fill=B)
    elif hat == "rain":  # chapeau de pluie
        d.chord((c - 70, c - 116, c + 70, c - 30), 180, 360, fill=B)
        d.polygon([(c - 96, c - 52), (c + 96, c - 52), (c + 80, c - 70), (c - 80, c - 70)], fill=B)
    elif hat == "santa":
        d.chord((c - 74, c - 112, c + 74, c - 20), 180, 360, fill=B)   # couvre les cheveux
        d.polygon([(c - 40, c - 100), (c + 50, c - 96), (c + 74, c - 160)], fill=B)
        d.ellipse((c + 60, c - 176, c + 92, c - 144), outline=B, width=5, fill=W)
        d.rounded_rectangle((c - 82, c - 70, c + 82, c - 46), radius=10, outline=B, width=5, fill=W)
    elif hat == "headphones":
        d.arc((c - 86, c - 92, c + 86, c + 50), 190, 350, fill=B, width=10)
        d.rounded_rectangle((c - 94, c - 20, c - 66, c + 30), radius=8, fill=B)
        d.rounded_rectangle((c + 66, c - 20, c + 94, c + 30), radius=8, fill=B)
    elif hat == "earmuffs":
        d.arc((c - 82, c - 96, c + 82, c + 30), 200, 340, fill=B, width=7)
        d.ellipse((c - 96, c - 24, c - 60, c + 12), fill=B)
        d.ellipse((c + 60, c - 24, c + 96, c + 12), fill=B)
    elif hat == "beret":
        d.chord((c - 80, c - 108, c + 70, c - 40), 180, 360, fill=B)
        d.rounded_rectangle((c - 72, c - 76, c + 62, c - 56), radius=8, fill=B)
        d.line((c - 6, c - 104, c + 2, c - 120), fill=B, width=5)
    elif hat == "bow":  # nœud dans les cheveux
        bx, by = c + 46, c - 66
        d.polygon([(bx, by), (bx - 30, by - 22), (bx - 30, by + 14)], fill=B)
        d.polygon([(bx, by), (bx + 30, by - 22), (bx + 30, by + 14)], fill=B)
        d.ellipse((bx - 8, by - 8, bx + 8, by + 8), outline=W, width=3, fill=B)
    elif hat == "flower":
        fx, fy = c + 50, c - 60
        for i in range(6):
            a = i * math.pi / 3
            d.ellipse((fx + 16 * math.cos(a) - 10, fy + 16 * math.sin(a) - 10, fx + 16 * math.cos(a) + 10, fy + 16 * math.sin(a) + 10), fill=B)
        d.ellipse((fx - 8, fy - 8, fx + 8, fy + 8), fill=W)
    elif hat == "cat_ears":  # serre-tête oreilles de chat
        for side in (-1, 1):
            x = c + side * 44
            d.polygon([(x - 22, c - 56), (x, c - 112), (x + 22, c - 56)], fill=B)
            d.polygon([(x - 10, c - 60), (x, c - 92), (x + 10, c - 60)], fill=W)
    elif hat == "sunhat":  # capeline
        d.chord((c - 60, c - 118, c + 60, c - 40), 180, 360, fill=B)
        d.ellipse((c - 104, c - 78, c + 104, c - 46), fill=B)
        d.rounded_rectangle((c - 60, c - 86, c + 60, c - 74), radius=4, fill=W)
    elif hat == "hood":  # capuche
        d.ellipse((c - 92, c - 100, c + 92, c + 84), fill=B)
        d.ellipse((c - 70, c - 70, c + 70, c + 70), outline=B, width=6, fill=W)
        d.ellipse((c - 70, c - 70, c + 70, c + 70), outline=B, width=6)
    elif hat == "party":  # chapeau de fête pointu
        d.polygon([(c - 36, c - 58), (c + 36, c - 58), (c + 10, c - 150)], fill=B)
        for y in (-80, -104):
            d.line((c + (y + 58) * -0.35 - 22, c + y, c + (y + 58) * -0.35 + 20, c + y), fill=W, width=4)
        d.ellipse((c + 2, c - 160, c + 18, c - 144), fill=B)
    elif hat == "crown":
        d.polygon([(c - 62, c - 58), (c + 62, c - 58), (c + 62, c - 110), (c + 34, c - 84), (c + 2, c - 120),
                   (c - 30, c - 84), (c - 62, c - 110)], fill=B)
        for x in (c - 36, c + 2, c + 40):
            d.ellipse((x - 5, c - 76, x + 5, c - 66), fill=W)
    elif hat == "bandana":
        d.chord((c - 72, c - 80, c + 72, c - 10), 180, 360, fill=B)
        d.rounded_rectangle((c - 74, c - 68, c + 74, c - 48), radius=6, fill=B)
        d.polygon([(c + 60, c - 60), (c + 100, c - 40), (c + 96, c - 70), (c + 80, c - 80)], fill=B)
        for x in range(-56, 60, 18):
            d.ellipse((c + x - 3, c - 61, c + x + 3, c - 55), fill=W)
    elif hat == "chef":
        d.rectangle((c - 50, c - 100, c + 50, c - 56), fill=B)
        d.ellipse((c - 64, c - 140, c - 10, c - 86), fill=B)
        d.ellipse((c - 30, c - 150, c + 30, c - 90), fill=B)
        d.ellipse((c + 10, c - 140, c + 64, c - 86), fill=B)
        d.rounded_rectangle((c - 54, c - 72, c + 54, c - 56), radius=4, outline=B, width=4, fill=W)
    elif hat == "pirate":
        d.chord((c - 90, c - 120, c + 90, c - 30), 180, 360, fill=B)
        d.polygon([(c - 100, c - 60), (c + 100, c - 60), (c + 80, c - 74), (c - 80, c - 74)], fill=B)
        d.ellipse((c - 12, c - 104, c + 12, c - 80), fill=W)
        d.line((c - 16, c - 78, c + 16, c - 66), fill=W, width=4)
        d.line((c + 16, c - 78, c - 16, c - 66), fill=W, width=4)
    elif hat == "halo":
        d.ellipse((c - 50, c - 99, c + 50, c - 79), outline=B, width=7)
    elif hat == "horns":
        for side in (-1, 1):
            x = c + side * 48
            d.polygon([(x - 14, c - 54), (x + side * 10, c - 108), (x + 14, c - 58)], fill=B)
    elif hat == "graduate":  # toque de diplômé
        d.polygon([(c - 90, c - 80), (c, c - 112), (c + 90, c - 80), (c, c - 48)], fill=B)
        d.rounded_rectangle((c - 52, c - 76, c + 52, c - 50), radius=6, fill=B)
        d.line((c + 90, c - 80, c + 96, c - 40), fill=B, width=4)
        d.ellipse((c + 90, c - 44, c + 102, c - 32), fill=B)
    elif hat == "helmet":  # casque vélo
        d.chord((c - 78, c - 118, c + 78, c - 10), 180, 360, fill=B)
        for x in (-40, -14, 12, 38):
            d.line((c + x, c - 100, c + x + 6, c - 62), fill=W, width=5)
        d.rectangle((c - 78, c - 68, c + 78, c - 56), fill=B)
    # ---- extras
    if extra == "scarf":
        d.rounded_rectangle((c - 62, c + 54, c + 62, c + 80), radius=10, fill=B)
        d.rectangle((c + 20, c + 70, c + 48, c + 100), fill=B)
        for x in range(-50, 51, 16):
            d.line((c + x, c + 58, c + x, c + 76), fill=W, width=3)
    elif extra == "coffee":
        d.rounded_rectangle((c + 56, c + 44, c + 96, c + 92), radius=6, outline=B, width=5, fill=W)
        d.rectangle((c + 56, c + 44, c + 96, c + 54), fill=B)
        d.arc((c + 88, c + 54, c + 112, c + 80), 270, 90, fill=B, width=5)
        for x in (c + 66, c + 80):
            d.line((x, c + 24, x + 4, c + 36), fill=B, width=4)
            d.line((x + 4, c + 36, x, c + 42), fill=B, width=4)
    elif extra == "umbrella":
        d.pieslice((c - 110, c - 140, c + 110, c + 20), 180, 360, fill=B)
        d.line((c, c - 60, c, c + 10), fill=B, width=5)
    elif extra == "zzz":
        for i, (dx, dy, sz) in enumerate(((56, -70, 26), (76, -94, 34), (98, -120, 42))):
            d.text((c + dx, c + dy), "z" if i < 2 else "Z", fill=B, font=font(sz, bold=True), anchor="mm")
    elif extra == "blush":
        d.ellipse((c - 54, c + 8, c - 40, c + 20), fill=B)
        d.ellipse((c + 40, c + 8, c + 54, c + 20), fill=B)
    elif extra == "tear":
        d.ellipse((c + 30, c + 6, c + 40, c + 24), fill=B)
    elif extra == "earrings":
        for side in (-1, 1):
            x = c + side * 70
            d.line((x, c + 18, x, c + 34), fill=B, width=3)
            d.ellipse((x - 8, c + 32, x + 8, c + 48), outline=B, width=4, fill=W)
    elif extra == "tea":  # tasse avec sachet
        d.rounded_rectangle((c + 56, c + 48, c + 98, c + 92), radius=6, outline=B, width=5, fill=W)
        d.arc((c + 90, c + 56, c + 114, c + 82), 270, 90, fill=B, width=5)
        d.line((c + 84, c + 48, c + 92, c + 30), fill=B, width=3)
        d.rectangle((c + 88, c + 22, c + 100, c + 32), fill=B)
    elif extra == "book":
        d.polygon([(c - 100, c + 52), (c - 48, c + 42), (c - 48, c + 96), (c - 100, c + 106)], outline=B, width=5, fill=W)
        d.polygon([(c - 48, c + 42), (c + 4, c + 52), (c + 4, c + 106), (c - 48, c + 96)], outline=B, width=5, fill=W)
        for y in (56, 68, 80):
            d.line((c - 92, c + y + 4, c - 56, c + y - 2), fill=B, width=2)
    elif extra == "heart":
        hx, hy = c + 74, c - 70
        d.ellipse((hx - 18, hy - 12, hx, hy + 6), fill=B)
        d.ellipse((hx, hy - 12, hx + 18, hy + 6), fill=B)
        d.polygon([(hx - 17, hy), (hx + 17, hy), (hx, hy + 22)], fill=B)
    elif extra == "tongue":
        d.chord((c - 10, c + 30, c + 14, c + 58), 0, 180, fill=B)
        d.ellipse((c - 8, c + 36, c + 12, c + 56), fill=B)
    elif extra == "mustache":
        for side in (-1, 1):
            d.chord((c + side * 22 - 24, c + 8, c + side * 22 + 24, c + 32), 180, 360, fill=B)
        d.ellipse((c - 6, c + 10, c + 6, c + 22), fill=B)
    elif extra == "freckles":
        for x, y in ((-48, 12), (-40, 20), (-54, 24), (40, 12), (48, 20), (54, 26), (-44, 30), (44, 32)):
            d.ellipse((c + x - 3, c + y - 3, c + x + 3, c + y + 3), fill=B)
    elif extra == "bowtie":
        by = c + 78
        d.polygon([(c, by), (c - 34, by - 16), (c - 34, by + 16)], fill=B)
        d.polygon([(c, by), (c + 34, by - 16), (c + 34, by + 16)], fill=B)
        d.ellipse((c - 8, by - 8, c + 8, by + 8), outline=W, width=3, fill=B)
    elif extra == "mask":  # masque de super-héros
        d.polygon([(c - 60, c - 24), (c - 8, c - 18), (c, c - 2), (c + 8, c - 18), (c + 60, c - 24),
                   (c + 56, c + 12), (c + 10, c + 10), (c, c + 2), (c - 10, c + 10), (c - 56, c + 12)], fill=B)
        d.ellipse((c - 40, c - 14, c - 16, c + 2), fill=W)
        d.ellipse((c + 16, c - 14, c + 40, c + 2), fill=W)
    elif extra == "sweat":
        d.polygon([(c + 60, c - 36), (c + 70, c - 10), (c + 50, c - 10)], fill=B)
        d.ellipse((c + 50, c - 20, c + 70, c + 0), fill=B)
    elif extra == "star":  # étoile filante
        pts = []
        sx, sy = c + 76, c - 76
        for i in range(10):
            r = 18 if i % 2 == 0 else 7
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((sx + r * math.cos(a), sy + r * math.sin(a)))
        d.polygon(pts, fill=B)
        d.line((sx - 20, sy + 10, sx - 50, sy + 30), fill=B, width=4)
    elif extra == "phone":
        d.rounded_rectangle((c + 56, c + 20, c + 92, c + 86), radius=6, outline=B, width=5, fill=W)
        d.rectangle((c + 62, c + 30, c + 86, c + 70), fill=B)
    elif extra == "scarf_plain":
        d.rounded_rectangle((c - 62, c + 54, c + 62, c + 80), radius=10, fill=B)
        d.rectangle((c - 48, c + 70, c - 20, c + 100), fill=B)
    return im


VARIANTS = {
    "cam": [
        ("classique",   dict(hair="long", eyes="open", mouth="neutral")),
        ("sourire",     dict(hair="long", eyes="open", mouth="smile", extra="blush")),
        ("clin d'œil",  dict(hair="long", eyes="wink", mouth="smirk")),
        ("chignon",     dict(hair="bun", eyes="open", mouth="smile")),
        ("queue",       dict(hair="ponytail", eyes="open", mouth="grin")),
        ("carré",       dict(hair="bob", eyes="open", mouth="smile")),
        ("frange",      dict(hair="fringe", eyes="open", mouth="neutral")),
        ("lunettes",    dict(hair="long", eyes="open", mouth="smile", glasses="square")),
        ("soleil",      dict(hair="long", eyes="open", mouth="grin", glasses="sun")),
        ("pluie",       dict(hair="long", eyes="open", mouth="neutral", hat="rain")),
        ("froid",       dict(hair="long", eyes="open", mouth="smile", hat="beanie", extra="scarf")),
        ("cache-oreilles", dict(hair="long", eyes="closed", mouth="smile", hat="earmuffs")),
        ("réveil",      dict(hair="long", eyes="sleepy", mouth="yawn", extra="zzz")),
        ("café",        dict(hair="long", eyes="sleepy", mouth="neutral", extra="coffee")),
        ("surprise",    dict(hair="long", eyes="wide", mouth="o")),
        ("musique",     dict(hair="long", eyes="closed", mouth="smile", hat="headphones")),
        ("vélo",        dict(hair="long", eyes="open", mouth="grin", hat="helmet")),
        ("noël",        dict(hair="long", eyes="open", mouth="smile", hat="santa")),
    ],
    "oliv": [
        ("classique",   dict(hair="short", eyes="open", mouth="smile", glasses="round")),
        ("sans lunettes", dict(hair="short", eyes="open", mouth="smile")),
        ("clin d'œil",  dict(hair="short", eyes="wink", mouth="smirk", glasses="round")),
        ("barbe",       dict(hair="short", eyes="open", mouth="smile", glasses="round", beard=True)),
        ("pics",        dict(hair="spiky", eyes="open", mouth="grin", glasses="round")),
        ("bouclé",      dict(hair="curly", eyes="open", mouth="smile", glasses="round")),
        ("chauve",      dict(hair="bald", eyes="open", mouth="smile", glasses="round")),
        ("carrées",     dict(hair="short", eyes="open", mouth="smile", glasses="square")),
        ("soleil",      dict(hair="short", eyes="open", mouth="grin", glasses="sun")),
        ("pluie",       dict(hair="short", eyes="open", mouth="neutral", glasses="round", hat="rain")),
        ("froid",       dict(hair="short", eyes="open", mouth="smile", glasses="round", hat="beanie", extra="scarf")),
        ("casquette",   dict(hair="short", eyes="open", mouth="smile", glasses="round", hat="cap")),
        ("réveil",      dict(hair="short", eyes="sleepy", mouth="yawn", glasses="round", extra="zzz")),
        ("café",        dict(hair="short", eyes="sleepy", mouth="neutral", glasses="round", extra="coffee")),
        ("surprise",    dict(hair="short", eyes="wide", mouth="o", glasses="round")),
        ("musique",     dict(hair="short", eyes="closed", mouth="smile", glasses="round", hat="headphones")),
        ("chic",        dict(hair="short", eyes="open", mouth="smile", glasses="round", hat="tophat")),
        ("noël",        dict(hair="short", eyes="open", mouth="smile", glasses="round", hat="santa", beard=True)),
    ],
}


PETARD = [
    ("épis",            dict(hair="petard", eyes="open", mouth="smile", glasses="round")),
    ("épis + clin",     dict(hair="petard", eyes="wink", mouth="smirk", glasses="round")),
    ("épis + barbe",    dict(hair="petard", eyes="open", mouth="grin", glasses="round", beard=True)),
    ("mèches folles",   dict(hair="petard_fou", eyes="open", mouth="smile", glasses="round")),
    ("mèches + surprise", dict(hair="petard_fou", eyes="wide", mouth="o", glasses="round")),
    ("oreiller",        dict(hair="petard_reveil", eyes="sleepy", mouth="yawn", glasses="round")),
    ("oreiller + café", dict(hair="petard_reveil", eyes="sleepy", mouth="neutral", glasses="round", extra="coffee")),
    ("crête",           dict(hair="crete", eyes="open", mouth="grin", glasses="round")),
    ("boule",           dict(hair="boule", eyes="open", mouth="smile", glasses="round")),
    ("hérisson",        dict(hair="herisson", eyes="open", mouth="smile", glasses="round")),
    ("hérisson + soleil", dict(hair="herisson", eyes="open", mouth="grin", glasses="sun")),
    ("dans le vent",    dict(hair="petard_vent", eyes="open", mouth="smile", glasses="round")),
    ("vent + musique",  dict(hair="petard_vent", eyes="closed", mouth="smile", glasses="round", hat="headphones")),
    ("épis sans lunettes", dict(hair="petard", eyes="open", mouth="smile")),
    ("épis + carrées",  dict(hair="petard", eyes="open", mouth="smile", glasses="square")),
]


CAM2 = [
    ("ondulés",         dict(hair="wavy", eyes="open", mouth="smile")),
    ("ondulés + clin",  dict(hair="wavy", eyes="wink", mouth="smirk", extra="earrings")),
    ("tresses",         dict(hair="braids", eyes="open", mouth="grin")),
    ("demi-queue",      dict(hair="halfup", eyes="open", mouth="smile", extra="blush")),
    ("chignon flou",    dict(hair="bun_loose", eyes="sleepy", mouth="neutral", extra="tea")),
    ("bandeau",         dict(hair="headband", eyes="open", mouth="smile")),
    ("bouclés",         dict(hair="curly_long", eyes="open", mouth="grin")),
    ("pixie",           dict(hair="pixie", eyes="open", mouth="smile", extra="earrings")),
    ("béret",           dict(hair="long", eyes="open", mouth="smile", hat="beret")),
    ("nœud",            dict(hair="long", eyes="open", mouth="grin", hat="bow")),
    ("fleur",           dict(hair="wavy", eyes="closed", mouth="smile", hat="flower")),
    ("oreilles de chat", dict(hair="long", eyes="open", mouth="smirk", hat="cat_ears")),
    ("capeline",        dict(hair="long", eyes="open", mouth="smile", hat="sunhat", glasses="sun")),
    ("bonnet",          dict(hair="wavy", eyes="open", mouth="smile", hat="beanie", extra="scarf")),
    ("lecture",         dict(hair="bun_loose", eyes="open", mouth="neutral", glasses="round", extra="book")),
    ("langue",          dict(hair="long", eyes="wink", mouth="neutral", extra="tongue")),
    ("amoureuse",       dict(hair="wavy", eyes="closed", mouth="smile", extra="heart")),
    ("thé du matin",    dict(hair="long", eyes="sleepy", mouth="neutral", extra="tea")),
]


def sheet_list(title, items, filename, cols=5):
    pad, label_h = 16, 26
    rows = math.ceil(len(items) / cols)
    im = Image.new("L", (cols * (S + pad) + pad, 60 + rows * (S + pad + label_h)), W)
    d = ImageDraw.Draw(im)
    d.text((pad, 18), title, fill=B, font=font(34, bold=True))
    for i, (name, opts) in enumerate(items):
        r, ci = divmod(i, cols)
        x, y = pad + ci * (S + pad), 60 + r * (S + pad + label_h)
        im.paste(face(**opts), (x, y))
        d.rectangle((x, y, x + S - 1, y + S - 1), outline=210)
        d.text((x + S / 2, y + S + 4), f"{i + 1}. {name}", fill=B, font=font(20), anchor="mt")
    im.save(HERE / filename)
    print("planche :", HERE / filename)


CAM3 = [
    ("rire",            dict(hair="long", eyes="happy", mouth="laugh")),
    ("yeux en cœur",    dict(hair="long", eyes="hearts", mouth="smile")),
    ("étoiles",         dict(hair="long", eyes="stars", mouth="o")),
    ("grognon",         dict(hair="long", eyes="angry", mouth="neutral")),
    ("perplexe",        dict(hair="long", eyes="raised", mouth="wavy")),
    ("triste",          dict(hair="long", eyes="open", mouth="sad", extra="tear")),
    ("sifflote",        dict(hair="long", eyes="closed", mouth="whistle")),
    ("taches de rousseur", dict(hair="long", eyes="open", mouth="smile", extra="freckles")),
    ("en retard",       dict(hair="long", eyes="wide", mouth="o", extra="sweat")),
    ("fête",            dict(hair="long", eyes="happy", mouth="laugh", hat="party")),
    ("reine",           dict(hair="long", eyes="open", mouth="smirk", hat="crown")),
    ("bandana",         dict(hair="long", eyes="open", mouth="grin", hat="bandana")),
    ("pirate",          dict(hair="long", eyes="patch", mouth="grin", hat="pirate")),
    ("ange",            dict(hair="long", eyes="closed", mouth="smile", hat="halo")),
    ("diablotine",      dict(hair="long", eyes="angry", mouth="grin", hat="horns")),
    ("super-héroïne",   dict(hair="long", eyes="open", mouth="smirk", extra="mask")),
    ("au téléphone",    dict(hair="long", eyes="open", mouth="smile", extra="phone")),
    ("étoile filante",  dict(hair="long", eyes="closed", mouth="smile", extra="star")),
]

OLIV3 = [
    ("rire",            dict(hair="short", eyes="happy", mouth="laugh", glasses="round")),
    ("yeux en cœur",    dict(hair="short", eyes="hearts", mouth="smile")),
    ("étoiles",         dict(hair="short", eyes="stars", mouth="o")),
    ("grognon",         dict(hair="short", eyes="angry", mouth="neutral", glasses="round")),
    ("perplexe",        dict(hair="short", eyes="raised", mouth="wavy", glasses="round")),
    ("sifflote",        dict(hair="short", eyes="closed", mouth="whistle", glasses="round")),
    ("moustache",       dict(hair="short", eyes="open", mouth="smile", glasses="round", extra="mustache")),
    ("nœud papillon",   dict(hair="short", eyes="open", mouth="smile", glasses="round", extra="bowtie")),
    ("en retard",       dict(hair="short", eyes="wide", mouth="o", glasses="round", extra="sweat")),
    ("fête",            dict(hair="short", eyes="happy", mouth="laugh", glasses="round", hat="party")),
    ("roi",             dict(hair="short", eyes="open", mouth="smirk", glasses="round", hat="crown")),
    ("bandana",         dict(hair="short", eyes="open", mouth="grin", glasses="round", hat="bandana")),
    ("pirate",          dict(hair="short", eyes="patch", mouth="grin", hat="pirate", beard=True)),
    ("chef",            dict(hair="short", eyes="open", mouth="smile", glasses="round", hat="chef", extra="mustache")),
    ("ange",            dict(hair="short", eyes="closed", mouth="smile", glasses="round", hat="halo")),
    ("diablotin",       dict(hair="short", eyes="angry", mouth="grin", glasses="round", hat="horns")),
    ("super-héros",     dict(hair="short", eyes="open", mouth="smirk", extra="mask")),
    ("diplômé",         dict(hair="short", eyes="open", mouth="smile", glasses="round", hat="graduate")),
]


def sheet_petard():
    sheet_list("Olivier — cheveux en pétard", PETARD, "variations_petard.png")
    sheet_list("Camille — série 2", CAM2, "variations_camille2.png", cols=6)


def sheet_serie3():
    sheet_list("Camille — série 3", CAM3, "variations_camille3.png", cols=6)
    sheet_list("Olivier — série 3", OLIV3, "variations_olivier3.png", cols=6)


def sheet():
    cols = 6
    pad, label_h = 16, 26
    out = []
    for key, items in VARIANTS.items():
        rows = math.ceil(len(items) / cols)
        im = Image.new("L", (cols * (S + pad) + pad, 60 + rows * (S + pad + label_h)), W)
        d = ImageDraw.Draw(im)
        d.text((pad, 18), key.capitalize(), fill=B, font=font(34, bold=True))
        for i, (name, opts) in enumerate(items):
            r, ci = divmod(i, cols)
            x = pad + ci * (S + pad)
            y = 60 + r * (S + pad + label_h)
            im.paste(face(**opts), (x, y))
            d.rectangle((x, y, x + S - 1, y + S - 1), outline=210)
            d.text((x + S / 2, y + S + 4), f"{i + 1}. {name}", fill=B, font=font(20), anchor="mt")
        out.append(im)
    total = Image.new("L", (max(i.width for i in out), sum(i.height for i in out) + 20), W)
    y = 0
    for im in out:
        total.paste(im, (0, y))
        y += im.height + 20
    total.save(HERE / "variations_visages.png")
    print("planche :", HERE / "variations_visages.png")


def build(selection: dict[str, list[str]]):
    """selection = {"cam": ["sourire", "soleil", ...], "oliv": [...]} → pictos/<personne>/<nom>.png"""
    for key, names in selection.items():
        folder = HERE / "pictos" / key
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*.png"):
            old.unlink()
        lookup = dict(VARIANTS[key])
        for n in names:
            face(**lookup[n]).save(folder / f"{n.replace(' ', '_').replace(chr(39), '')}.png")
            print("écrit", folder / n)


# Pictos retenus (décision d'Olivier, 29/10/2026) : un au hasard par jour (voir render.pick_picto)
SELECTION = {
    "cam": ["sourire", "clin d'œil", "café", "musique"],                         # planche 1 : 2, 3, 14, 16
    "oliv": ["classique", "sans lunettes", "clin d'œil", "pics", "réveil", "surprise"],  # planche 1 : 1, 2, 3, 5, 13, 15
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sheet"
    if cmd == "build":
        build(SELECTION)
    elif cmd == "petard":
        sheet_petard()
    elif cmd == "serie3":
        sheet_serie3()
    else:
        sheet()
