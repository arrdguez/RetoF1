"""
Estadísticas históricas por piloto en el Autódromo Hermanos Rodríguez.

Fuente: API Jolpica (sucesora de Ergast), endpoint por circuito `rodriguez`.
Todo se calcula a partir de resultados reales; no hay valores escritos a mano.

Métricas por piloto:
- starts, wins, podiums, poles, front_rows, fastest_laps, points_finishes
- dnfs, avg_finish (solo clasificados), best_finish, avg_grid, avg_positions_gained
- seasons y resultado por año

Se calculan dos vistas:
- all_time: todas las ediciones (1963-1970, 1986-1992, 2015-hoy)
- modern:   desde 2015 (trazado actual con el Foro Sol)
"""

from __future__ import annotations

import csv
import json
import logging
import time
from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Optional

import requests

from config.settings import PROCESSED_DATA_DIR, RAW_DATA_DIR

logger = logging.getLogger(__name__)

BASE_URL = "https://api.jolpi.ca/ergast/f1"
CIRCUIT_ID = "rodriguez"
MODERN_ERA_START = 2015
CACHE_DIR = RAW_DATA_DIR / "mexico"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_json(path: str, params: Optional[Dict[str, Any]] = None, retries: int = 5, timeout: int = 30) -> Dict[str, Any]:
    """GET con reintentos y espera exponencial (Jolpica se satura en fines de semana de carrera)."""
    url = f"{BASE_URL}/{path}.json"
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params or {"limit": 100}, timeout=timeout)
            if resp.status_code == 429:
                raise requests.HTTPError("429 rate limited")
            resp.raise_for_status()
            return resp.json()["MRData"]
        except (requests.RequestException, ValueError) as exc:
            wait = 2 ** attempt
            logger.warning("Intento %s/%s falló para %s (%s). Reintento en %ss", attempt, retries, path, exc, wait)
            time.sleep(wait)
    raise RuntimeError(f"No se pudo descargar {url} tras {retries} intentos")


def _cached(name: str, path: str) -> Dict[str, Any]:
    """Lee de data/raw/mexico/<name>.json; si no existe, descarga y guarda."""
    file = CACHE_DIR / f"{name}.json"
    if file.exists():
        return json.loads(file.read_text(encoding="utf-8"))
    data = _get_json(path)
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.4)  # respeta el rate limit de Jolpica
    return data


def fetch_mexico_editions() -> List[Dict[str, str]]:
    """Ediciones del GP en el circuito (temporada, ronda, fecha). No se cachea: es barata y cambia."""
    races = _get_json(f"circuits/{CIRCUIT_ID}/races")["RaceTable"]["Races"]
    return [{"season": r["season"], "round": r["round"], "date": r["date"]} for r in races]


def fetch_mexico_results() -> List[Dict[str, Any]]:
    """Resultados de carrera de cada edición ya disputada (una petición pequeña por edición)."""
    today = date.today().isoformat()
    races = []
    for ed in fetch_mexico_editions():
        if ed["date"] >= today:
            continue  # edición futura o en curso: aún sin resultados
        data = _cached(f"{ed['season']}_results", f"{ed['season']}/{ed['round']}/results")
        race_list = data["RaceTable"]["Races"]
        if race_list:
            races.append(race_list[0])
            logger.info("Resultados %s: %s pilotos", ed["season"], len(race_list[0].get("Results", [])))
    return races


def fetch_mexico_qualifying() -> Dict[str, str]:
    """{season: driverId del poleman} para ediciones con datos de clasificación (Ergast: 1994+)."""
    today = date.today().isoformat()
    poles = {}
    for ed in fetch_mexico_editions():
        if ed["date"] >= today or int(ed["season"]) < 1994:
            continue
        try:
            data = _cached(f"{ed['season']}_qualifying", f"{ed['season']}/{ed['round']}/qualifying")
        except RuntimeError as exc:  # complementario: si falla, se usa grid == 1
            logger.warning("Sin clasificación %s: %s", ed["season"], exc)
            continue
        for race in data["RaceTable"]["Races"]:
            for q in race.get("QualifyingResults", []):
                if q.get("position") == "1":
                    poles[ed["season"]] = q["Driver"]["driverId"]
    return poles


def fetch_grid(season: str) -> List[str]:
    """driverIds inscritos en una temporada (para marcar quién está en la parrilla actual)."""
    try:
        data = _cached(f"grid_{season}", f"{season}/drivers")
        return [d["driverId"] for d in data["DriverTable"]["Drivers"]]
    except RuntimeError as exc:
        logger.warning("No se pudo obtener la parrilla %s: %s", season, exc)
        return []


