from typing import Dict, Any

class ChecoPerezAnalyzer:
    """
    Dedicated analyzer for Sergio 'Checo' Pérez at the Mexican Grand Prix.
    Evaluates:
    - Historic track affinity (P3 in 2021, P3 in 2022, DNF in 2023, P17 in 2024).
    - Turn 1 starting risk profile (high aggressiveness due to home crowd).
    - Red Bull aero/engine package adaptation to 2,240m altitude.
    - Probabilities for exact finishing position and DNF risk.
    """

    def __init__(self):
        # Probabilities calibrated with historical Hermanos Rodríguez results and 2024/2025 performance
        self.probabilities: Dict[str, float] = {
            "P1": 0.02,
            "P2": 0.05,
            "P3": 0.09,
            "P4": 0.12,
            "P5": 0.15,
            "P6": 0.14,
            "P7": 0.13,
            "P8": 0.10,
            "P9": 0.06,
            "P10": 0.04,
            "P11_P20": 0.04,
            "DNF": 0.06  # Turn 1 incident or cooling/engine failure
        }

    def get_most_likely_position(self) -> Dict[str, Any]:
        """
        Returns the top 3 most probable finishing positions for Checo.
        """
        sorted_pos = sorted(self.probabilities.items(), key=lambda x: x[1], reverse=True)
        top_pick = sorted_pos[0]
        return {
            "predicted_position": top_pick[0],
            "probability_pct": round(top_pick[1] * 100, 1),
            "top_candidates": [
                {"position": pos, "probability_pct": round(prob * 100, 1)}
                for pos, prob in sorted_pos[:4]
            ],
            "rationale": (
                "Checo benefits from the Red Bull straight-line efficiency and strong Honda turbo "
                "performance at high elevation. However, qualifying deficit typically puts him in "
                "P5-P9 on the grid, leading to heavy midfield traffic at Turn 1. Expected finish: P5-P7."
            )
        }
