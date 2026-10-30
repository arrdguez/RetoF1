#!/usr/bin/env python3
"""
f1_hybrid_predictor.py
Canonical Hybrid F1 Strategy & Prediction Pipeline for Mexico GP (2,240m ASL).

Unifies:
1. Monte Carlo Race Simulator (2,500+ iterations with dynamic recent form) -> Pole, Podium, Checo Pérez
2. Stochastic Poisson Model (scipy.stats.poisson) -> Safety Cars Físicos (Punto #5)
3. Tactical Pit-Window & Degradation Model -> Vuelta Rápida (Punto #3)

Exports:
- Console report with mathematical justifications and probability percentages
- StrategyPredictionDTO JSON for corporate ASO / APX architectures
"""

import json
from pathlib import Path
from typing import Dict, Any

from config.settings import BASE_DIR
from src.models.predictor import F1RacePredictor

REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_and_export_dto(pred_data: Dict[str, Any]) -> Dict[str, Any]:
    q = pred_data["quiniela_predictions"]
    pole = q["1_pole_position"]
    podium = q["2_podio_oficial"]
    fl = q["3_vuelta_rapida"]
    checo = q["4_posicion_checo_perez"]
    sc = q["5_safety_cars_fisicos"]

    dto = {
        "header": {
            "serviceName": "F1_Strategy_Prediction_Service",
            "apiVersion": "1.0.0",
            "architectureStack": "ASO_APX_Compatible_DTO",
            "circuit": "Autodromo Hermanos Rodriguez",
            "elevationMeters": 2240,
            "airDensityRatio": pred_data["altitude_physics"]["density_ratio"],
            "pipelineType": "Canonical_Monte_Carlo_And_Poisson_Unified",
        },
        "strategyPredictionDTO": {
            "point_1_polePosition": {
                "predictedDriver": pole["driver"],
                "confidencePct": pole["probability_pct"],
                "topContenders": pole["top_contenders"],
                "methodology": pole["methodology"],
                "awardedPoints": pole["challenge_points"],
            },
            "point_2_officialPodium": {
                "p1_winner": podium["p1_winner"],
                "p2_second": podium["p2_second"],
                "p3_third": podium["p3_third"],
                "exactSequence": podium["exact_podium_sequence"],
                "jointProbabilityPct": podium["combination_probability_pct"],
                "methodology": podium["methodology"],
                "awardedPoints": podium["challenge_points"],
            },
            "point_3_fastestLap": {
                "predictedDriver": fl["driver"],
                "confidencePct": fl["probability_pct"],
                "methodology": fl["methodology"],
                "awardedPoints": fl["challenge_points"],
            },
            "point_4_checoPerezPosition": {
                "predictedPosition": checo["predicted_finish"],
                "probabilityPct": checo["probability_pct"],
                "alternatives": checo["alternatives"],
                "dnfRiskPct": checo["dnf_risk_pct"],
                "methodology": checo["methodology"],
                "awardedPoints": checo["challenge_points"],
            },
            "point_5_safetyCarsPhysical": {
                "predictedCount": sc["predicted_count"],
                "modeProbabilityPct": sc["mode_probability_pct"],
                "pAtLeastOnePct": sc["p_at_least_one_pct"],
                "distribution": sc["distribution"],
                "lambdaEffective": sc["lambda_effective"],
                "lambdaBase": sc["lambda_base"],
                "methodology": sc["methodology"],
                "awardedPoints": sc["challenge_points"],
            },
        },
        "summaryScore": {
            "maximumChallengePoints": 80,
            "projectedAccuracyScore": "No medido (backtest pendiente)",
        },
    }

    # Save to file
    dto_path = REPORTS_DIR / "strategy_prediction_dto.json"
    with open(dto_path, "w", encoding="utf-8") as f:
        json.dump(dto, f, indent=2)

    return dto


