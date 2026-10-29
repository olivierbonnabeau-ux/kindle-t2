"""Serveur HTTP pour le Kindle.

    GET /kindle.png   → image 758×1024 niveaux de gris (régénérée au plus toutes
                        les `schedule.min_regen_s` secondes). En-tête
                        X-Refresh-Seconds = délai conseillé avant le prochain appel.
    GET /             → page HTML qui affiche l'image et se recharge toute seule
                        (pratique pour tester dans un navigateur, ou sur le Kindle).
    GET /health       → JSON : état API, âge des données, mode (active/normal/night).
    GET /kindle.png?force=1 → force la régénération (debug).

Lancement :  python server.py   (ou run.bat)
"""
from __future__ import annotations

import io
import locale
import logging
import threading
import time
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

from flask import Flask, Response, jsonify, request

import render
from logic import compute_all
from prim_client import DeparturesResult, PrimClient, TrafficResult, load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("kindle")

for loc in ("fr_FR.UTF-8", "French_France.1252", "fr_FR"):
    try:
        locale.setlocale(locale.LC_TIME, loc)
        break
    except locale.Error:
        continue

cfg = load_config()
TZ = ZoneInfo(cfg.get("timezone", "Europe/Paris"))
SCHED = cfg.get("schedule", {})
MIN_REGEN = float(SCHED.get("min_regen_s", 30))

app = Flask(__name__)
_lock = threading.Lock()
_state = {"png": None, "generated_mono": 0.0, "generated_at": None, "mode": None,
          "stale": False, "error": None, "n_departures": 0}

try:
    client: PrimClient | None = PrimClient(cfg)
    _client_error = None
except RuntimeError as e:  # clé absente : on démarre quand même, écran d'erreur
    client, _client_error = None, str(e)
    log.error(_client_error)


def _parse_hm(s: str) -> dtime:
    h, m = s.split(":")
    return dtime(int(h), int(m))


def _in_window(now_t: dtime, start: str, end: str) -> bool:
    s, e = _parse_hm(start), _parse_hm(end)
    if s <= e:
        return s <= now_t < e
    return now_t >= s or now_t < e  # fenêtre qui passe minuit


def current_mode(now: datetime) -> tuple[str, int]:
    """→ ("night"|"active"|"normal", refresh_s)"""
    t = now.time()
    night = SCHED.get("night")
    if night:
        # Nuits de vendredi→samedi et samedi→dimanche : dernier tram plus tard (start_weekend).
        start = night["start"]
        if now.weekday() in (5, 6) and night.get("start_weekend"):
            start = night["start_weekend"]
        if _in_window(t, start, night["end"]):
            return "night", int(night.get("refresh_s", 1800))
    active = SCHED.get("active")
    if active and _in_window(t, active["start"], active["end"]):
        return "active", int(active.get("refresh_s", 60))
    return "normal", int(SCHED.get("normal", {}).get("refresh_s", 300))


def build_image(now: datetime) -> tuple[bytes, dict]:
    mode, refresh = current_mode(now)
    info = {"mode": mode, "refresh_s": refresh, "stale": False, "error": None, "n_departures": 0}
    if mode == "night":
        first = None
        if client is not None:
            try:
                dep = client.get_first_departure_after(now)   # horaires théoriques, cache 120 s
                first = dep.expected if dep else None
            except Exception as e:  # jamais bloquer l'écran nuit
                log.warning("premier tram indisponible : %s", e)
        img = render.render_night(now, cfg, next_active=SCHED.get("night", {}).get("end", "06:00"),
                                  first_tram=first)
        info["first_tram"] = first.isoformat() if first else None
    elif client is None:
        res = DeparturesResult(stale=True, error=_client_error)
        plans = compute_all(cfg["people"], [], now)
        img = render.render_screen(plans, [], TrafficResult(), now, cfg, stale=True)
        info.update(stale=True, error=_client_error)
    else:
        res = client.get_departures()
        traffic = client.get_traffic()
        plans = compute_all(cfg["people"], res.times, now, int(cfg.get("render", {}).get("next_departures", 4)))
        img = render.render_screen(plans, res.times, traffic, now, cfg, stale=res.stale,
                                   theoretical=res.theoretical_times)
        info.update(stale=res.stale, error=res.error, n_departures=len(res.departures),
                    fetched_at=res.fetched_at.isoformat() if res.fetched_at else None)
        if res.stale:
            log.warning("API PRIM indisponible : %s", res.error)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), info


def get_png(force: bool = False) -> tuple[bytes, dict]:
    with _lock:
        age = time.monotonic() - _state["generated_mono"]
        if _state["png"] is None or force or age >= MIN_REGEN:
            now = datetime.now(TZ)
            png, info = build_image(now)
            _state.update(png=png, generated_mono=time.monotonic(), generated_at=now, **info)
            log.info("image régénérée (%s, %d départs, stale=%s)", info["mode"], info["n_departures"], info["stale"])
        return _state["png"], {k: v for k, v in _state.items() if k != "png"}


@app.get("/kindle.png")
def kindle_png():
    png, info = get_png(force=request.args.get("force") == "1")
    resp = Response(png, mimetype="image/png")
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Refresh-Seconds"] = str(info.get("refresh_s", 300))
    resp.headers["X-Mode"] = str(info.get("mode"))
    return resp


@app.get("/health")
def health():
    _, info = get_png()
    now = datetime.now(TZ)
    gen = info.get("generated_at")
    return jsonify({
        "ok": not info.get("stale", False),
        "mode": info.get("mode"),
        "refresh_s": info.get("refresh_s"),
        "stale": info.get("stale"),
        "error": info.get("error"),
        "n_departures": info.get("n_departures"),
        "image_age_s": round((now - gen).total_seconds(), 1) if gen else None,
        "fetched_at": info.get("fetched_at"),
        "now": now.isoformat(),
    })


@app.get("/")
def index():
    _, info = get_png()
    refresh = info.get("refresh_s", 300)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="{refresh}"><title>Kindle T2</title>
<style>html,body{{margin:0;background:#fff}}img{{display:block;width:100vw;max-width:758px;margin:0 auto}}</style>
</head><body><img src="/kindle.png?t={int(time.time())}" width="758" height="1024"></body></html>"""


if __name__ == "__main__":
    import signal

    # Service de fond : un Ctrl+C parasite (console partagée, fermeture d'un autre outil)
    # ne doit pas l'arrêter. Pour l'arrêter : fermer la fenêtre, ou arrêter la tâche.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)
    srv = cfg.get("server", {})
    host, port = srv.get("host", "0.0.0.0"), int(srv.get("port", 8080))
    log.info("Serveur Kindle T2 sur http://%s:%d/kindle.png", host, port)
    app.run(host=host, port=port, threaded=True)
