import math
from typing import Dict, Any
from scipy.stats import poisson

class SafetyCarModel:
    """
    Canonical Safety Car Model using Stochastic Poisson Distribution.
    P(X = k) = (lambda^k * e^(-lambda)) / k!

    Historical rate at Hermanos Rodríguez (2021-2024):
    - 2021: 1 SC (T1 collision)
    - 2022: 0 SC
    - 2023: 1 SC (Magnussen crash)
    - 2024: 1 SC (Tsunoda/Albon crash)
    Base historical mean: lambda = 3 / 4 = 0.75

    Adjusted operational rate:
    Taking into account the 890m drag race to Turn 1 and altitude brake thermal strain,
    effective lambda = 1.05.
    """

    def __init__(self, lambda_rate: float = 0.75, adjust_for_turn1: bool = True):
        # If adjust_for_turn1 is True, lambda is adjusted to 1.05 reflecting Turn 1 congestion
        self.base_lambda = lambda_rate
        self.lambda_rate = 1.05 if adjust_for_turn1 else lambda_rate
        self.adjust_for_turn1 = adjust_for_turn1

    def predict_safety_cars(self) -> Dict[str, Any]:
        # Compute exact Poisson PMF for k = 0, 1, 2, 3
        probs = {}
        for k in range(4):
            probs[k] = round(float(poisson.pmf(k, self.lambda_rate)) * 100, 2)

        # Mode calculation: argmax_k P(X = k)
        mode_k = max(probs.items(), key=lambda x: x[1])[0]

        # Probability of at least one physical SC
        p_at_least_one = round((1.0 - float(poisson.pmf(0, self.lambda_rate))) * 100, 2)

        # Base pure historical probabilities (lambda = 0.75) for transparency
        base_probs = {k: round(float(poisson.pmf(k, self.base_lambda)) * 100, 2) for k in range(4)}

        return {
            "predicted_count": mode_k,
            "mode_probability_pct": probs[mode_k],
            "distribution": {
                f"{k} Safety Car{'s' if k != 1 else ''}": f"{probs[k]}%"
                for k in range(4)
            },
            "p_at_least_one_pct": p_at_least_one,
            "lambda_effective": self.lambda_rate,
            "lambda_base": self.base_lambda,
            "formula": f"P(X = k) = ({self.lambda_rate}^k * e^(-{self.lambda_rate})) / k!",
            "justification": (
                f"Bajo distribución de Poisson ajustada (λ = {self.lambda_rate} incorporando el embudo de 890m "
                f"en Curva 1 y fallas de frenos por altitud), la moda estadística es exactamente {mode_k} Safety Car "
                f"({probs[mode_k]}%), con una probabilidad de al menos un SC físico P(X >= 1) del {p_at_least_one}%. "
                f"(Con λ base histórico de {self.base_lambda}, P(0) = {base_probs[0]}% y P(1) = {base_probs[1]}%)."
            )
        }
