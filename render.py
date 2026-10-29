"""Rendu de l'image e-ink 758×1024 (Kindle Paperwhite), niveaux de gris.

    from render import render_screen, render_night
    img = render_screen(plans, departures, traffic, now, cfg)   # PIL.Image mode "L"
    img.save("kindle.png")

Police : DejaVu Sans si présente (./fonts/ ou C:\\Windows\\Fonts), sinon
Segoe UI / Arial / Verdana (Windows), sinon police bitmap Pillow.
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
PICTOS = HERE / "pictos"

WHITE, LIGHT, GREY, DARK, BLACK = 255, 235, 150, 60, 0

_FONT_CANDIDATES = {
    "regular": ["DejaVuSans.ttf", "segoeui.ttf", "arial.ttf", "verdana.ttf"],
    "bold": ["DejaVuSans-Bold.ttf", "segoeuib.ttf", "arialbd.ttf", "verdanab.ttf"],
}
_FONT_DIRS = [HERE / "fonts", Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu")]
_font_cache: dict[tuple, ImageFont.FreeTypeFont] = {}

_JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
_MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
         "septembre", "octobre", "novembre", "décembre"]


def date_fr(dt: datetime) -> str:
    """'Jeudi 29 octobre' sans dépendre de la locale système (Render est en anglais)."""
    return f"{_JOURS[dt.weekday()]} {dt.day} {_MOIS[dt.month - 1]}"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    for name in _FONT_CANDIDATES["bold" if bold else "regular"]:
        for d in _FONT_DIRS:
            p = d / name
            if p.exists():
                f = ImageFont.truetype(str(p), size)
                _font_cache[key] = f
                return f
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f


# ---------------------------------------------------------------- pictos
def pick_picto(person_key: str, day: datetime, weather: str | None = None) -> Path | None:
    """Un picto différent chaque jour ; si `weather` est donné, on préfère un
    fichier dont le nom contient ce mot (ex. "pluie", "soleil")."""
    folder = PICTOS / person_key
    if not folder.is_dir():
        return None
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp"))
    if not files:
        return None
    if weather:
        w = weather.lower()
        matching = [p for p in files if w in p.stem.lower()]
        if matching:
            files = matching
    # hash stable de (personne, date) → même picto toute la journée, change le lendemain
    h = int(hashlib.md5(f"{person_key}:{day:%Y-%m-%d}".encode()).hexdigest(), 16)
    return files[h % len(files)]


def load_picto(path: Path | None, size: int, fallback_initial: str) -> Image.Image:
    box = Image.new("L", (size, size), WHITE)
    if path and path.exists():
        try:
            im = Image.open(path).convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            bg.alpha_composite(im)
            im = bg.convert("L")
            im = ImageOps.autocontrast(im)
            im.thumbnail((size, size), Image.LANCZOS)
            box.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
            return box
        except Exception:
            pass
    # Fallback : rond avec l'initiale
    d = ImageDraw.Draw(box)
    d.ellipse((4, 4, size - 4, size - 4), outline=BLACK, width=6, fill=LIGHT)
    f = font(int(size * 0.5), bold=True)
    d.text((size / 2, size / 2), fallback_initial.upper(), fill=BLACK, font=f, anchor="mm")
    return box


# ---------------------------------------------------------------- helpers
def _text_w(draw: ImageDraw.ImageDraw, text: str, f) -> int:
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    return r - l


def _fit_text(draw, text: str, f_size: int, max_w: int, bold=False, min_size=18):
    """Réduit la taille jusqu'à ce que le texte tienne dans max_w."""
    size = f_size
    while size > min_size:
        f = font(size, bold)
        if _text_w(draw, text, f) <= max_w:
            return f
        size -= 2
    return font(min_size, bold)


def _wrap(draw, text: str, f, max_w: int, max_lines: int = 2) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if _text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text):
        lines[-1] = lines[-1][: max(0, len(lines[-1]) - 1)].rstrip() + "…"
    return lines