def _empty_stats() -> Dict[str, Any]:
    return {
        "starts": 0, "wins": 0, "podiums": 0, "poles": 0, "front_rows": 0,
        "fastest_laps": 0, "points_finishes": 0, "dnfs": 0,
        "_finishes": [], "_grids": [], "_gains": [], "seasons": [], "results_by_year": {},
    }


def compute_driver_stats(
    races: List[Dict[str, Any]],
    poles_by_season: Dict[str, str],
    min_season: Optional[int] = None,
) -> List[Dict[str, Any]]:
    stats: Dict[str, Dict[str, Any]] = defaultdict(_empty_stats)
    info: Dict[str, Dict[str, str]] = {}

    for race in races:
        season = race["season"]
        if min_season and int(season) < min_season:
            continue
        results = race.get("Results", [])
        if not results:
            continue  # edición sin disputar aún (p. ej. la del año en curso)

        pole_driver = poles_by_season.get(season)

        for res in results:
            drv = res["Driver"]
            did = drv["driverId"]
            info[did] = {
                "code": drv.get("code") or drv["familyName"][:3].upper(),
                "name": f"{drv['givenName']} {drv['familyName']}",
                "nationality": drv.get("nationality", ""),
            }
            s = stats[did]
            s["starts"] += 1
            s["seasons"].append(int(season))

            pos_text = res.get("positionText", "")
            classified = pos_text.isdigit()
            pos = int(res["position"]) if classified else None
            grid = int(res.get("grid", 0) or 0)

            if classified:
                s["_finishes"].append(pos)
                if pos == 1:
                    s["wins"] += 1
                if pos <= 3:
                    s["podiums"] += 1
                if pos <= 10:
                    s["points_finishes"] += 1
                if grid > 0:
                    s["_gains"].append(grid - pos)
            elif pos_text == "R":
                s["dnfs"] += 1

            if grid > 0:
                s["_grids"].append(grid)
                if grid <= 2:
                    s["front_rows"] += 1

            # Pole: dato de clasificación si existe; si no, salida desde P1.
            if (pole_driver and pole_driver == did) or (not pole_driver and grid == 1):
                s["poles"] += 1

            if res.get("FastestLap", {}).get("rank") == "1":
                s["fastest_laps"] += 1

            s["results_by_year"][season] = f"P{pos}" if classified else (res.get("status") or pos_text)

    rows = []
    for did, s in stats.items():
        fin, grids, gains = s.pop("_finishes"), s.pop("_grids"), s.pop("_gains")
        rows.append({
            "driver_id": did,
            **info[did],
            **s,
            "avg_finish": round(sum(fin) / len(fin), 2) if fin else None,
            "best_finish": min(fin) if fin else None,
            "avg_grid": round(sum(grids) / len(grids), 2) if grids else None,
            "avg_positions_gained": round(sum(gains) / len(gains), 2) if gains else None,
            "win_rate_pct": round(100 * s["wins"] / s["starts"], 1),
            "podium_rate_pct": round(100 * s["podiums"] / s["starts"], 1),
            "dnf_rate_pct": round(100 * s["dnfs"] / s["starts"], 1),
        })

    rows.sort(key=lambda r: (-r["wins"], -r["podiums"], -r["poles"], r["avg_finish"] or 99))
    return rows


def compute_winners_by_year(races: List[Dict[str, Any]], poles_by_season: Dict[str, str]) -> List[Dict[str, Any]]:
    out = []
    for race in races:
        results = race.get("Results", [])
        if not results:
            continue
        winner = next((r for r in results if r.get("position") == "1"), None)
        podium = [r["Driver"].get("code", r["Driver"]["familyName"][:3].upper())
                  for r in sorted(results, key=lambda r: int(r["position"]))[:3]]
        fl = next((r for r in results if r.get("FastestLap", {}).get("rank") == "1"), None)
        pole_id = poles_by_season.get(race["season"])
        pole = next((r for r in results if r["Driver"]["driverId"] == pole_id), None) if pole_id \
            else next((r for r in results if r.get("grid") == "1"), None)
        out.append({
            "season": int(race["season"]),
            "winner": winner["Driver"].get("code") if winner else None,
            "winner_team": winner["Constructor"]["name"] if winner else None,
            "winner_grid": int(winner["grid"]) if winner else None,
            "podium": podium,
            "pole": pole["Driver"].get("code") if pole else None,
            "pole_won": bool(pole and winner and pole["Driver"]["driverId"] == winner["Driver"]["driverId"]),
            "fastest_lap": fl["Driver"].get("code") if fl else None,
        })
    return out


