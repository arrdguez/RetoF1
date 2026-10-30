# Guion de presentación — Estratega de F1 (GP de México 2026)

**Autores:** Alejandro Rodríguez Rodríguez · Camilo Serrano Fuentes

Base de texto para las diapositivas. Cada bloque indica el título de la diapositiva y los puntos a incluir (y una nota de voz opcional para presentar).

---

## Diapositiva 1 — Portada

**Título:** Estratega de F1 — GP de México 2026
**Subtítulo:** Predicción estadística de la quiniela oficial
**Autores:** Alejandro Rodríguez Rodríguez · Camilo Serrano Fuentes

- Desafío Tech: "Conviértete en el Estratega de F1"
- Autódromo Hermanos Rodríguez · 2,240 m s. n. m.

> **Nota:** "Vamos a mostrar cómo predecimos los 5 resultados del GP de México con un modelo estadístico, no con intuición."

---

## Diapositiva 2 — El reto

**Título:** Los 5 puntos a predecir

| # | Punto | Puntos |
|---|-------|--------|
| 1 | Pole position | 10 |
| 2 | Podio exacto (1º·2º·3º) | 35 |
| 3 | Vuelta rápida | 10 |
| 4 | Posición de Checo Pérez | 15 |
| 5 | Safety Cars físicos | 10 |

- Regla clave: **5 puntos parciales** si aciertas el piloto en el podio pero no su posición exacta.
- Entrega antes de la clasificación del sábado.

> **Nota:** "El podio vale 35 puntos y tiene puntos parciales: por eso optimizamos valor esperado, no solo probabilidad."

---

## Diapositiva 3 — Datos reales

**Título:** Datos reales, no suposiciones

- **18 rondas de 2026** (orden de llegada y abandonos) — Jolpica/Ergast
- **Histórico del GP de México 2015–2025** (resultados y clasificación)
- **Parrilla oficial 2026:** 22 pilotos, 11 escuderías
- Contexto clave: Antonelli lidera con 365 pts (9 victorias); **Cadillac (Checo) tiene 0 puntos**

> **Nota:** "Todo se alimenta de datos reales. El cruce piloto–equipo usa identificadores estables, no nombres."

---

## Diapositiva 4 — Metodología

**Título:** Cuatro modelos estadísticos combinados

1. **Bradley-Terry** — rating de ritmo por comparación por pares (máxima verosimilitud).
2. **Plackett-Luce** — probabilidad de permutaciones (podio exacto).
3. **Monte Carlo** — 20 000 simulaciones para incertidumbre y eventos raros (DNF, curva 1).
4. **Poisson-Gamma Bayesiano** — Safety Cars con intervalo de credibilidad.

**Selección final:** optimización del **valor esperado de puntos**.

> **Nota:** "Cada cifra se calcula; nada se escribe a mano ni se inventa."

---

## Diapositiva 5 — Las 5 respuestas

**Título:** Nuestra quiniela

| # | Pronóstico | Prob. |
|---|-----------|-------|
| 1 | Pole: **Antonelli** | 16.4 % |
| 2 | Podio: **ANT · HAM · VER** | 0.5 % conjunta |
| 3 | Vuelta rápida: **Hamilton** | 15.4 % |
| 4 | Checo: **DNF** (P17–P21) | 15.9 % |
| 5 | Safety Cars: **0** | 48.2 % |

> **Nota:** "El podio está muy apretado; ser honestos con esa incertidumbre es parte del método."

---

## Diapositiva 6 — Pole y podio

**Título:** Pole y podio: un campo muy cerrado

- Ganador más probable: **Antonelli 16.6 %**, seguido de Hamilton (14.0 %) y Verstappen (12.5 %).
- Verstappen suma su dominio histórico en México (5 victorias) y su gran momento (ganó 2 de las 3 últimas).
- La terna **ANT→HAM→VER** maximiza el valor esperado (8.9 pts), no el podio "más probable".

> **Nota:** "Ningún piloto supera el 17 %: apostamos al que maximiza puntos esperados, no al favorito simple."

---

## Diapositiva 7 — Vuelta rápida y Checo

**Título:** Vuelta rápida y Checo Pérez

- **Vuelta rápida: Hamilton (15.4 %)** — rating alto + historial de giro rápido en México.
- **Checo: DNF (15.9 %)** — Cadillac tiene 0 puntos (11.º de 11); su zona realista es P17–P21 o abandono.
- Riesgo de abandono del 15.5 %.

> **Nota:** "Aquí el dato de Cadillac lo cambia todo: no es un Checo de Red Bull, es un coche sin puntos en toda la temporada."

---

## Diapositiva 8 — Safety Cars

**Título:** Safety Cars: modelo Bayesiano

- Poisson-Gamma Bayesiano (predictiva Binomial Negativa).
- Moda: **0 Safety Cars (48.2 %)**; 1 SC al 32.2 %.
- Tasa λ posterior: media 0.80, intervalo creíble 90 % [0.27, 1.55].

> **Nota:** "Con solo 4 ediciones verificadas, reportamos el intervalo de incertidumbre en lugar de fingir precisión."

---

## Diapositiva 9 — Validación

**Título:** Backtest temporal (leave-one-out 2016–2025)

- **45.0 / 55 puntos medios** (pole + podio + vuelta rápida).
- **44 %** de acierto de ganador (empata con el baseline "líder del campeonato").
- Brier del ganador: 0.80 · Safety Cars: 1/4 aciertos.

> **Nota:** "Medimos el modelo contra el pasado, sin fuga de información, y lo reportamos con honestidad."

---

## Diapositiva 10 — Honestidad y limitaciones

**Título:** Lo que sí y lo que no podemos garantizar

- ✅ Podio/pole con probabilidades reales, no confianzas inventadas.
- ✅ Corrección de Checo/Cadillac (el mayor acierto del modelo).
- ⚠️ Vuelta rápida y podio exacto son casi impredecibles (se dice con claridad).
- ⚠️ Safety Cars con muestra pequeña (n = 4).

> **Nota:** "La honestidad metodológica es parte de la entrega: preferimos decir 'no sabemos' a inventar un número."

---

## Diapositiva 11 — Conclusión

**Título:** Respuestas finales

**Pole Antonelli · Podio ANT–HAM–VER · Vuelta rápida Hamilton · Checo DNF · Safety Cars 0**

- Modelo estadístico, datos reales, validación temporal y optimización de puntos.
- Código y datos reproducibles en el repositorio.

> **Nota:** "Gracias. Preguntas."
