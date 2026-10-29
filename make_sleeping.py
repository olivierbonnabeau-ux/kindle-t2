"""Génère kindle/dashboard/sleeping.png : l'écran affiché par kindle-dash la nuit
(quand le prochain réveil est à plus d'une heure). Statique, sans heure."""
from pathlib import Path

from PIL import Image, ImageDraw

from render import DARK, GREY, WHITE, BLACK, font, load_config_render

HERE = Path(__file__).resolve().parent


def main():
    cfg = load_config_render()
    rc = cfg.get("render", {})
    W, H = int(rc.get("width", 758)), int(rc.get("height", 1024))
    stop = cfg["stop"]
    img = Image.new("L", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 140), f"{stop['name']} · {stop['line_name']}", fill=DARK, font=font(36, bold=True), anchor="mt")
    cx, cy = W // 2, H // 2 - 60
    d.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=BLACK)
    d.ellipse((cx - 30, cy - 115, cx + 125, cy + 40), fill=WHITE)  # croissant
    d.text((cx, cy + 170), "Bonne nuit", fill=BLACK, font=font(64, bold=True), anchor="mt")
    d.text((cx, cy + 260), f"Premier tram vers {cfg['schedule']['night']['end']}", fill=DARK, font=font(30), anchor="mt")
    d.text((cx, H - 60), "Le Kindle se réveillera tout seul", fill=GREY, font=font(22), anchor="mt")
    out = HERE / "kindle" / "dashboard" / "sleeping.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG")
    print("écrit", out)


if __name__ == "__main__":
    main()
