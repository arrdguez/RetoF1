"""
Backtest temporal (leave-one-out) del modelo sobre el GP de México 2016-2025.

Para cada año Y se predice con SOLO información disponible antes de la carrera:
  - Forma: clasificación de pilotos/constructores ANTES del GP de México Y.
  - Afinidad: resultados de México de años ANTERIORES a Y (sin fuga temporal).

Se puntúa con el sistema oficial (scoring.py) y se reportan aciertos, puntos
medios y Brier del ganador, además de una referencia simple (líder del campeonato).

Categorías evaluadas: pole, podio (3 casillas) y vuelta rápida.
(Checo y Safety Cars se excluyen: Checo cambió de equipo en 2026 y los SC ya
tienen su propio backtest leave-one-out n=4.)

Uso: python -m src.evaluation.backtest
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List

import requests

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.evaluation.scoring import ChallengeScorer

BASE = "https://api.jolpi.ca/ergast/f1"
MEXICO_ROUND = {
    2015: 17,
    2016: 19,
    2017: 18,
    2018: 19,
    2019: 18,
    2021: 18,
    2022: 20,
    2023: 19,
    2024: 20,
    2025: 20,
}
CACHE = RAW_DATA_DIR / "backtest"
CACHE.mkdir(parents=True, exist_ok=True)


def _get(path: str, params: dict = None) -> Dict[str, Any]:
    url = f"{BASE}/{path}.json"
    for attempt in range(1, 6):
        try:
            r = requests.get(url, params=params or {"limit": 100}, timeout=30)
            r.raise_for_status()
            return r.json()["MRData"]
        except Exception:
            time.sleep(2**attempt)
    raise RuntimeError(f"fallo descargando {url}")


def _cached(name: str, path: str) -> Dict[str, Any]:
    f = CACHE / f"{name}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    data = _get(path)
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.3)
    return data


def load_standings(year: int, round_: int) -> Dict[str, float]:
    d = _cached(f"drivers_{year}_r{round_}", f"{year}/{round_}/driverstandings")
    pts = {}
    for s in d["StandingsTable"]["StandingsLists"][0]["DriverStandings"]:
        pts[s["Driver"]["code"]] = float(s["points"])
    c = _cached(f"ctors_{year}_r{round_}", f"{year}/{round_}/constructorstandings")
    cpts = {}
    for s in c["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]:
        cpts[s["Constructor"]["constructorId"]] = float(s["points"])
    return pts, cpts


def team_of(code: str) -> str:
    """Asigna equipo aproximado por código (suficiente para el backtest)."""
    return code  # no se usa el cruce por equipo en el backtest simple


def mexico_affinity_from(prior_years: List[int]) -> Dict[str, Dict[str, float]]:
    """Afinidad de México usando SOLO los años < Y (sin fuga)."""
    stats: Dict[str, Dict[str, float]] = {}
    for y in prior_years:
        f = RAW_DATA_DIR / "mexico" / f"{y}_results.json"
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        for race in data["RaceTable"]["Races"]:
            for res in race.get("Results", []):
                code = res["Driver"]["code"]
                s = stats.setdefault(
                    code, {"starts": 0, "wins": 0, "pods": 0, "fl": 0, "fin": []}
                )
                pos = res.get("positionText", "")
                s["starts"] += 1
                if pos.isdigit():
                    s["fin"].append(int(pos))
                    if int(pos) == 1:
                        s["wins"] += 1
                    if int(pos) <= 3:
                        s["pods"] += 1
                if res.get("FastestLap", {}).get("rank") == "1":
                    s["fl"] += 1
    out = {}
    for code, s in stats.items():
        starts = s["starts"]
        avg = (sum(s["fin"]) / len(s["fin"])) if s["fin"] else 99.0
        out[code] = {
            "mx_aff": math.log(
                1.0
                + 15 * s["wins"] / starts
                + 3 * s["pods"] / starts
                + 0.5 / max(avg, 1.0)
            ),
            "fl_count": s["fl"],
        }
    return out


def build_skill(
    form: Dict[str, float], aff: Dict[str, Dict[str, float]]
) -> Dict[str, float]:
    # Refleja la filosofía del modelo de producción: la forma actual domina y la
    # afinidad de circuito es un ajuste modesto (15%), no dominante.
    codes = set(form) | set(aff)
    skill = {}
    for c in codes:
        f = math.log(1.0 + form.get(c, 0.0))
        a = aff.get(c, {}).get("mx_aff", 0.0)
        skill[c] = 0.85 * f + 0.15 * a
    return skill


def softmax(skill: Dict[str, float]) -> Dict[str, float]:
    mx = max(skill.values())
    e = {c: math.exp(skill[c] - mx) for c in skill}
    tot = sum(e.values())
    return {c: e[c] / tot for c in e}


def actual_result(year: int) -> Dict[str, Any]:
    f = RAW_DATA_DIR / "mexico" / f"{year}_results.json"
    data = json.loads(f.read_text(encoding="utf-8"))
    race = data["RaceTable"]["Races"][0]
    results = race["Results"]
    classified = [r for r in results if r.get("positionText", "").isdigit()]
    classified.sort(key=lambda r: int(r["position"]))
    top3 = [r["Driver"]["code"] for r in classified[:3]]
    fl = next(
        (
            r["Driver"]["code"]
            for r in results
            if r.get("FastestLap", {}).get("rank") == "1"
        ),
        None,
    )
    pole = next((r["Driver"]["code"] for r in results if r.get("grid") == "1"), None)
    return {
        "p1": top3[0],
        "p2": top3[1],
        "p3": top3[2],
        "fastest_lap": fl,
        "pole": pole,
    }


def run() -> Dict[str, Any]:
    scorer = ChallengeScorer()
    years = sorted(MEXICO_ROUND)
    all_years = years
    rows = []
    brier_win = []
    baseline_correct = 0

    for idx, y in enumerate(years):
        if y < 2016:
            continue  # 2015 no tiene historial moderno previo
        r = MEXICO_ROUND[y]
        form, _ct = load_standings(y, r - 1)
        prior = [yy for yy in all_years if yy < y]
        aff = mexico_affinity_from(prior)
        skill = build_skill(form, aff)
        probs = softmax(skill)

        # predicción por orden de skill
        ranked = sorted(skill, key=skill.get, reverse=True)
        pred_pole = ranked[0]
        pred_p1, pred_p2, pred_p3 = ranked[0], ranked[1], ranked[2]
        # vuelta rápida: skill + historial de FL
        fl_rank = sorted(
            skill,
            key=lambda c: skill[c] + 0.5 * aff.get(c, {}).get("fl_count", 0) / 2,
            reverse=True,
        )
        pred_fl = fl_rank[0]

        act = actual_result(y)

        pred = {
            "pole": pred_pole,
            "p1": pred_p1,
            "p2": pred_p2,
            "p3": pred_p3,
            "fastest_lap": pred_fl,
            "checo_position": "P10",
            "safety_cars": 0,
        }
        act_full = {
            "pole": act["pole"],
            "p1": act["p1"],
            "p2": act["p2"],
            "p3": act["p3"],
            "fastest_lap": act["fastest_lap"],
            "checo_position": "P10",
            "safety_cars": 0,
        }
        # ignora checo y SC en la comparación (los forzamos iguales para no puntuarlos)
        score = scorer.score_prediction(pred, act_full)

        winner_hit = pred_p1 == act["p1"]
        pole_hit = pred_pole == act["pole"]
        leader = max(form, key=form.get)
        baseline_correct += leader == act["p1"]
        # Brier del ganador (multiclase sobre top-k de skill)
        brier = sum(
            (probs.get(c, 0.0) - (1.0 if c == act["p1"] else 0.0)) ** 2 for c in probs
        )
        brier_win.append(brier)

        rows.append(
            {
                "year": y,
                "pred_winner": pred_p1,
                "act_winner": act["p1"],
                "pred_pole": pred_pole,
                "act_pole": act["pole"],
                "pred_podium": [pred_p1, pred_p2, pred_p3],
                "act_podium": act["p1"],
                "pred_fl": pred_fl,
                "act_fl": act["fastest_lap"],
                "winner_hit": winner_hit,
                "pole_hit": pole_hit,
                "points": score["total_score"],
                "breakdown": score["breakdown"],
            }
        )

    n = len(rows)
    total_pts = sum(r["points"] for r in rows)
    mean_pts = total_pts / n
    winner_acc = sum(r["winner_hit"] for r in rows) / n
    pole_acc = sum(r["pole_hit"] for r in rows) / n
    fl_acc = sum(1 for r in rows if r["pred_fl"] == r["act_fl"]) / n
    mean_brier = sum(brier_win) / n
    baseline_acc = baseline_correct / n

    result = {
        "years": n,
        "mean_points": round(mean_pts, 2),
        "max_points": 55,  # pole(10) + podium(35) + FL(10)
        "winner_accuracy": round(winner_acc, 3),
        "pole_accuracy": round(pole_acc, 3),
        "fastest_lap_accuracy": round(fl_acc, 3),
        "brier_winner": round(mean_brier, 4),
        "baseline_leader_winner_accuracy": round(baseline_acc, 3),
        "rows": rows,
    }
    out = PROCESSED_DATA_DIR / "backtest_results.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


if __name__ == "__main__":
    r = run()
    print(f"Años evaluados: {r['years']}")
    print(f"Puntos medios: {r['mean_points']} / {r['max_points']}")
    print(
        f"Acierto ganador: {r['winner_accuracy'] * 100:.0f}%  |  baseline líder: {r['baseline_leader_winner_accuracy'] * 100:.0f}%"
    )
    print(
        f"Acierto pole: {r['pole_accuracy'] * 100:.0f}%  |  Acierto vuelta rápida: {r['fastest_lap_accuracy'] * 100:.0f}%"
    )
    print(f"Brier ganador: {r['brier_winner']}")
    for row in r["rows"]:
        print(
            f"  {row['year']}: win {row['pred_winner']}->{row['act_winner']} ({'OK' if row['winner_hit'] else 'x'}) | pole {row['pred_pole']}->{row['act_pole']} ({'OK' if row['pole_hit'] else 'x'}) | {row['points']} pts"
        )