# ---------------------------------------------------------------- écran principal
def render_screen(plans, departures, traffic, now: datetime, cfg: dict,
                  stale: bool = False, weather: str | None = None) -> Image.Image:
    rc = cfg.get("render", {})
    W, H = int(rc.get("width", 758)), int(rc.get("height", 1024))
    stop = cfg["stop"]
    img = Image.new("L", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    margin = 28

    # --- en-tête
    title = f"{stop['name']} · {stop['line_name']}"
    d.text((margin, 30), title, fill=BLACK, font=font(40, bold=True))
    clock = now.strftime("%H:%M")
    f_clock = font(40, bold=True)
    d.text((W - margin - _text_w(d, clock, f_clock), 30), clock, fill=BLACK, font=f_clock)
    d.text((margin, 84), date_fr(now), fill=DARK, font=font(24))
    d.line((margin, 124, W - margin, 124), fill=BLACK, width=3)

    # --- deux colonnes
    col_top, col_bottom = 150, 700
    col_w = (W - 2 * margin) // 2
    d.line((W // 2, col_top, W // 2, col_bottom), fill=GREY, width=2)
    people_cfg = {p["name"]: p for p in cfg["people"]}
    for i, plan in enumerate(plans):
        x0 = margin + i * col_w
        cx = x0 + col_w // 2
        pkey = people_cfg.get(plan.name, {}).get("key", plan.name.lower())
        picto = load_picto(pick_picto(pkey, now, weather), 190, plan.name[:1])
        img.paste(picto, (cx - 95, col_top))
        d.text((cx, col_top + 215), plan.name, fill=BLACK, font=font(36, bold=True), anchor="mt")

        # gros chiffre
        big_y = col_top + 300
        if plan.leave_in_min is None:
            d.text((cx, big_y), "—", fill=GREY, font=font(96, bold=True), anchor="mt")
        elif plan.leave_now:
            f = _fit_text(d, "Maintenant !", 64, col_w - 20, bold=True)
            # inversé pour attirer l'œil
            l, t, r, b = d.textbbox((cx, big_y + 20), "Maintenant !", font=f, anchor="mt")
            d.rounded_rectangle((l - 14, t - 10, r + 14, b + 10), radius=14, fill=BLACK)
            d.text((cx, big_y + 20), "Maintenant !", fill=WHITE, font=f, anchor="mt")
        else:
            f_num = font(110, bold=True)
            num = str(plan.leave_in_min)
            f_min = font(44)
            w_num, w_min = _text_w(d, num, f_num), _text_w(d, " min", f_min)
            x = cx - (w_num + w_min) // 2
            d.text((x, big_y), num, fill=BLACK, font=f_num, anchor="lt")
            d.text((x + w_num, big_y + 58), " min", fill=BLACK, font=f_min, anchor="lt")

        y = col_top + 445
        tram = plan.target_tram.strftime("%H:%M") if plan.target_tram else "--:--"
        d.text((cx, y), f"tram {tram}", fill=BLACK, font=font(34), anchor="mt")
        d.text((cx, y + 48), f"{plan.walk_min} min à pied", fill=DARK, font=font(26), anchor="mt")
        if plan.margin_min:
            d.text((cx, y + 82), f"+ {plan.margin_min} min de marge", fill=GREY, font=font(20), anchor="mt")

    # --- prochains départs
    y = col_bottom + 10
    d.line((margin, y, W - margin, y), fill=BLACK, width=3)
    y += 18
    d.text((margin, y), f"Prochains départs → {stop['destination']}", fill=BLACK, font=font(28, bold=True))
    y += 48
    n = int(rc.get("next_departures", 4))
    nexts = sorted(departures)[:n]
    if nexts:
        slot = (W - 2 * margin) // n
        for i, t in enumerate(nexts):
            cx = margin + i * slot + slot // 2
            d.text((cx, y), t.strftime("%H:%M"), fill=BLACK, font=font(52, bold=i == 0), anchor="mt")
            mins = int((t - now).total_seconds() // 60)
            d.text((cx, y + 62), f"{max(mins, 0)} min", fill=DARK, font=font(24), anchor="mt")
    else:
        d.text((margin, y + 10), "Aucun passage annoncé", fill=DARK, font=font(34))
    y += 104

    # --- état trafic / données
    d.line((margin, y, W - margin, y), fill=GREY, width=2)
    y += 14
    if stale:
        status, msg = "⚠ Données indisponibles", "dernière réponse de l'API affichée"
    elif traffic is not None and traffic.disrupted:
        status, msg = "Trafic perturbé", traffic.message
    else:
        status, msg = "Trafic normal", (traffic.message if traffic and traffic.message != "Trafic normal" else "")
    f_status = font(28, bold=True)
    d.text((margin, y), status, fill=BLACK, font=f_status)
    if msg:
        f_msg = font(22)
        lines = _wrap(d, msg, f_msg, W - 2 * margin, max_lines=2)
        for i, line in enumerate(lines):
            d.text((margin, y + 38 + i * 28), line, fill=DARK, font=f_msg)

    # pied : heure de mise à jour
    foot = f"maj {now:%H:%M:%S}"
    f_foot = font(18)
    d.text((W - margin - _text_w(d, foot, f_foot), H - 24), foot, fill=GREY, font=f_foot)
    return img


# ---------------------------------------------------------------- écran nuit
def render_night(now: datetime, cfg: dict, next_active: str = "06:00") -> Image.Image:
    rc = cfg.get("render", {})
    W, H = int(rc.get("width", 758)), int(rc.get("height", 1024))
    img = Image.new("L", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    stop = cfg["stop"]
    d.text((W // 2, 120), f"{stop['name']} · {stop['line_name']}", fill=DARK, font=font(36, bold=True), anchor="mt")
    d.text((W // 2, H // 2 - 120), now.strftime("%H:%M"), fill=BLACK, font=font(160, bold=True), anchor="mm")
    d.text((W // 2, H // 2 + 20), date_fr(now), fill=DARK, font=font(30), anchor="mm")
    d.ellipse((W // 2 - 40, H // 2 + 90, W // 2 + 40, H // 2 + 170), fill=BLACK)
    d.ellipse((W // 2 - 10, H // 2 + 78, W // 2 + 60, H // 2 + 150), fill=WHITE)  # croissant de lune
    d.text((W // 2, H - 140), f"Bonne nuit — horaires à partir de {next_active}", fill=GREY, font=font(24), anchor="mm")
    return img


def load_config_render() -> dict:
    import yaml

    with open(HERE / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":  # aperçu avec données simulées
    import locale
    from datetime import timedelta
    from zoneinfo import ZoneInfo

    import yaml

    from logic import compute_all
    from prim_client import TrafficResult

    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "French_France.1252")
        except locale.Error:
            pass
    cfg = yaml.safe_load(open(HERE / "config.yaml", encoding="utf-8"))
    now = datetime.now(ZoneInfo(cfg["timezone"])).replace(second=0, microsecond=0)
    fake = [now + timedelta(minutes=m) for m in (4, 9, 15, 21, 28, 35)]
    plans = compute_all(cfg["people"], fake, now)
    out = HERE / "preview.png"
    render_screen(plans, fake, TrafficResult(disrupted=True, message="Trafic perturbé entre La Défense et Pont de Bezons suite à un incident technique, reprise estimée à 09:30."), now, cfg).save(out)
    render_night(now, cfg).save(HERE / "preview_night.png")
    print("écrit", out, "et preview_night.png")
