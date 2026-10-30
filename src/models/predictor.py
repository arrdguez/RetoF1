from typing import Dict, Any
from .monte_carlo_sim import MonteCarloRaceSimulator
from src.features.checo_analyzer import ChecoPerezAnalyzer
from src.features.safety_car_model import SafetyCarModel
from src.features.altitude_physics import AltitudePhysicsModel

class F1RacePredictor:
    """
    Main canonical prediction pipeline.
    Synthesizes Monte Carlo simulation, altitude physics, recent form,
    Checo Pérez empirical finish distribution, and Poisson Safety Car modeling.
    """

    def __init__(self, n_simulations: int = 2500, seed: int = 42):
        self.simulator = MonteCarloRaceSimulator(seed=seed)
        self.checo_analyzer = ChecoPerezAnalyzer()
        self.sc_model = SafetyCarModel(lambda_rate=0.75, adjust_for_turn1=True)
        self.altitude_model = AltitudePhysicsModel()
        self.n_simulations = n_simulations

    def generate_full_prediction(self) -> Dict[str, Any]:
        """
        Runs the canonical prediction pipeline and returns structured predictions
        with probabilities, rationales, and points breakdown.
        """
        sim_results = self.simulator.run_monte_carlo(self.n_simulations)
        checo_data = self.checo_analyzer.analyze_mc_results(sim_results["checo_finish_probabilities"])
        sc_data = self.sc_model.predict_safety_cars()
        altitude_data = self.altitude_model.get_altitude_impact_summary()

        # 1. Pole Position
        top_pole = next(iter(sim_results["pole_probabilities"].items()))
        pole_pred = {
            "driver": top_pole[0],
            "probability_pct": top_pole[1],
            "top_contenders": dict(list(sim_results["pole_probabilities"].items())[:3]),
            "challenge_points": 10,
            "methodology": "Simulación Monte Carlo calibrada con Pace de Q3 y Velocidad en Recta (2,240m)",
            "rationale": (
                f"{top_pole[0]} demostró el mejor ritmo en tandas de clasificación a una vuelta "
                f"minimizando el drag en la recta de 890m y maximizando tracción en el Sector 3."
            )
        }

        # 2. Official Podium (1st, 2nd, 3rd)
        top_podium_str = next(iter(sim_results["top_podium_combinations"].items()))
        podium_drivers = [d.strip() for d in top_podium_str[0].split("-")]
        podium_pred = {
            "p1_winner": podium_drivers[0],
            "p2_second": podium_drivers[1],
            "p3_third": podium_drivers[2],
            "exact_podium_sequence": podium_drivers,
            "combination_probability_pct": top_podium_str[1],
            "p1_prob_pct": sim_results["winner_probabilities"].get(podium_drivers[0], 0),
            "p2_prob_pct": sim_results["p2_probabilities"].get(podium_drivers[1], 0),
            "p3_prob_pct": sim_results["p3_probabilities"].get(podium_drivers[2], 0),
            "challenge_points": 35,  # 15 + 10 + 10
            "methodology": "Distribución Conjunta Monte Carlo P(P1 ∩ P2 ∩ P3) en 2,500 iteraciones",
            "rationale": (
                f"La gestión de neumáticos y el balance de refrigeración en altitud favorecen a {podium_drivers[0]} para la victoria, "
                f"con {podium_drivers[1]} y {podium_drivers[2]} completando el podio en aire limpio."
            )
        }

        # 3. Fastest Lap (Vuelta Rápida)
        top_fl = next(iter(sim_results["fastest_lap_probabilities"].items()))
        fl_pred = {
            "driver": top_fl[0],
            "probability_pct": top_fl[1],
            "top_contenders": dict(list(sim_results["fastest_lap_probabilities"].items())[:3]),
            "challenge_points": 10,
            "methodology": "Modelo Táctico de Ventana de Pits (>24s) en vueltas 65-68 con neumáticos Blandos",
            "rationale": (
                f"{top_fl[0]} proyecta la mayor probabilidad de abrir una brecha superior a 24 segundos "
                "para realizar una parada táctica libre y colocar neumáticos Blandos en las vueltas finales."
            )
        }

        # 4. Checo Pérez Position (Derivado 100% de la simulación MC)
        checo_pred = {
            "predicted_finish": checo_data["predicted_position"],
            "probability_pct": checo_data["probability_pct"],
            "alternatives": checo_data["top_candidates"],
            "dnf_risk_pct": checo_data["dnf_risk_pct"],
            "challenge_points": 15,
            "methodology": "Distribución empírica Monte Carlo con penalización por tráfico y riesgo Curva 1",
            "rationale": checo_data["rationale"]
        }

        # 5. Safety Cars (Derivado 100% de Poisson scipy.stats)
        sc_pred = {
            "predicted_count": sc_data["predicted_count"],
            "mode_probability_pct": sc_data["mode_probability_pct"],
            "distribution": sc_data["distribution"],
            "p_at_least_one_pct": sc_data["p_at_least_one_pct"],
            "lambda_effective": sc_data["lambda_effective"],
            "lambda_base": sc_data["lambda_base"],
            "challenge_points": 10,
            "methodology": f"Distribución Estocástica de Poisson (scipy.stats.poisson): {sc_data['formula']}",
            "rationale": sc_data["justification"]
        }

        return {
            "meta": {
                "challenge_name": "Desafío Tech: Estratega de F1 con GitHub Stack",
                "circuit": "Autódromo Hermanos Rodríguez (Mexico GP)",
                "elevation_m": 2240,
                "n_simulations": self.n_simulations,
                "pipeline": "Canonical Monte Carlo & Poisson Engine (Single Source of Truth)"
            },
            "altitude_physics": altitude_data,
            "quiniela_predictions": {
                "1_pole_position": pole_pred,
                "2_podio_oficial": podium_pred,
                "3_vuelta_rapida": fl_pred,
                "4_posicion_checo_perez": checo_pred,
                "5_safety_cars_fisicos": sc_pred
            },
            "total_potential_points": 80
        }
