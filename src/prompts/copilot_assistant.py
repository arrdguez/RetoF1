import json
from typing import Dict, Any, Optional

class CopilotPromptGenerator:
    """
    Generates tailored Copilot prompts for the challenge.
    These prompts are formatted to be pasted directly into GitHub Copilot Chat (VS Code / JetBrains / Web)
    to generate the required screenshot evidence for the challenge submission.
    """

    @staticmethod
    def get_official_flyer_prompt() -> str:
        """
        The exact prompt shown on the official challenge flyer.
        """
        return (
            "Actúa como un Lead Data & Performance Engineer de Fórmula 1. "
            "Necesito procesar los datasets de telemetría de las últimas 3 carreras de la temporada, "
            "el histórico del Autódromo Hermanos Rodríguez a 2,240 metros sobre el nivel del mar y "
            "el pronóstico de clima para el fin de semana.\n\n"
            "Tomando en cuenta la carga aerodinámica, refrigeración de frenos y la fiabilidad de las "
            "unidades de potencia actuales, genera una predicción fundamentada con porcentajes de "
            "probabilidad para:\n"
            "1) Ganador de la Pole Position,\n"
            "2) Top 3 exacto en carrera,\n"
            "3) Vuelta rápida,\n"
            "4) Posición final de Checo Pérez,\n"
            "5) Número de Safety Cars físicos esperados.\n\n"
            "Justifica brevemente la lógica de cada estimación."
        )

    @staticmethod
    def get_enriched_telemetry_prompt(telemetry_summary: Optional[Dict[str, Any]] = None) -> str:
        """
        An advanced prompt that injects calculated physics (air density ratio, altitude cooling loss)
        and Monte Carlo baseline stats to produce an even more impressive Copilot response.
        """
        summary_str = ""
        if telemetry_summary:
            summary_str = f"\n\nContexto Telemetría y Simulación calculada:\n```json\n{json.dumps(telemetry_summary, indent=2)}\n```"

        return (
            "Actúa como Lead Strategy & Performance Engineer de F1 para el GP de México "
            "(Autódromo Hermanos Rodríguez, 2,240m de altitud, densidad del aire ~78% del nivel del mar).\n"
            "Hemos analizado la telemetría de las últimas 3 carreras (Baku, Marina Bay, Austin), degradación térmica "
            "de frenos y turbos operando cerca del límite de 125,000 RPM, y la longitud de 890m hasta la Curva 1.{summary}\n\n"
            "Con base en estos datos y simulaciones, genera tu pronóstico definitivo estructurado con probabilidades exactas:\n"
            "1. Ganador de la Pole Position (Q3 Sábado)\n"
            "2. Podio Oficial Exacto (1°, 2° y 3° lugar)\n"
            "3. Vuelta Rápida\n"
            "4. Posición final de Checo Pérez (o DNF)\n"
            "5. Número exacto de Safety Cars físicos (sin contar VSC)\n\n"
            "Incluye un resumen técnico de 2 líneas por cada punto explicando el factor crítico (aerodinámica, refrigeración, tráfico o fiabilidad)."
        ).format(summary=summary_str)