def print_rich_report(pred_data: Dict[str, Any]):
    q = pred_data["quiniela_predictions"]
    pole = q["1_pole_position"]
    podium = q["2_podio_oficial"]
    fl = q["3_vuelta_rapida"]
    checo = q["4_posicion_checo_perez"]
    sc = q["5_safety_cars_fisicos"]

    banner = """
╔══════════════════════════════════════════════════════════════════════════════════╗
║  🏁 ESTRATEGA DE F1 - REPORTE CANÓNICO UNIFICADO (GRAN PREMIO DE MÉXICO)        ║
║     Autódromo Hermanos Rodríguez | 2,240 msnm | Densidad Aire: ~74% Nivel Mar    ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

    print(
        "┌──────────────────────────────────────────────────────────────────────────────────┐"
    )
    print(
        "│ 1️⃣  POLE POSITION (Sábado Q3) | Modelo: Simulación Monte Carlo (10 pts)           │"
    )
    print(
        "├──────────────────────────────────────────────────────────────────────────────────┤"
    )
    print(
        f"│  ▶ Piloto Pronosticado: {pole['driver']:<6} | Probabilidad: {pole['probability_pct']}%"
    )
    print(f"│  ▶ Contendientes:       {pole['top_contenders']}")
    print(f"│  ▶ Justificación:       {pole['rationale']}")
    print(
        "└──────────────────────────────────────────────────────────────────────────────────┘\n"
    )

    print(
        "┌──────────────────────────────────────────────────────────────────────────────────┐"
    )
    print(
        "│ 2️⃣  PODIO OFICIAL EXACTO (Domingo) | Modelo: Probabilidad Conjunta MC (35 pts)   │"
    )
    print(
        "├──────────────────────────────────────────────────────────────────────────────────┤"
    )
    print(
        f"│  ▶ 1° Lugar (Ganador, 15 pts): {podium['p1_winner']} (Probabilidad: {podium['p1_prob_pct']}%)"
    )
    print(
        f"│  ▶ 2° Lugar (10 pts):          {podium['p2_second']} (Probabilidad: {podium['p2_prob_pct']}%)"
    )
    print(
        f"│  ▶ 3° Lugar (10 pts):          {podium['p3_third']} (Probabilidad: {podium['p3_prob_pct']}%)"
    )
    print(
        f"│  ▶ Secuencia Exacta:           {' ➔ '.join(podium['exact_podium_sequence'])} (P Conjunta: {podium['combination_probability_pct']}%)"
    )
    print(f"│  ▶ Justificación:              {podium['rationale']}")
    print(
        "└──────────────────────────────────────────────────────────────────────────────────┘\n"
    )

    print(
        "┌──────────────────────────────────────────────────────────────────────────────────┐"
    )
    print(
        "│ 3️⃣  VUELTA RÁPIDA | Modelo: Ventana Táctica de Pits & Degradación (10 pts)       │"
    )
    print(
        "├──────────────────────────────────────────────────────────────────────────────────┤"
    )
    print(
        f"│  ▶ Piloto Seleccionado: {fl['driver']} (Probabilidad táctica: {fl['probability_pct']}%)"
    )
    print(f"│  ▶ Contendientes:       {fl['top_contenders']}")
    print(f"│  ▶ Justificación:       {fl['rationale']}")
    print(
        "└──────────────────────────────────────────────────────────────────────────────────┘\n"
    )

    print(
        "┌──────────────────────────────────────────────────────────────────────────────────┐"
    )
    print(
        "│ 4️⃣  POSICIÓN EXACTA CHECO PÉREZ | Modelo: Distribución Empírica MC (15 pts)      │"
    )
    print(
        "├──────────────────────────────────────────────────────────────────────────────────┤"
    )
    print(
        f"│  ▶ Posición Pronosticada: {checo['predicted_finish']} (Probabilidad: {checo['probability_pct']}%)"
    )
    print(f"│  ▶ Riesgo DNF Curva 1:    {checo['dnf_risk_pct']}%")
    print("│  ▶ Distribución:")
    for cand in checo["alternatives"]:
        print(f"│      - {cand['position']}: {cand['probability_pct']}%")
    print(f"│  ▶ Justificación:         {checo['rationale']}")
    print(
        "└──────────────────────────────────────────────────────────────────────────────────┘\n"
    )

    print(
        "┌──────────────────────────────────────────────────────────────────────────────────┐"
    )
    print(
        "│ 5️⃣  SAFETY CARS FÍSICOS (No VSC) | Modelo: Distribución de Poisson (10 pts)      │"
    )
    print(
        "├──────────────────────────────────────────────────────────────────────────────────┤"
    )
    print(
        f"│  ▶ Fórmula Estocástica:   P(X = k) = (λ^k * e^-λ) / k! | λ_efectiva = {sc['lambda_effective']}"
    )
    print(
        f"│  ▶ Conteo Pronosticado:   {sc['predicted_count']} Safety Car(s) físico(s) (Moda: {sc['mode_probability_pct']}%)"
    )
    print(
        f"│  ▶ P(Al menos 1 SC):      {sc['p_at_least_one_pct']}% (Embudo de 890m hacia Curva 1)"
    )
    print(f"│  ▶ Distribución:          {sc['distribution']}")
    print(f"│  ▶ Justificación:         {sc['rationale']}")
    print(
        "└──────────────────────────────────────────────────────────────────────────────────┘\n"
    )

    print(
        "===================================================================================="
    )
    print(
        "🎯 TOTAL PUNTOS POSIBLES: 80 PUNTOS | DTO EXPORTADO: reports/strategy_prediction_dto.json"
    )
    print(
        "===================================================================================="
    )


def main(n_simulations: int = 20000, seed: int = 42):
    predictor = F1RacePredictor(n_simulations=n_simulations, seed=seed)
    pred_data = predictor.generate_full_prediction()
    generate_and_export_dto(pred_data)
    print_rich_report(pred_data)


if __name__ == "__main__":
    main()
