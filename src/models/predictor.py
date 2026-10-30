from typing import Dict, Any
from .monte_carlo_sim import MonteCarloRaceSimulator
from src.features.checo_analyzer import ChecoPerezAnalyzer
from src.features.safety_car_model import SafetyCarModel
from src.features.altitude_physics import AltitudePhysicsModel

class F1RacePredictor:
    """
    Main prediction pipeline.
    Synthesizes Monte Carlo simulation, altitude physics, recent form,
    Checo Pérez telemetry profile, and Safety Car modeling to output
    the 5 targets required by the challenge.
    """

    def __init__(self, n_simulations: int = 2500, seed: int = 42):
        self.simulator = MonteCarloRaceSimulator(seed=seed)
        self.checo_analyzer = ChecoPerezAnalyzer()
        self.sc_model = SafetyCarModel()
        self.altitude_model = AltitudePhysicsModel()
        self.n_simulations = n_simulations

    def generate_full_prediction(self) -> Dict[str, Any]:
        """
        Runs the full prediction pipeline and returns structured predictions
        with probabilities, rationales, and points breakdown.
        """
        sim_results = self.simulator.run_monte_carlo(self.n_simulations)
        checo_data = self.checo_analyzer.get_most_likely_position()
        sc_data = self.sc_model.predict_safety_cars()
        altitude_data = self.altitude_model.get_altitude_impact_summary()

        # 1. Pole Position
        top_pole = next(iter(sim_results["pole_probabilities"].items()))
        pole_pred = {
            "driver": top_pole[0],
            "probability_pct": top_pole[1],
            "top_contenders": dict(list(sim_results["pole_probabilities"].items())[:3]),
            "challenge_points": 10,
            "rationale": (
                f"{top_pole[0]} demonstrates optimal single-lap pace and aerodynamic efficiency "
                f"in thin air conditions (2,240m altitude), minimizing drag on Sector 1 straight."
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
            "rationale": (
                f"Tire management and engine thermal balance favor {podium_drivers[0]} for the win, "
                f"with {podium_drivers[1]} and {podium_drivers[2]} holding strong race pace in clear air."
            )
        }

        # 3. Fastest Lap
        top_fl = next(iter(sim_results["fastest_lap_probabilities"].items()))
        fl_pred = {
            "driver": top_fl[0],
            "probability_pct": top_fl[1],
            "top_contenders": dict(list(sim_results["fastest_lap_probabilities"].items())[:3]),
            "challenge_points": 10,
            "rationale": (
                f"{top_fl[0]} is projected to possess free pit window gap in the final laps to pit "
                "for new softs and claim the extra bonus point."
            )
        }

        # 4. Checo Pérez Position
        checo_pred = {
            "predicted_finish": checo_data["predicted_position"],
            "probability_pct": checo_data["probability_pct"],
            "alternatives": checo_data["top_candidates"],
            "challenge_points": 15,
            "rationale": checo_data["rationale"]
        }

        # 5. Safety Cars (Physical)
        sc_pred = {
            "predicted_count": sc_data["predicted_count"],
            "probability_pct": sc_data["probability_pct"],
            "distribution": sc_data["distribution"],
            "challenge_points": 10,
            "rationale": sc_data["rationale"]
        }

        return {
            "meta": {
                "challenge_name": "Desafío Tech: Estratega de F1 con GitHub Stack",
                "circuit": "Autódromo Hermanos Rodríguez (Mexico GP)",
                "elevation_m": 2240,
                "n_simulations": self.n_simulations
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
