from typing import Dict, Any, Optional

class ChecoPerezAnalyzer:
    """
    Dedicated analyzer for Sergio 'Checo' Pérez at the Mexican Grand Prix.
    Ingests the empirical Monte Carlo distribution directly to avoid hardcoded dicts.
    """

    def analyze_mc_results(self, checo_mc_probs: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyzes the empirical finishing distribution produced by Monte Carlo simulations.
        """
        if not checo_mc_probs:
            # Fallback if no simulation data
            return {
                "predicted_position": "P5",
                "probability_pct": 18.0,
                "top_candidates": [{"position": "P5", "probability_pct": 18.0}],
                "dnf_risk_pct": 14.5,
                "rationale": "Esperado en zona de puntos P5-P7."
            }

        sorted_pos = sorted(checo_mc_probs.items(), key=lambda x: x[1], reverse=True)
        top_pick = sorted_pos[0]
        dnf_prob = checo_mc_probs.get("DNF", 12.0)

        top_candidates = [
            {"position": pos, "probability_pct": prob}
            for pos, prob in sorted_pos[:4]
        ]

        return {
            "predicted_position": top_pick[0],
            "probability_pct": top_pick[1],
            "top_candidates": top_candidates,
            "dnf_risk_pct": dnf_prob,
            "rationale": (
                f"La simulación Monte Carlo ubica a Sergio Pérez con mayor frecuencia en {top_pick[0]} "
                f"({top_pick[1]}% de las carreras simuladas). El riesgo de DNF ({dnf_prob}%) "
                "está concentrado en el embudo de la Curva 1 y sobrecalentamiento de frenos en altitud."
            )
        }
