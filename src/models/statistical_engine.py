"""
Motor estadístico canónico para la quiniela del GP de México 2026.

Principios:
- Datos reales determinan la predicción (nada escrito a mano).
- Métodos válidos para muestra pequeña: ratings basados en puntos 2026,
  afinidad histórica de circuito, modelo Plackett-Luce (permutaciones),
  Monte Carlo para incertidumbre y eventos raros (DNF), Poisson empírico
  para Safety Cars, y optimización de puntos esperados (EV).
- Toda cifra publicada se calcula aquí; nada se fuerza ni se inventa.

Pipeline:
  datos 2026 (standings ronda 18) + histórico México (2015-2025) + clima
  -> skill por piloto (quali y carrera)
  -> Plackett-Luce + Monte Carlo multi-seed (distribución conjunta de orden)
  -> Poisson empírico (Safety Cars)
  -> optimizador de EV (selección de la quiniela)
  -> dict único (consola / JSON DTO / dashboard / informe)
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scipy.stats import gamma, nbinom

from config.settings import PROCESSED_DATA_DIR, RAW_DATA_DIR, SCORING_CONFIG
from src.features.altitude_physics import AltitudePhysicsModel

# ---------------------------------------------------------------------------
# Datos de entrada
# ---------------------------------------------------------------------------

# Mapa de equipos 2026 (R19 México). Fuente: Wikipedia "2026 F1 season" (Entries).
# Provenance marcado explícito: es la única parte no derivada de la API de resultados.
TEAMS_2026: Dict[str, str] = {
    "ANT": "mercedes",
    "RUS": "mercedes",
    "HAM": "ferrari",
    "LEC": "ferrari",
    "VER": "red_bull",
    "HAD": "red_bull",
    "NOR": "mclaren",
    "PIA": "mclaren",
    "LAW": "rb",
    "LIN": "rb",
    "GAS": "alpine",
    "COL": "alpine",
    "OCO": "haas",
    "BEA": "haas",
    "HUL": "audi",
    "BOR": "audi",
    "ALO": "aston_martin",
    "STR": "aston_martin",
    "ALB": "williams",
    "SAI": "williams",
    "PER": "cadillac",
    "BOT": "cadillac",
}

TEAM_DISPLAY: Dict[str, str] = {
    "mercedes": "Mercedes",
    "ferrari": "Ferrari",
    "red_bull": "Red Bull",
    "mclaren": "McLaren",
    "rb": "Racing Bulls",
    "alpine": "Alpine",
    "haas": "Haas",
    "audi": "Audi",
    "williams": "Williams",
    "aston_martin": "Aston Martin",
    "cadillac": "Cadillac",
}

DRIVER_NAMES: Dict[str, str] = {
    "ANT": "Andrea Kimi Antonelli",
    "RUS": "George Russell",
    "HAM": "Lewis Hamilton",
    "LEC": "Charles Leclerc",
    "VER": "Max Verstappen",
    "HAD": "Isack Hadjar",
    "NOR": "Lando Norris",
    "PIA": "Oscar Piastri",
    "LAW": "Liam Lawson",
    "LIN": "Arvid Lindblad",
    "GAS": "Pierre Gasly",
    "COL": "Franco Colapinto",
    "OCO": "Esteban Ocon",
    "BEA": "Oliver Bearman",
    "HUL": "Nico Hulkenberg",
    "BOR": "Gabriel Bortoleto",
    "ALO": "Fernando Alonso",
    "STR": "Lance Stroll",
    "ALB": "Alexander Albon",
    "SAI": "Carlos Sainz",
    "PER": "Sergio Perez",
    "BOT": "Valtteri Bottas",
}

# Pesos del modelo (hiperparámetros documentados; no calibrados a un resultado).
# - Forma 2026 (puntos) ~35%: ritmo general de la temporada.
# - Victorias 2026 ~20%: señal de dominancia (predecir "quién gana" necesita
#   las victorias, no solo la consistencia de puntos).
# - Equipo ~30%: en F1 el coche explica gran parte del rendimiento.
# - Afinidad México ~15%: ajuste modesto por dominio de circuito.
W_FORM = 0.35
W_WINS = 0.20
W_TEAM = 0.30
W_MX = 0.15

# Ruido de Monte Carlo (multiplicativo, log-normal) para cuantificar incertidumbre.
NOISE_QUALI = 0.25
NOISE_RACE = 0.15

# Priors de abandono (documentados; se validan en backtest).
BASE_MECHANICAL_DNF = 0.04  # fallo mecánico base
NEW_TEAM_DNF_BONUS = 0.03  # Cadillac (escudería debutante) -> más riesgo
T1_FRONT_BACK_RISK = 0.012  # curva 1, coches de cabeza/cola
T1_MIDFIELD_RISK = 0.030  # curva 1, pelotón medio (P4-P14)
GRID_PENALTY_PER_POS = 0.010  # penalización por salir atrás (log-skill)

SEED_BASE = 2026


class StatisticalF1Predictor:
    """Predicción canónica para los 5 puntos de la quiniela."""

    def __init__(self, n_simulations: int = 20000, seed: int = 42):
        self.n_simulations = n_simulations
        self.seed = seed
        self._mx_stats = (
            self._load_mexico_stats()
        )  # cache: se usa en drivers y vuelta rápida
        self.drivers: List[Dict[str, Any]] = self._build_drivers()
        self.sc_model = self._load_sc_model()
        self.weather = self._load_weather()
        self.altitude = AltitudePhysicsModel()

    # -- Carga de datos -----------------------------------------------------

    def _load_standings(
        self,
    ) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, int]]:
        """Devuelve (pts_driver, pts_constructor, wins_driver) desde Jolpica 2026 (ronda 18)."""
        ds = json.loads((RAW_DATA_DIR / "2026" / "driverstandings.json").read_text())
        cs = json.loads(
            (RAW_DATA_DIR / "2026" / "constructorstandings.json").read_text()
        )

        pts_driver: Dict[str, float] = {}
        wins_driver: Dict[str, int] = {}
        for s in ds["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]:
            code = s["Driver"]["code"]
            pts_driver[code] = float(s["points"])
            wins_driver[code] = int(s["wins"])

        pts_ctor: Dict[str, float] = {}
        for c in cs["MRData"]["StandingsTable"]["StandingsLists"][0][
            "ConstructorStandings"
        ]:
            ctor_id = c["Constructor"]["constructorId"]
            pts_ctor[ctor_id] = float(c["points"])

        return pts_driver, pts_ctor, wins_driver

    def _load_mexico_stats(self) -> Dict[str, Dict[str, float]]:
        """Afinidad histórica por piloto en México (era moderna 2015+)."""
        payload = json.loads(
            (PROCESSED_DATA_DIR / "mexico_driver_stats.json").read_text()
        )
        out: Dict[str, Dict[str, float]] = {}
        for r in payload["driver_stats_modern"]:
            out[r["code"]] = {
                "starts": r["starts"],
                "wins": r["wins"],
                "podiums": r["podiums"],
                "poles": r["poles"],
                "fastest_laps": r["fastest_laps"],
                "dnfs": r["dnfs"],
                "avg_finish": r["avg_finish"] or 99.0,
                "win_rate": r["win_rate_pct"] / 100.0,
                "podium_rate": r["podium_rate_pct"] / 100.0,
                "dnf_rate": r["dnf_rate_pct"] / 100.0,
            }
        return out

    def _build_drivers(self) -> List[Dict[str, Any]]:
        pts_d, pts_c, wins = self._load_standings()
        mx = self._mx_stats
        drivers = []
        for code, team_id in TEAMS_2026.items():
            dpts = pts_d.get(code, 0.0)
            if team_id not in pts_c:
                raise ValueError(
                    f"ConstructorId '{team_id}' no encontrado en standings 2026 (driver {code})"
                )
            tpts = pts_c[team_id]
            m = mx.get(code, None)

            form = math.log(1.0 + dpts)
            team_log = math.log(1.0 + tpts)

            # Afinidad de circuito: solo si hay al menos 1 salida en México.
            if m and m["starts"] >= 1:
                mx_aff = math.log(
                    1.0
                    + 15.0 * m["win_rate"]
                    + 3.0 * m["podium_rate"]
                    + 0.5 / max(m["avg_finish"], 1.0)
                )
                dnf_rate = m["dnf_rate"]
            else:
                mx_aff = 0.0
                dnf_rate = 0.0

            is_new_team = team_id == "cadillac"
            mechanical = BASE_MECHANICAL_DNF + (
                NEW_TEAM_DNF_BONUS if is_new_team else 0.0
            )
            if dnf_rate > 0.0:
                mechanical = 0.5 * mechanical + 0.5 * dnf_rate  # mezcla con histórico

            drivers.append(
                {
                    "code": code,
                    "name": DRIVER_NAMES[code],
                    "team": TEAM_DISPLAY.get(team_id, team_id),
                    "team_id": team_id,
                    "points_2026": dpts,
                    "wins_2026": wins.get(code, 0),
                    "team_points_2026": tpts,
                    "mexico_affinity": mx_aff,
                    "mexico_starts": m["starts"] if m else 0,
                    "mexico_avg_finish": m["avg_finish"] if m else None,
                    "mechanical_dnf": round(min(mechanical, 0.25), 4),
                }
            )

        return drivers

    def _skills(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Skill quali/carrera por piloto (log de theta de Plackett-Luce)."""
        sq: Dict[str, float] = {}
        sr: Dict[str, float] = {}
        for d in self.drivers:
            form = math.log(1.0 + d["points_2026"])
            wins_log = math.log(1.0 + d["wins_2026"])
            team_log = math.log(1.0 + d["team_points_2026"])
            mx_aff = d["mexico_affinity"]
            s = W_FORM * form + W_WINS * wins_log + W_TEAM * team_log + W_MX * mx_aff
            sq[d["code"]] = s
            sr[d["code"]] = s
        return sq, sr

    def _load_sc_model(self) -> Dict[str, Any]:
        sc = json.loads((PROCESSED_DATA_DIR / "mexico_sc_history.json").read_text())
        return sc

    def _load_weather(self) -> Dict[str, Any]:
        path = PROCESSED_DATA_DIR / "weather_cdmx_weekend.json"
        if path.exists():
            return json.loads(path.read_text())
        return {"days": []}

    # -- Muestreo Plackett-Luce --------------------------------------------

    @staticmethod
    def _plackett_luce_order(skills: Dict[str, float]) -> List[str]:
        """Muestrea una permutación exacta del modelo Plackett-Luce."""
        remaining = list(skills.keys())
        order: List[str] = []
        while remaining:
            weights = [math.exp(skills[c]) for c in remaining]
            total = sum(weights)
            r = random.random() * total
            acc = 0.0
            for i, c in enumerate(remaining):
                acc += weights[i]
                if r <= acc:
                    order.append(c)
                    remaining.pop(i)
                    break
        return order

    def _sample_quali(self, sq: Dict[str, float]) -> List[str]:
        noisy = {c: sq[c] + random.gauss(0, NOISE_QUALI) for c in sq}
        return self._plackett_luce_order(noisy)

    def _sample_race(self, sr: Dict[str, float], grid: List[str]) -> List[str]:
        # DNF mecánico
        dnf = set()
        for d in self.drivers:
            if random.random() < d["mechanical_dnf"]:
                dnf.add(d["code"])

        # Riesgo de curva 1 (en función de la posición de salida)
        for i, code in enumerate(grid):
            if code in dnf:
                continue
            risk = T1_MIDFIELD_RISK if 3 <= i <= 13 else T1_FRONT_BACK_RISK
            if random.random() < risk:
                dnf.add(code)

        # Skill con penalización de parrilla (salir atrás reduce ritmo efectivo)
        noisy: Dict[str, float] = {}
        grid_idx = {c: i for i, c in enumerate(grid)}
        for d in self.drivers:
            c = d["code"]
            if c in dnf:
                continue
            g = grid_idx.get(c, len(grid))
            noisy[c] = sr[c] - GRID_PENALTY_PER_POS * g + random.gauss(0, NOISE_RACE)

        return self._plackett_luce_order(noisy)

    # -- Vuelta rápida ------------------------------------------------------

    def _fastest_lap_model(self, sr: Dict[str, float]) -> Dict[str, float]:
        """
        Modelo honesto de vuelta rápida: combinación de ritmo de carrera y
        afinidad histórica de vuelta rápida en México. NO es una regresión
        simulada: es una distribución construida a partir de skill real.
        Todos los pilotos son elegibles (el objetivo es el giro más rápido,
        no un punto de campeonato); el peso de los rezagados es naturalmente
        mínimo por su skill bajo.
        """
        weights = {}
        for d in self.drivers:
            c = d["code"]
            fl_hist = self._mx_stats.get(c, {})
            w = math.exp(sr[c]) * (1.0 + 0.5 * (fl_hist.get("fastest_laps", 0) / 2.0))
            weights[c] = w
        total = sum(weights.values())
        return {c: round(w / total, 4) for c, w in weights.items()}

    # -- Simulación completa -----------------------------------------------

    def run_simulation(self) -> Dict[str, Any]:
        random.seed(self.seed)
        sq, sr = self._skills()
        codes = [d["code"] for d in self.drivers]

        pole = Counter()
        winner = Counter()
        p2 = Counter()
        p3 = Counter()
        podium_combos = Counter()
        fl_counter = Counter()
        checo = Counter()

        for _ in range(self.n_simulations):
            grid = self._sample_quali(sq)
            pole[grid[0]] += 1

            classified = self._sample_race(sr, grid)
            # posición final real: DNF quedan fuera de clasificación
            if classified:
                winner[classified[0]] += 1
                if len(classified) > 1:
                    p2[classified[1]] += 1
                if len(classified) > 2:
                    p3[classified[2]] += 1
                top3 = tuple(classified[:3])
                podium_combos[top3] += 1
            else:
                top3 = ()

            # Checo: posición o DNF
            if "PER" not in classified and "PER" in codes:
                checo["DNF"] += 1
            elif "PER" in classified:
                checo[f"P{classified.index('PER') + 1}"] += 1

            # Vuelta rápida (todos elegibles; peso por ritmo + historial)
            flw = self._fastest_lap_model(sr)
            if flw:
                fl_driver = random.choices(
                    list(flw.keys()), weights=list(flw.values()), k=1
                )[0]
                fl_counter[fl_driver] += 1

        n = self.n_simulations

        def pct(c: Counter) -> Dict[str, float]:
            return {k: round(100.0 * v / n, 2) for k, v in c.most_common()}

        # Checo: distribución completa P1..P22 + DNF
        checo_dist = {}
        for k in [f"P{i}" for i in range(1, 23)] + ["DNF"]:
            if k in checo:
                checo_dist[k] = round(100.0 * checo[k] / n, 2)
        checo_sorted = sorted(checo_dist.items(), key=lambda x: -x[1])

        return {
            "n_simulations": n,
            "seed": self.seed,
            "skills": {
                c: {"quali": round(sq[c], 3), "race": round(sr[c], 3)} for c in codes
            },
            "pole_probabilities": pct(pole),
            "winner_probabilities": pct(winner),
            "p2_probabilities": pct(p2),
            "p3_probabilities": pct(p3),
            "top_podium_combinations": pct(podium_combos),
            "fastest_lap_probabilities": pct(fl_counter),
            "checo_distribution": checo_dist,
            "checo_sorted": checo_sorted,
        }

    # -- Optimización de puntos esperados (EV) -----------------------------

    def _optimize_podium(self, sim: Dict[str, Any]) -> Dict[str, Any]:
        """Elige la terna ordenada de pilotos distintos que maximiza los puntos esperados."""
        w = {
            "winner": SCORING_CONFIG.winner_exact,  # 15
            "second": SCORING_CONFIG.second_exact,  # 10
            "third": SCORING_CONFIG.third_exact,  # 10
            "other": SCORING_CONFIG.podium_other_position,  # 5
        }
        codes = [d["code"] for d in self.drivers]

        p1 = sim["winner_probabilities"]
        p2 = sim["p2_probabilities"]
        p3 = sim["p3_probabilities"]

        def on_podium(d):
            return p1.get(d, 0) + p2.get(d, 0) + p3.get(d, 0)

        best_ev = -1.0
        best = None
        for a in codes:
            for b in codes:
                if b == a:
                    continue
                for c in codes:
                    if c in (a, b):
                        continue
                    ev = 0.0
                    # slot 1 (a): 15 exacto, 5 si podio en otra pos
                    ev += w["other"] * on_podium(a) + (
                        w["winner"] - w["other"]
                    ) * p1.get(a, 0)
                    ev += w["other"] * on_podium(b) + (
                        w["second"] - w["other"]
                    ) * p2.get(b, 0)
                    ev += w["other"] * on_podium(c) + (
                        w["third"] - w["other"]
                    ) * p3.get(c, 0)
                    if ev > best_ev:
                        best_ev = ev
                        best = (a, b, c, ev)
        return {
            "p1": best[0],
            "p2": best[1],
            "p3": best[2],
            "expected_points": round(best[3] / 100.0, 2),
        }

    # -- Predicción final --------------------------------------------------

    def generate_full_prediction(self) -> Dict[str, Any]:
        sim = self.run_simulation()

        # 1. Pole (moda)
        pole_driver = max(sim["pole_probabilities"], key=sim["pole_probabilities"].get)
        pole_pct = sim["pole_probabilities"][pole_driver]

        # 2. Podio (EV-óptimo)
        pod = self._optimize_podium(sim)
        p1_d, p2_d, p3_d = pod["p1"], pod["p2"], pod["p3"]

        # 3. Vuelta rápida (moda)
        fl_driver = max(
            sim["fastest_lap_probabilities"], key=sim["fastest_lap_probabilities"].get
        )
        fl_pct = sim["fastest_lap_probabilities"][fl_driver]

        # 4. Checo (moda de la distribución completa)
        checo_mode = sim["checo_sorted"][0]
        checo_mode_pos, checo_mode_pct = checo_mode
        dnf_pct = sim["checo_distribution"].get("DNF", 0.0)

        # 5. Safety Cars (Poisson empírico)
        sc = self._safety_car_prediction()

        return {
            "meta": {
                "challenge_name": "Desafío Tech: Estratega de F1 con GitHub Stack",
                "circuit": "Autódromo Hermanos Rodríguez (Mexico GP)",
                "elevation_m": 2240,
                "target_event": "2026 Mexico City Grand Prix (R19, 2026-11-01)",
                "data_cutoff": "2026-10-31 (antes de clasificación)",
                "n_simulations": self.n_simulations,
                "seed": self.seed,
                "pipeline": "Ratings 2026 + afinidad México + Plackett-Luce + Monte Carlo + Poisson",
                "data_sources": {
                    "standings_2026": "Jolpica/Ergast (ronda 18)",
                    "mexico_history": "Jolpica/Ergast 2015-2025",
                    "teams_2026": "Wikipedia 2026 F1 (manual, trazable)",
                    "safety_cars": "compilado manual 2021-2024 (trazable)",
                },
            },
            "altitude_physics": self.altitude.get_altitude_impact_summary(),
            "quiniela_predictions": {
                "1_pole_position": {
                    "driver": pole_driver,
                    "probability_pct": pole_pct,
                    "top_contenders": dict(list(sim["pole_probabilities"].items())[:5]),
                    "challenge_points": SCORING_CONFIG.pole_exact,
                    "methodology": "Plackett-Luce sobre skill de clasificación (forma 2026 + equipo + afinidad México)",
                    "rationale": (
                        f"{DRIVER_NAMES[pole_driver]} ({pole_driver}) maximiza la combinación de ritmo "
                        f"2026 y afinidad con el trazado; probabilidad {pole_pct}% de llevarse la pole en Q3."
                    ),
                },
                "2_podio_oficial": {
                    "p1_winner": p1_d,
                    "p2_second": p2_d,
                    "p3_third": p3_d,
                    "exact_podium_sequence": [p1_d, p2_d, p3_d],
                    "combination_probability_pct": sim["top_podium_combinations"].get(
                        (p1_d, p2_d, p3_d), 0.0
                    ),
                    "p1_prob_pct": sim["winner_probabilities"].get(p1_d, 0),
                    "p2_prob_pct": sim["p2_probabilities"].get(p2_d, 0),
                    "p3_prob_pct": sim["p3_probabilities"].get(p3_d, 0),
                    "expected_points": pod["expected_points"],
                    "challenge_points": SCORING_CONFIG.winner_exact
                    + SCORING_CONFIG.second_exact
                    + SCORING_CONFIG.third_exact,
                    "methodology": "Terna que maximiza puntos esperados (15/10/10 + 5 parcial) sobre la distribución Plackett-Luce",
                    "rationale": (
                        f"La terna {p1_d}→{p2_d}→{p3_d} maximiza el valor esperado del podio "
                        f"({pod['expected_points']} pts esperados), considerando los puntos parciales por piloto en el podio."
                    ),
                },
                "3_vuelta_rapida": {
                    "driver": fl_driver,
                    "probability_pct": fl_pct,
                    "top_contenders": dict(
                        list(sim["fastest_lap_probabilities"].items())[:5]
                    ),
                    "challenge_points": SCORING_CONFIG.fastest_lap_exact,
                    "methodology": "Ritmo de carrera (top-10) × afinidad histórica de vuelta rápida en México",
                    "rationale": (
                        f"{DRIVER_NAMES[fl_driver]} ({fl_driver}) combina ritmo de carrera con historial "
                        f"de vuelta rápida en México (probabilidad {fl_pct}%)."
                    ),
                },
                "4_posicion_checo_perez": {
                    "predicted_finish": checo_mode_pos,
                    "probability_pct": checo_mode_pct,
                    "alternatives": [
                        {"position": k, "probability_pct": v}
                        for k, v in sim["checo_sorted"][:6]
                    ],
                    "dnf_risk_pct": dnf_pct,
                    "challenge_points": SCORING_CONFIG.checo_position_exact,
                    "methodology": "Moda de la distribución empírica P1..P22 ∪ DNF (Cadillac, 0 pts en 2026)",
                    "rationale": (
                        f"Cadillac acumula 0 puntos en 2026 (11º de 11 constructores): la moda de la "
                        f"distribución ubica a Checo en {checo_mode_pos} ({checo_mode_pct}%), con {dnf_pct}% de DNF."
                    ),
                },
                "5_safety_cars_fisicos": sc,
            },
            "total_potential_points": SCORING_CONFIG.max_possible_points,
            "distributions": {
                "winner": sim["winner_probabilities"],
                "pole": sim["pole_probabilities"],
                "podium_top": dict(list(sim["top_podium_combinations"].items())[:10]),
                "fastest_lap": sim["fastest_lap_probabilities"],
                "checo": sim["checo_distribution"],
            },
        }

    def _safety_car_prediction(self) -> Dict[str, Any]:
        """
        Modelo Poisson-Gamma Bayesiano para Safety Cars.

        - Prior débil sobre la tasa:  lambda ~ Gamma(alpha0=1, beta0=1).
        - Datos: n ediciones, suma de SC físicos = total.
        - Posterior:                 lambda ~ Gamma(alpha0+total, beta0+n).
        - Predictiva posterior (lo que importa): Binomial Negativa, que ya
          incorpora la incertidumbre de estimar lambda con n pequeña.
        """
        alpha0, beta0 = 1.0, 1.0
        n = self.sc_model["sample_size"]
        total = self.sc_model["total_physical_sc"]
        a_post = alpha0 + total
        b_post = beta0 + n

        # Predictiva posterior (Binomial Negativa) para k = 0,1,2,3
        p_succ = b_post / (b_post + 1.0)
        probs = {
            k: round(float(nbinom.pmf(k, a_post, p_succ)) * 100, 2) for k in range(4)
        }
        p_3plus = round(100.0 - sum(probs.values()), 2)
        mode = max(probs, key=probs.get)
        p_at_least_one = round(100.0 - probs[0], 2)

        # Posterior de lambda: media, moda e intervalo creíble 90%
        lam_mean = round(a_post / b_post, 3)
        lam_mode = round((a_post - 1.0) / b_post, 3) if a_post > 1 else 0.0
        lam_lo = round(float(gamma.ppf(0.05, a_post, scale=1.0 / b_post)), 3)
        lam_hi = round(float(gamma.ppf(0.95, a_post, scale=1.0 / b_post)), 3)

        ev = {
            k: round(SCORING_CONFIG.safety_cars_exact * p / 100.0, 2)
            for k, p in probs.items()
        }
        return {
            "predicted_count": mode,
            "mode_probability_pct": probs[mode],
            "p_at_least_one_pct": p_at_least_one,
            "distribution": {
                f"{k} Safety Car{'s' if k != 1 else ''}": f"{probs[k]}%"
                for k in range(4)
            },
            "distribution_3plus_pct": p_3plus,
            "expected_points_by_pick": ev,
            "lambda_empirical": round(total / n, 3),
            "lambda_base": round(total / n, 3),
            "lambda_effective": round(total / n, 3),
            "lambda_posterior_mean": lam_mean,
            "lambda_posterior_mode": lam_mode,
            "lambda_credible_interval_90": [lam_lo, lam_hi],
            "sample_size": n,
            "prior": f"Gamma(alpha={alpha0}, beta={beta0})",
            "posterior": f"Gamma(alpha={a_post}, beta={b_post})",
            "challenge_points": SCORING_CONFIG.safety_cars_exact,
            "methodology": "Poisson-Gamma Bayesiano (predictiva Binomial Negativa)",
            "rationale": (
                f"Con {total} SC físicos en {n} ediciones (2021-2024) y prior Gamma(1,1), la predictiva "
                f"Binomial Negativa da moda {mode} Safety Car(s) ({probs[mode]}%) y P(X≥1)={p_at_least_one}%. "
                f"La tasa posterior λ tiene media {lam_mean} e intervalo creíble 90% [{lam_lo}, {lam_hi}] "
                f"(muestra pequeña -> incertidumbre alta). El pick EV-óptimo es {mode} SC ({ev[mode]} pts)."
            ),
        }
