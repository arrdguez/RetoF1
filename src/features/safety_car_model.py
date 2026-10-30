from typing import Dict, Any

class SafetyCarModel:
    """
    Models physical Safety Car (no VSC) probabilities for the Mexican Grand Prix.
    Factors:
    - 890m run to Turn 1 causing recurrent multi-car first-lap pileups.
    - Stadium section (Foro Sol) tight confines with limited run-off.
    - Altitude causing brake overheating and component failures.
    - Historical frequency: Physical SC deployed in ~75% of modern Mexico GP editions.
    """

    def __init__(self):
        # Calibrated distribution for physical Safety Cars count (0, 1, 2, 3+)
        self.probabilities: Dict[int, float] = {
            0: 0.22,
            1: 0.54,
            2: 0.19,
            3: 0.05
        }

    def predict_safety_cars(self) -> Dict[str, Any]:
        sorted_sc = sorted(self.probabilities.items(), key=lambda x: x[1], reverse=True)
        top_sc = sorted_sc[0]
        return {
            "predicted_count": top_sc[0],
            "probability_pct": round(top_sc[1] * 100, 1),
            "distribution": {
                f"{k} Safety Car{'s' if k != 1 else ''}": f"{round(v * 100, 1)}%"
                for k, v in self.probabilities.items()
            },
            "rationale": (
                "Historically, 1 physical Safety Car is the mode (54% probability), primarily triggered "
                "by lap 1 Turn 1 collisions or mid-race brake failures caused by thermal overheating "
                "in thin Mexico City air."
            )
        }
