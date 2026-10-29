"""Appelle l'API PRIM une fois et affiche les prochains départs T2 à Pont de Bezons.

À lancer en premier pour valider la clé (.env) et les identifiants (config.yaml) :
    python test_prim.py
Option --raw : affiche aussi le JSON brut du premier quai (debug).
"""
import json
import sys
from datetime import datetime

import requests

from prim_client import STOP_MONITORING_URL, PrimClient, load_api_key, load_config

if hasattr(sys.stdout, "reconfigure"):  # console Windows en cp1252 → UTF-8
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    cfg = load_config()
    try:
        key = load_api_key()
    except RuntimeError as e:
        print("ERREUR :", e)
        return 2

    stop = cfg["stop"]
    print(f"Arrêt : {stop['name']}  quais={stop['stop_point_ids']}  ligne={stop['line_name']} ({stop['line_id']})")
    print(f"Clé   : {key[:4]}…{key[-4:]} ({len(key)} caractères)\n")

    # 1) appel brut sur le premier quai pour voir le code HTTP exact
    sp = stop["stop_point_ids"][0]
    r = requests.get(
        STOP_MONITORING_URL,
        params={"MonitoringRef": f"STIF:StopPoint:Q:{sp}:"},
        headers={"apiKey": key, "Accept": "application/json"},
        timeout=15,
    )
    print(f"GET stop-monitoring (quai {sp}) → HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:800])
        print("\n→ 401/403 : clé invalide ou API 'Prochains passages' non souscrite sur PRIM.")
        print("→ 404/400 : identifiant d'arrêt non reconnu, relancer find_ids.py.")
        return 1
    if "--raw" in sys.argv:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2)[:6000])

    # 2) passage par le client (fusion des deux quais, filtre T2, tri)
    client = PrimClient(cfg, key)
    res = client.get_departures(force=True)
    if res.error:
        print("ERREUR client :", res.error)
        return 1
    now = datetime.now(client.tz)
    print(f"\nProchains départs T2 → {stop['destination']} (maintenant {now:%H:%M}) :")
    if not res.departures:
        print("  (aucun passage annoncé — service terminé ? ou mauvais quai)")
    for d in res.departures:
        mins = int((d.expected - now).total_seconds() // 60)
        delay = f"  retard +{d.delay_min} min" if d.delay_min > 0 else ""
        kind = "théorique " if d.theoretical else "temps réel"
        print(f"  {d.expected:%H:%M}  dans {mins:>3} min   {kind}  → {d.destination[:34]}  [quai {d.stop_point}]{delay}")
    if client.theo_error:
        print("  (horaires théoriques indisponibles :", client.theo_error, ")")

    traffic = client.get_traffic(force=True)
    print("\nTrafic :", "PERTURBÉ — " + traffic.message if traffic.disrupted else traffic.message,
          f"(erreur: {traffic.error})" if traffic.error else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
