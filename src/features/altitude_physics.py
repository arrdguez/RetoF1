import math
from typing import Dict, Any

class AltitudePhysicsModel:
    """
    Models the physical effects of high altitude (2,240 m ASL) at Autódromo Hermanos Rodríguez:
    - Air density reduction (~22% less than sea level).
    - Reduced aerodynamic drag (high top speeds on the 890m main straight).
    - Reduced aerodynamic downforce (cars run Monaco wings but generate Monza downforce).
    - Reduced mass airflow for radiator/turbo cooling and brake duct cooling.
    - Turbocharger strain (spinning near the 125,000 RPM regulation limit to compensate).
    """

    SEA_LEVEL_PRESSURE_HPA = 1013.25
    SEA_LEVEL_DENSITY_KG_M3 = 1.225
    MOLAR_MASS_AIR = 0.0289644  # kg/mol
    GAS_CONSTANT = 8.31432  # N·m/(mol·K)
    GRAVITY = 9.80665  # m/s^2

    def __init__(self, altitude_m: float = 2240.0, temp_c: float = 22.0):
        self.altitude_m = altitude_m
        self.temp_k = temp_c + 273.15
        self.density_ratio = self.calculate_density_ratio()

    def calculate_density_ratio(self) -> float:
        """
        Barometric formula calculation for air density ratio compared to sea level.
        """
        # Standard barometric temperature lapse: T = T0 - L * h
        lapse_rate = 0.0065  # K/m
        t0 = 288.15  # Sea level standard temp in K
        p_ratio = (1.0 - (lapse_rate * self.altitude_m) / t0) ** (
            (self.GRAVITY * self.MOLAR_MASS_AIR) / (self.GAS_CONSTANT * lapse_rate)
        )
        density_ratio = p_ratio * (t0 / self.temp_k)
        return round(density_ratio, 4)

    def get_altitude_impact_summary(self) -> Dict[str, Any]:
        drag_reduction_pct = round((1.0 - self.density_ratio) * 100, 1)
        downforce_reduction_pct = drag_reduction_pct
        cooling_efficiency_loss_pct = drag_reduction_pct

        return {
            "altitude_m": self.altitude_m,
            "density_ratio": self.density_ratio,
            "air_density_pct_of_sea_level": round(self.density_ratio * 100, 1),
            "drag_reduction_pct": drag_reduction_pct,
            "downforce_loss_pct": downforce_reduction_pct,
            "cooling_efficiency_loss_pct": cooling_efficiency_loss_pct,
            "turbo_stress_multiplier": 1.28,
            "brake_thermal_stress_multiplier": 1.35,
            "overtaking_impact": "Slipstream effect is weakened by thin air, but DRS delta remains strong due to top speed"
        }
