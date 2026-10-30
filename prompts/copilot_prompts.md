# 🏎️ Guía de Prompting con GitHub Copilot para el Desafío F1

Este documento contiene los prompts diseñados específicamente para obtener las capturas de pantalla de interacción con **GitHub Copilot** requeridas en la entrega del reto.

---

## 📌 Prompt 1: Oficial del Flyer (Recomendado para Captura Directa)

Copia y pega este prompt exacto en **GitHub Copilot Chat** (en VS Code, JetBrains o GitHub.com):

```text
Actúa como un Lead Data & Performance Engineer de Fórmula 1. Necesito procesar los datasets de telemetría de las últimas 3 carreras de la temporada, el histórico del Autódromo Hermanos Rodríguez a 2,240 metros sobre el nivel del mar y el pronóstico de clima para el fin de semana.

Tomando en cuenta la carga aerodinámica, refrigeración de frenos y la fiabilidad de las unidades de potencia actuales, genera una predicción fundamentada con porcentajes de probabilidad para:
1) Ganador de la Pole Position,
2) Top 3 exacto en carrera,
3) Vuelta rápida,
4) Posición final de Checo Pérez,
5) Número de Safety Cars físicos esperados.

Justifica brevemente la lógica de cada estimación.
```

---

## 🚀 Prompt 2: Avanzado con Telemetría & Simulación Inyectada (Gana puntos por profundidad técnica)

Si deseas sorprender en el criterio de desempate (*"mayor cantidad de tecnología apalancada"*), usa este prompt tras correr el script de simulación `python main.py --predict`:

```text
Actúa como Lead Strategy & Performance Engineer de F1 para el GP de México en el Autódromo Hermanos Rodríguez (2,240m de altitud, densidad del aire ~78% del nivel del mar).

Hemos corrido una simulación Monte Carlo de 2,500 iteraciones con la telemetría de las últimas 3 carreras, modelado la pérdida de refrigeración en frenos y turbocompresores al 22%, y analizado el embotellamiento de 890 metros hasta la Curva 1.

Resultados de la simulación:
- Pole Position proyectada: LEC / VER / NOR
- Podio más probable: VER (1°), LEC (2°), NOR (3°)
- Vuelta Rápida: NOR / VER
- Posición Checo Pérez: P5 (Alternativa P6 / DNF por toque en Curva 1)
- Safety Cars físicos: 1 (54% de probabilidad histórica y geométrica)

Genera el reporte ejecutivo final para entregar en la Quiniela oficial con la justificación técnica de cada pronóstico y la estrategia de neumáticos recomendada.
```

---

## 📸 Checklist para la Captura de Entrega
1. Abrir VS Code con este repositorio abierto en el explorador.
2. Abrir la pestaña lateral de **GitHub Copilot Chat**.
3. Enviar uno de los prompts anteriores.
4. Tomar captura de pantalla nítida donde se aprecie:
   - El prompt enviado.
   - La respuesta estructurada de Copilot.
   - El árbol de archivos del proyecto (`RetoF1`).
