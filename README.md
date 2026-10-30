# 🏁 Reto F1: Estratega de F1 con GitHub Stack & Copilot

Proyecto para el **"Desafío Tech: Conviértete en el 'Estratega de F1' con GitHub Stack"** (Gran Premio de México en el Autódromo Hermanos Rodríguez).

Este repositorio implementa un sistema integral de **análisis de telemetría, física aerodinámica/altitud a 2,240 msnm, simulación probabilística Monte Carlo y prompting para GitHub Copilot** para ganar la quiniela oficial.

---

## 🎯 Los 5 Puntos a Predecir & Sistema de Puntuación

| # | Punto a Predecir | Criterio de Puntuación | Puntos Máximos |
|---|------------------|-------------------------|:--------------:|
| **1** | **La Pole Position** | Piloto con el mejor tiempo en la Q3 del sábado | **10 pts** |
| **2** | **El Podio Oficial** | 1°, 2° y 3° lugar exactos del domingo (15 + 10 + 10 pts; o 5 pts c/u si aciertas piloto en otra posición del podio) | **35 pts** |
| **3** | **La Vuelta Rápida** | Piloto con el giro más veloz registrado en carrera | **10 pts** |
| **4** | **Posición de Checo Pérez** | Lugar exacto de llegada (o DNF/Abandono) | **15 pts** |
| **5** | **Safety Cars Físicos** | Conteo exacto de autos de seguridad físicos desplegados (excluye VSC) | **10 pts** |
| **TOTAL** | **Puntaje Máximo Posible** | | **80 pts** |

---

## 🏗️ Estructura del Repositorio

```text
RetoF1/
├── config/
│   └── settings.py          # Constantes del circuito (2,240m altitud, 71 vueltas, curva 1) y reglas de puntos
├── data/
│   ├── raw/                 # Respuestas crudas de APIs
│   ├── processed/           # Datasets limpios y unificados
│   └── samples/             # Datasets locales precargados (pilotos, últimas 3 carreras, histórico México, clima)
├── src/
│   ├── apis/                # Conectores modulares de datos
│   │   ├── fastf1_client.py # Telemetría oficial vía FastF1 con caché local
│   │   ├── openf1_client.py # API REST pública OpenF1 (vueltas, intervalos, tiempos)
│   │   ├── ergast_client.py # Histórico Jolpica / Ergast F1 (resultados, podios, poles)
│   │   └── weather_client.py# Pronóstico meteorológico en tiempo real (Open-Meteo)
│   ├── features/            # Feature Engineering & Modelado Físico
│   │   ├── altitude_physics.py # Impacto de altitud: densidad del aire (-25%), refrigeración de frenos y turbos
│   │   ├── recent_form.py   # Análisis de momentum y fiabilidad en las últimas 3 carreras
│   │   ├── checo_analyzer.py# Modelo específico para Checo Pérez (histórico CDMX, riesgo curva 1)
│   │   └── safety_car_model.py# Distribución de probabilidad de Safety Car físico
│   ├── models/              # Simulación & Pronóstico
│   │   ├── monte_carlo_sim.py # Simulador Monte Carlo (2,500+ carreras por corrida)
│   │   └── predictor.py     # Agregador oficial de las 5 predicciones con porcentajes
│   ├── evaluation/
│   │   └── scoring.py       # Validador y calculador de puntos oficial del desafío
│   └── prompts/
│       └── copilot_assistant.py # Generador dinámico de prompts con telemetría inyectada
├── prompts/
│   ├── copilot_prompts.md   # Prompts listos para copiar/pegar en GitHub Copilot Chat
│   └── submission_template.md # Plantilla formateada para la entrega de respuestas
├── main.py                  # CLI principal del proyecto
├── requirements.txt         # Dependencias Python
└── README.md
```

---

## ⚡ Inicio Rápido

### 1. Clonar y preparar entorno
```bash
git clone <url-del-repo>
cd RetoF1
python3 -m venv venv
source venv/bin/activate    # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Nota:** El proyecto funciona **out-of-the-box** de forma local gracias a los datos precargados en `data/samples/`, por lo que puedes ejecutar simulaciones de inmediato mientras se recopilan datos adicionales de APIs.

### 2. Ejecutar la Simulación y Generar el Pronóstico
```bash
python main.py --predict
```

### 3. Ver todas las opciones disponibles
```bash
python main.py --all            # Ejecuta física, simulación, demo de puntos y prompt
python main.py --physics        # Ver análisis de altitud, densidad del aire y refrigeración
python main.py --test-score     # Simulación de evaluación de puntos
python main.py --prompt         # Muestra el prompt oficial para Copilot
python main.py --sims 5000      # Aumenta el número de iteraciones Monte Carlo
```

---

## 🤖 Uso con GitHub Copilot (Requisito de Entrega)

La mecánica del concurso solicita:
> *"Envía tus 5 respuestas y captura de pantalla de tu interacción con GitHub Copilot... Se considerará la mayor cantidad de tecnología apalancada y el horario de entrega como criterio de desempate."*

1. Abre este proyecto en **VS Code** o tu IDE con GitHub Copilot habilitado.
2. Abre **GitHub Copilot Chat** (`Ctrl+Alt+I` o icono lateral).
3. Utiliza la guía en [`prompts/copilot_prompts.md`](file:///home/rfeynman/Dropbox/src/RetoF1/prompts/copilot_prompts.md).
4. El prompt inyecta los resultados de nuestra simulación Monte Carlo y el análisis físico de los 2,240 metros sobre el nivel del mar, lo que genera una respuesta técnica de alto impacto para la captura de pantalla de entrega.

---

## 📊 Factores Clave del Modelo (Autódromo Hermanos Rodríguez)

1. **Altitud Extrema (2,240 msnm):**
   - Densidad del aire de aproximadamente **~74-78%** respecto al nivel del mar.
   - Aunque los monoplazas montan alerones de máxima carga (configuración Mónaco), la densidad reducida produce carga aerodinámica equivalente a Monza.
   - Velocidades punta de **>350 km/h** en la recta principal de 890m.
2. **Refrigeración Crítica:**
   - La masa de aire que entra a los radiadores y ductos de freno cae en ~25%, provocando sobrecalentamiento térmico severo y mayor riesgo de fallas de frenos y MGU-H/turbocompresor (girando cerca de las 125,000 RPM límite).
3. **Peligro en Curva 1:**
   - La recta de 890 metros hasta la primera frenada es la más larga del calendario, generando un embudo de 20 monoplazas que dispara la probabilidad histórica de Safety Car físico en la vuelta 1 al **54-70%**.
4. **Factor Checo Pérez:**
   - Historial en México: P3 (2021), P3 (2022), DNF (2023 por contacto en curva 1), P17 (2024).

---

## 🤝 Colaboración

Para trabajar con tu compañero:
1. Crea tu rama de trabajo: `git checkout -b feature/nuevas-apis`
2. Si agregas endpoints de nuevas APIs, agrégalos dentro del módulo `src/apis/`.
3. Para validar que todo siga corriendo: `python main.py --predict`.
