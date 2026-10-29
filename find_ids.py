"""Cherche les identifiants IDFM (arrêt + ligne) de "Pont de Bezons" sur le tram T2.

Utilise l'open data IDFM (sans clé). Affiche les candidats et propose les ids
à mettre dans config.yaml.
"""
import json
import sys

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE ="https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/arrets-lignes/records"


def query(where: str, limit: int = 50):
    r = requests.get(BASE, params={"where": where, "limit": limit}, timeout=20)
    r.raise_for_status()
    return r.json().get("results", [])


def main():
    stop = sys.argv[1] if len(sys.argv) > 1 else "Pont de Bezons"
    rows = query(f'stop_name like "{stop}"')
    if not rows:
        print("Aucun arrêt trouvé pour", stop)
        return
    print(f"{len(rows)} enregistrement(s) pour « {stop} » :\n")
    for r in rows:
        print(
            f"  stop_id={r.get('stop_id')}  id={r.get('id')}  route_long_name={r.get('route_long_name')}  "
            f"shortname={r.get('shortname')}  mode={r.get('mode')}  operator={r.get('operatorname')}  "
            f"stop_name={r.get('stop_name')}"
        )
    t2 = [r for r in rows if "T2" in str(r.get("route_long_name", "")) or str(r.get("shortname")) == "T2"]
    if t2:
        print("\nCandidats T2 :")
        for r in t2:
            print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