def build_mexico_history(current_season: str = "2026") -> Dict[str, Any]:
    races = fetch_mexico_results()
    poles = fetch_mexico_qualifying()
    grid_now = set(fetch_grid(current_season))

    all_time = compute_driver_stats(races, poles)
    modern = compute_driver_stats(races, poles, min_season=MODERN_ERA_START)
    for row in all_time + modern:
        row["on_current_grid"] = row["driver_id"] in grid_now

    winners = compute_winners_by_year(races, poles)
    modern_winners = [w for w in winners if w["season"] >= MODERN_ERA_START]
    payload = {
        "circuit": "Autódromo Hermanos Rodríguez",
        "source": "Jolpica / Ergast API",
        "editions_with_results": len(winners),
        "current_season": current_season,
        "current_grid_driver_ids": sorted(grid_now),
        "modern_era_summary": {
            "editions": len(modern_winners),
            "pole_to_win_pct": round(100 * sum(w["pole_won"] for w in modern_winners) / len(modern_winners), 1)
            if modern_winners else None,
            "avg_winner_grid": round(sum(w["winner_grid"] for w in modern_winners) / len(modern_winners), 2)
            if modern_winners else None,
        },
        "winners_by_year": winners,
        "driver_stats_modern": modern,
        "driver_stats_all_time": all_time,
    }

    out_json = PROCESSED_DATA_DIR / "mexico_driver_stats.json"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_cols = ["code", "name", "starts", "wins", "podiums", "poles", "front_rows", "fastest_laps",
                "points_finishes", "dnfs", "avg_finish", "best_finish", "avg_grid",
                "avg_positions_gained", "win_rate_pct", "podium_rate_pct", "dnf_rate_pct", "on_current_grid"]
    for label, rows in (("modern", modern), ("all_time", all_time)):
        with open(PROCESSED_DATA_DIR / f"mexico_driver_stats_{label}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=csv_cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    return payload


def print_history(payload: Dict[str, Any], top: int = 15) -> None:
    from rich.console import Console
    from rich.table import Table

    console = Console()

    t = Table(title="Ganadores del GP de México por edición", header_style="bold cyan")
    for col in ("Año", "Ganador", "Equipo", "Salió", "Pole", "Pole→Win", "Podio", "V. Rápida"):
        t.add_column(col)
    for w in payload["winners_by_year"]:
        t.add_row(str(w["season"]), w["winner"] or "-", w["winner_team"] or "-", f"P{w['winner_grid']}",
                  w["pole"] or "-", "✓" if w["pole_won"] else "", " - ".join(w["podium"]), w["fastest_lap"] or "-")
    console.print(t)

    m = payload["modern_era_summary"]
    console.print(f"\n[bold]Era moderna ({MODERN_ERA_START}+):[/bold] {m['editions']} ediciones | "
                  f"la pole ganó el {m['pole_to_win_pct']}% | el ganador salió en promedio de P{m['avg_winner_grid']}\n")

    def driver_table(rows: List[Dict[str, Any]], title: str) -> Table:
        tb = Table(title=title, header_style="bold magenta")
        for col in ("Piloto", "Parrilla 2026", "Carreras", "Victorias", "Podios", "Poles", "V.Ráp",
                    "Pts", "DNF", "Prom. final", "Mejor", "Prom. salida", "Pos. ganadas"):
            tb.add_column(col, justify="right" if col not in ("Piloto",) else "left")
        for r in rows[:top]:
            tb.add_row(
                f"{r['code']} ({r['name']})", "✓" if r.get("on_current_grid") else "",
                str(r["starts"]), str(r["wins"]), str(r["podiums"]), str(r["poles"]), str(r["fastest_laps"]),
                str(r["points_finishes"]), str(r["dnfs"]),
                str(r["avg_finish"] or "-"), f"P{r['best_finish']}" if r["best_finish"] else "-",
                str(r["avg_grid"] or "-"), str(r["avg_positions_gained"] if r["avg_positions_gained"] is not None else "-"),
            )
        return tb

    console.print(driver_table(payload["driver_stats_modern"], f"Estadística por piloto - era moderna ({MODERN_ERA_START}+)"))
    console.print(driver_table(payload["driver_stats_all_time"], "Estadística por piloto - histórico completo (1963+)"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print_history(build_mexico_history())
