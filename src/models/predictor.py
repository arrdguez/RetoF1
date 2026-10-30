"""
Punto de entrada canónico del predictor.

La clase `F1RacePredictor` es ahora un alias de `StatisticalF1Predictor`
(motor estadístico basado en datos reales: ratings 2026 + afinidad México +
Plackett-Luce + Monte Carlo + Poisson empírico + optimización de EV).

Se mantiene el nombre para no romper la CLI ni el exportador de DTO.
"""

from .statistical_engine import StatisticalF1Predictor

F1RacePredictor = StatisticalF1Predictor

__all__ = ["F1RacePredictor", "StatisticalF1Predictor"]
