"""Calcul "partir dans X min" pour chaque personne.

Règle : premier tram tel que (heure_tram − marche − marge) ≥ maintenant.
X = minutes entières restantes avant cet instant de départ ; X ≤ 0 → "Maintenant !".
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Plan:
    name: str
    walk_min: int
    margin_min: int
    leave_in_min: int | None          # None si aucun tram exploitable
    target_tram: datetime | None      # tram visé
    next_departures: list[datetime]   # les N prochains départs (tous, pas seulement ceux atteignables)

    @property
    def label(self) -> str:
        if self.leave_in_min is None:
            return "—"
        if self.leave_in_min <= 0:
            return "Maintenant !"
        return f"{self.leave_in_min} min"

    @property
    def leave_now(self) -> bool:
        return self.leave_in_min is not None and self.leave_in_min <= 0


def compute_plan(
    name: str,
    walk_min: int,
    margin_min: int,
    departures: list[datetime],
    now: datetime,
    next_n: int = 4,
) -> Plan:
    deps = sorted(departures)
    lead = timedelta(minutes=walk_min + margin_min)
    target = None
    leave_in = None
    for tram in deps:
        leave_at = tram - lead
        if leave_at >= now:
            target = tram
            leave_in = int((leave_at - now).total_seconds() // 60)
            break
    # Cas limite : un tram part dans moins de (marche+marge) mais c'est le seul
    # → on l'affiche quand même avec "Maintenant !" plutôt que rien.
    if target is None and deps:
        last = deps[-1]
        if last > now:
            target, leave_in = last, 0
    return Plan(
        name=name,
        walk_min=walk_min,
        margin_min=margin_min,
        leave_in_min=leave_in,
        target_tram=target,
        next_departures=[d for d in deps if d >= now][:next_n],
    )


def compute_all(people: list[dict], departures: list[datetime], now: datetime, next_n: int = 4) -> list[Plan]:
    return [
        compute_plan(p["name"], int(p["walk_min"]), int(p.get("margin_min", 1)), departures, now, next_n)
        for p in people
    ]


if __name__ == "__main__":
    from datetime import timezone
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("Europe/Paris")
    now = datetime.now(tz).replace(second=0, microsecond=0)
    fake = [now + timedelta(minutes=m) for m in (3, 8, 14, 20, 27)]
    for p in compute_all([{"name": "Cam", "walk_min": 9}, {"name": "Oliv", "walk_min": 6}], fake, now):
        print(p.name, "→", p.label, "tram", p.target_tram.strftime("%H:%M") if p.target_tram else None,
              [d.strftime("%H:%M") for d in p.next_departures])
