"""Client PRIM (Île-de-France Mobilités) : prochains départs du T2 à Pont de Bezons.

- cache mémoire de `prim.cache_s` secondes (30 s par défaut) ;
- en cas d'erreur réseau / HTTP, on garde la dernière réponse valide et on
  marque le résultat `stale=True` (l'écran affichera "données indisponibles") ;
- infos trafic via general-message (optionnel, même mécanique).

Usage :
    from prim_client import PrimClient
    c = PrimClient()                   # lit config.yaml + .env
    r = c.get_departures()             # DeparturesResult
"""
from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import yaml
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
STOP_MONITORING_URL = "https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring"
GENERAL_MESSAGE_URL = "https://prim.iledefrance-mobilites.fr/marketplace/general-message"
NAVITIA_URL = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia"


def load_config(path: Path | None = None) -> dict:
    with open(path or HERE / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_api_key() -> str:
    load_dotenv(HERE / ".env")
    key = os.environ.get("PRIM_API_KEY", "").strip()
    if not key or key == "colle_ta_cle_ici":
        raise RuntimeError(
            "Clé PRIM absente : copie .env.example en .env et renseigne PRIM_API_KEY."
        )
    return key


@dataclass
class Departure:
    expected: datetime          # heure de départ attendue (temps réel), tz-aware
    aimed: datetime | None      # heure théorique
    destination: str
    line: str
    stop_point: str
    theoretical: bool = False   # True = horaire théorique (Navitia), pas de temps réel

    @property
    def delay_min(self) -> int:
        if not self.aimed:
            return 0
        return round((self.expected - self.aimed).total_seconds() / 60)


@dataclass
class DeparturesResult:
    departures: list[Departure] = field(default_factory=list)
    fetched_at: datetime | None = None   # heure de la dernière réponse API valide
    stale: bool = False                  # True si l'API est tombée et qu'on sert l'ancien résultat
    error: str | None = None             # message de la dernière erreur

    @property
    def times(self) -> list[datetime]:
        return [d.expected for d in self.departures]

    @property
    def theoretical_times(self) -> set[datetime]:
        return {d.expected for d in self.departures if d.theoretical}


@dataclass
class TrafficResult:
    disrupted: bool = False
    message: str = ""
    stale: bool = False
    error: str | None = None


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _first_text(value) -> str:
    """Les champs SIRI arrivent comme [{"value": "..."}] ou comme chaîne."""
    if isinstance(value, list):
        if not value:
            return ""
        value = value[0]
    if isinstance(value, dict):
        return str(value.get("value", ""))
    return str(value or "")


class PrimClient:
    def __init__(self, config: dict | None = None, api_key: str | None = None):
        self.cfg = config or load_config()
        self.api_key = api_key or load_api_key()
        prim = self.cfg.get("prim", {})
        self.cache_s = float(prim.get("cache_s", 30))
        self.timeout_s = float(prim.get("timeout_s", 10))
        self.max_departures = int(prim.get("max_departures", 8))
        self.cache_peak_s = float(prim.get("cache_peak_s", self.cache_s))
        self.secondary_interval_s = float(prim.get("secondary_interval_s", 900))
        self.traffic_cache_s = float(prim.get("traffic_cache_s", 600))
        self.navitia_stop_points: list[str] = [str(s) for s in prim.get("navitia_stop_points", [])]
        self.navitia_count = int(prim.get("navitia_count", 8))
        self.navitia_cache_s = float(prim.get("navitia_cache_s", 1800))
        self.tz = ZoneInfo(self.cfg.get("timezone", "Europe/Paris"))

        stop = self.cfg["stop"]
        self.stop_point_ids: list[str] = [str(s) for s in stop["stop_point_ids"]]
        self.secondary_stop_point_ids: list[str] = [str(s) for s in stop.get("secondary_stop_point_ids", [])]
        self.line_ref = f"STIF:Line::{stop['line_id']}:"

        self._lock = threading.Lock()
        self._last: DeparturesResult = DeparturesResult()
        self._last_fetch_mono = 0.0
        self._real: list[Departure] = []          # derniers passages temps réel valides
        self._real_at: datetime | None = None
        self._secondary: list[Departure] = []
        self._secondary_fetch_mono = 0.0
        self._rt_blocked_until = 0.0              # quota épuisé (429) : pas d'appel avant
        self._traffic: TrafficResult = TrafficResult()
        self._traffic_fetch_mono = 0.0
        self._theo: list[Departure] = []
        self._theo_fetch_mono = 0.0
        self.theo_error: str | None = None
        self.calls = {"realtime": 0, "traffic": 0, "navitia": 0}   # compteur d'appels (diagnostic)

        self._session = requests.Session()
        self._session.headers.update({"apiKey": self.api_key, "Accept": "application/json"})

    # ------------------------------------------------------------------ départs
    def get_departures(self, force: bool = False, peak: bool = False) -> DeparturesResult:
        """Passages à venir : temps réel (rafraîchi toutes les cache_s, ou cache_peak_s en
        pointe) complété par les horaires théoriques. Si le temps réel est indisponible
        (quota 429, panne), on garde les derniers passages réels encore à venir, puis les
        théoriques, et stale=True avec l'erreur."""
        with self._lock:
            interval = self.cache_peak_s if peak else self.cache_s
            age = time.monotonic() - self._last_fetch_mono
            if not force and self._last_fetch_mono and age < interval:
                return self._last
            error = None
            if time.monotonic() < self._rt_blocked_until and not force:
                error = f"quota temps réel épuisé, reprise dans {int((self._rt_blocked_until - time.monotonic()) / 60)} min"
            else:
                try:
                    self._real = self._fetch_all_departures()
                    self._real_at = datetime.now(self.tz)
                except Exception as e:  # réseau, HTTP, JSON…
                    error = f"{type(e).__name__}: {e}"
            now = datetime.now(timezone.utc)
            real = [d for d in self._real if d.expected >= now]
            deps = self._complete_with_theoretical(real)
            self._last = DeparturesResult(departures=deps, fetched_at=self._real_at,
                                          stale=error is not None, error=error)
            self._last_fetch_mono = time.monotonic()
            return self._last

    def _fetch_all_departures(self) -> list[Departure]:
        seen: dict[tuple, Departure] = {}
        errors = []
        for sp in self.stop_point_ids:
            try:
                for d in self._fetch_stop_point(sp):
                    seen.setdefault((d.expected.isoformat(), d.destination), d)
            except Exception as e:
                errors.append(f"{sp}: {type(e).__name__}: {e}")
        # second quai : rarement interrogé (jamais vu actif), on réutilise sa dernière réponse
        if self.secondary_stop_point_ids and not errors:
            if time.monotonic() - self._secondary_fetch_mono >= self.secondary_interval_s:
                try:
                    self._secondary = [d for sp in self.secondary_stop_point_ids for d in self._fetch_stop_point(sp)]
                except Exception as e:
                    errors.append(f"{self.secondary_stop_point_ids}: {type(e).__name__}: {e}")
                self._secondary_fetch_mono = time.monotonic()
            for d in self._secondary:
                seen.setdefault((d.expected.isoformat(), d.destination), d)
        if not seen and errors:
            raise RuntimeError("; ".join(errors))
        now = datetime.now(timezone.utc)
        deps = sorted((d for d in seen.values() if d.expected >= now), key=lambda d: d.expected)
        return deps[: self.max_departures]

    def _fetch_stop_point(self, stop_point_id: str) -> list[Departure]:
        self.calls["realtime"] += 1
        r = self._session.get(
            STOP_MONITORING_URL,
            params={"MonitoringRef": f"STIF:StopPoint:Q:{stop_point_id}:"},
            timeout=self.timeout_s,
        )
        self._note_rate_limit(r)
        r.raise_for_status()
        return self.parse_stop_monitoring(r.json(), stop_point_id)

    def _note_rate_limit(self, r: requests.Response) -> None:
        """429 : on respecte Retry-After, plafonné à 15 min (le quota peut être relevé sur le
        portail à tout moment : on re-sonde régulièrement plutôt que d'attendre minuit)."""
        if r.status_code == 429:
            try:
                wait = float(r.headers.get("retry-after") or r.headers.get("ratelimit-reset") or 300)
            except ValueError:
                wait = 300
            self._rt_blocked_until = time.monotonic() + max(5.0, min(wait, 900))


    def parse_stop_monitoring(self, payload: dict, stop_point_id: str = "") -> list[Departure]:
        out: list[Departure] = []
        deliveries = (
            payload.get("Siri", {}).get("ServiceDelivery", {}).get("StopMonitoringDelivery", [])
        )
        for delivery in deliveries:
            for visit in delivery.get("MonitoredStopVisit", []) or []:
                mvj = visit.get("MonitoredVehicleJourney", {})
                line = _first_text(mvj.get("LineRef"))
                if self.line_ref and line and line != self.line_ref:
                    continue
                call = mvj.get("MonitoredCall", {})
                expected = _parse_iso(
                    _first_text(call.get("ExpectedDepartureTime"))
                    or _first_text(call.get("ExpectedArrivalTime"))
                )
                if not expected:
                    continue
                aimed = _parse_iso(
                    _first_text(call.get("AimedDepartureTime"))
                    or _first_text(call.get("AimedArrivalTime"))
                )
                dest = _first_text(mvj.get("DestinationName")) or _first_text(
                    call.get("DestinationDisplay")
                )
                out.append(
                    Departure(
                        expected=expected.astimezone(self.tz),
                        aimed=aimed.astimezone(self.tz) if aimed else None,
                        destination=dest,
                        line=line,
                        stop_point=stop_point_id,
                    )
                )
        return out

    def get_first_departure_after(self, when: datetime) -> Departure | None:
        """Premier départ théorique à partir de `when` (écran nuit : premier tram du matin)."""
        with self._lock:
            theo = self._get_theoretical()
        for d in theo:
            if d.expected >= when:
                return d
        return None

    # ------------------------------------------------------------------ théorique (Navitia)
    def _complete_with_theoretical(self, real: list[Departure]) -> list[Departure]:
        """Garde les passages temps réel, puis ajoute les horaires théoriques qui suivent le
        dernier passage réel (à plus d'une minute), jusqu'à max_departures."""
        theo = self._get_theoretical()
        if not theo:
            return real
        last_real = max((d.expected for d in real), default=datetime.now(timezone.utc))
        cutoff = last_real + timedelta(minutes=1)
        extra = [d for d in theo if d.expected >= cutoff]
        merged = sorted(real + extra, key=lambda d: d.expected)
        return merged[: self.max_departures]

    def _get_theoretical(self) -> list[Departure]:
        """Horaires théoriques Navitia, cache navitia_cache_s ; en cas d'erreur, on garde les
        précédents (filtrés sur le futur) et on note l'erreur dans theo_error."""
        if not self.navitia_stop_points:
            return []
        age = time.monotonic() - self._theo_fetch_mono
        if self._theo_fetch_mono and age < self.navitia_cache_s:
            pass
        else:
            try:
                self._theo = self._fetch_theoretical()
                self.theo_error = None
            except Exception as e:
                self.theo_error = f"{type(e).__name__}: {e}"
            self._theo_fetch_mono = time.monotonic()
        now = datetime.now(timezone.utc)
        return [d for d in self._theo if d.expected >= now]

    def _fetch_theoretical(self) -> list[Departure]:
        out: dict[str, Departure] = {}
        line_code = str(self.cfg["stop"].get("line_name", ""))
        for sp in self.navitia_stop_points:
            self.calls["navitia"] += 1
            r = self._session.get(
                f"{NAVITIA_URL}/stop_points/{sp}/departures",
                params={"count": self.navitia_count, "data_freshness": "base_schedule",
                        "from_datetime": datetime.now(self.tz).strftime("%Y%m%dT%H%M%S")},
                timeout=self.timeout_s,
            )
            r.raise_for_status()
            for dep in r.json().get("departures", []):
                info = dep.get("display_informations", {})
                if line_code and info.get("code") != line_code:
                    continue
                raw = dep["stop_date_time"]["departure_date_time"]  # ex. 20261029T234500, heure locale
                t = datetime.strptime(raw, "%Y%m%dT%H%M%S").replace(tzinfo=self.tz)
                key = t.isoformat()
                out.setdefault(key, Departure(
                    expected=t, aimed=t, destination=info.get("direction", ""),
                    line=info.get("code", ""), stop_point=sp.rsplit(":", 1)[-1], theoretical=True,
                ))
        return sorted(out.values(), key=lambda d: d.expected)

    # ------------------------------------------------------------------ trafic
    def get_traffic(self, force: bool = False, cache_s: float | None = None) -> TrafficResult:
        cache_s = self.traffic_cache_s if cache_s is None else cache_s
        with self._lock:
            age = time.monotonic() - self._traffic_fetch_mono
            if not force and self._traffic_fetch_mono and age < cache_s:
                return self._traffic
            try:
                self._traffic = self._fetch_traffic()
            except Exception as e:
                self._traffic = TrafficResult(
                    disrupted=self._traffic.disrupted,
                    message=self._traffic.message,
                    stale=True,
                    error=f"{type(e).__name__}: {e}",
                )
            self._traffic_fetch_mono = time.monotonic()
            return self._traffic

    def _fetch_traffic(self) -> TrafficResult:
        self.calls["traffic"] += 1
        r = self._session.get(
            GENERAL_MESSAGE_URL, params={"LineRef": self.line_ref}, timeout=self.timeout_s
        )
        r.raise_for_status()
        return self.parse_general_message(r.json())

    @staticmethod
    def parse_general_message(payload: dict) -> TrafficResult:
        msgs: list[str] = []
        deliveries = (
            payload.get("Siri", {}).get("ServiceDelivery", {}).get("GeneralMessageDelivery", [])
        )
        for delivery in deliveries:
            for info in delivery.get("InfoMessage", []) or []:
                content = info.get("Content", {})
                for m in content.get("Message", []) or []:
                    txt = _first_text(m.get("MessageText"))
                    if txt:
                        msgs.append(" ".join(txt.split()))
        if not msgs:
            return TrafficResult(disrupted=False, message="Trafic normal")
        # message le plus court en premier : plus lisible sur un e-ink
        msgs.sort(key=len)
        return TrafficResult(disrupted=True, message=msgs[0])


if __name__ == "__main__":  # petit test manuel
    c = PrimClient()
    res = c.get_departures()
    print("stale:", res.stale, "error:", res.error)
    for d in res.departures:
        print(d.expected.strftime("%H:%M"), d.destination, f"(+{d.delay_min} min)" if d.delay_min else "",
              "[théorique]" if d.theoretical else "[temps réel]")
