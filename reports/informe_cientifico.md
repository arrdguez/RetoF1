# Informe científico-estadístico de predicción

## Gran Premio de México 2026 — Desafío Tech "Estratega de F1"

**Evento objetivo:** Mexico City Grand Prix 2026 (ronda 19, 1 de noviembre de 2026), Autódromo Hermanos Rodríguez (2,240 m s. n. m.).
**Fecha de corte de datos:** 30–31 de octubre de 2026 (antes del inicio de la clasificación). Ningún dato posterior al corte fue utilizado.

---

## 1. Resumen ejecutivo

| # | Punto | Pronóstico | Prob. | Método estadístico | Puntos |
|---|-------|-----------|-------|--------------------|--------|
| 1 | Pole (Q3) | **ANT — Antonelli** | 15.2 % | Plackett-Luce + Monte Carlo | 10 |
| 2 | Podio (1º·2º·3º) | **ANT · HAM · VER** | 0.4 % conjunta | Plackett-Luce + optimización de EV | 35 |
| 3 | Vuelta rápida | **RUS — Russell** | 14.9 % | Pesos ritmo × historial | 10 |
| 4 | Posición de Checo Pérez | **P20** (DNF 15.5 %) | 15.9 % | Distribución empírica Monte Carlo | 15 |
| 5 | Safety Cars físicos | **0** | 48.2 % | Poisson-Gamma Bayesiano | 10 |

**Mensaje clave:** el campo 2026 está *muy apretado* en la cabeza (los 6 primeros pilotos tienen entre 10 % y 15 % de ganar), por lo que ninguna apuesta de podio tiene alta probabilidad. La certeza real del sistema está en dos extremos: **Checo en la cola (P17–P21 / DNF, por Cadillac con 0 puntos)** y **0 Safety Cars** como moda empírica.

---

## 2. Contexto temporal y coherencia

Se define explícitamente el evento y el corte para evitar contaminación (fugas de información futura):

- **Temporada:** 2026. **Evento:** GP de México (R19).
- **Corte:** 31 de octubre de 2026, antes de clasificación. La regla exige entregar antes de la qualy (transcripción del reto, línea 60).
- **Dato de forma reciente:** clasificación de pilotos y constructores tras la ronda 18 (COTA, 25 de octubre de 2026) — es la señal de ritmo más actual disponible y, al ser acumulada, resume la temporada completa, no solo 3–4 carreras.
- **Parrilla y equipos:** 22 pilotos / 11 equipos de 2026 (Mercedes, Ferrari, Red Bull, McLaren, Racing Bulls, Alpine, Haas, Audi, Williams, Aston Martin, Cadillac). El cruce piloto→equipo usa `constructorId` (identificador estable), nunca el nombre visible.

---

## 3. Datos y fuentes

| Conjunto | Fuente | Nota |
|----------|--------|------|
| Clasificación pilotos 2026 (R18) | Jolpica/Ergast (`api.jolpi.ca`) | 23 pilotos, puntos y victorias |
| Clasificación constructores 2026 (R18) | Jolpica/Ergast | 11 equipos, indexado por `constructorId` |
| Histórico GP México (resultados + qualy) | Jolpica/Ergast, 2015–2025 | ganadores, podios, poles, vueltas rápidas, DNF, posiciones por piloto |
| Equipos 2026 por piloto | Wikipedia (tabla "Entries" 2026) | único dato de entrada manual, marcado y trazable |
| Safety Cars físicos por edición | Compilado de informes de carrera (2021–2024) | n = 4; ver limitaciones |
| Clima fin de semana 2026 | Open-Meteo | actual, no incorporado causalmente (ver §6) |

---

## 4. Metodología (reseña de cada método)

### 4.1 Ratings de rendimiento (skill)
Cada piloto recibe un *skill* logarítmico construido **solo** a partir de datos reales:

```
skill = 0.35·log(1+pts_2026) + 0.20·log(1+victorias) + 0.30·log(1+pts_equipo) + 0.15·afinidad_México
```

- **Forma 2026 (35 %):** puntos reales del campeonato (escala log).
- **Victorias (20 %):** señal de dominancia — predecir *quién gana* necesita victorias, no solo consistencia.
- **Equipo (30 %):** puntos del constructor (en F1 el coche explica gran parte del rendimiento).
- **Afinidad México (15 %):** victorias, podios y posición media histórica de cada piloto en este trazado (2015–2025).

Los pesos (0.35 / 0.20 / 0.30 / 0.15) son hiperparámetros documentados, no calibrados hacia un resultado concreto.

### 4.2 Modelo Plackett-Luce (permutaciones)
La posición final es una **permutación**; el modelo canónico para ordenar es Plackett-Luce. La probabilidad de un orden completo es el producto de elecciones sucesivas con pesos proporcionales a `exp(skill)`. Produce la **probabilidad conjunta del podio exacto** (lo que exige el punto 2), no solo marginales.

### 4.3 Monte Carlo (incertidumbre y eventos raros)
Sobre el modelo base: ruido multiplicativo por iteración (mayor en clasificación), abandonos mecánicos por piloto (con penalización para Cadillac, escudería debutante), riesgo de curva 1 según posición de salida, y penalización por salir atrás. **20 000 iteraciones con semilla fija (42)** → distribuciones completas, no una sola cifra.

### 4.4 Poisson-Gamma Bayesiano (Safety Cars)
En lugar de fijar λ=0.75, se modela de forma Bayesiana:
- Prior débil sobre la tasa: λ ~ Gamma(1, 1).
- Posterior con 3 SC en 4 ediciones: λ ~ Gamma(4, 5) → media 0.80, intervalo creíble 90 % [0.27, 1.55].
- **Predictiva** (lo que importa para apostar): **Binomial Negativa**, que ya incorpora la incertidumbre de estimar λ con n=4.

La moda es **0 SC (48.2 %)**, seguida de 1 SC (32.2 %).

### 4.5 Vuelta rápida
Pesos construidos con ritmo de carrera proyectado × historial real de vuelta rápida en México. Sin regresión sintética. Favorece a pilotos con ritmo y con giros rápidos previos aquí (Russell y Leclerc lideran con 2 cada uno en la era moderna).

### 4.6 Optimización de puntos esperados (EV) — y qué significa "piloto en el podio (posición distinta)"
La regla del concurso otorga **puntos parciales**: si aciertas el piloto pero **no su posición exacta**, ganas **5 pts**.

> **Ejemplo:** si apuestas a VER como ganador y VER termina **2º o 3º**, ganas **5 pts** (no 15 ni 0). Es el premio de consolación por acertar al piloto *dentro del podio* pero no su casilla exacta.

Por eso el podio "más probable" no es necesariamente el que maximiza puntos. Se optimiza la **terna ordenada de pilotos distintos** que maximiza:

```
EV = Σ_slots [ 5·P(piloto en podio) + (w_slot − 5)·P(piloto en posición exacta) ]
```
donde w = (15, 10, 10). La terna resultante (ANT→HAM→VER) es la de mayor valor esperado (≈ 8.4 pts).

---

## 5. Resultados detallados

### 5.1 Pole (moda)
| Piloto | Prob. |
|--------|-------|
| ANT | 15.2 % |
| VER | 12.4 % |
| HAM | 11.1 % |
| RUS | 10.9 % |
| NOR | 10.8 % |
| LEC | 9.8 % |

### 5.2 Ganador (marginal)
| Piloto | Prob. |
|--------|-------|
| ANT | 15.7 % |
| VER | 12.6 % |
| HAM | 12.0 % |
| RUS | 11.5 % |
| NOR | 10.9 % |
| LEC | 9.8 % |

### 5.3 Posición de Checo Pérez (distribución empírica)
Cadillac tiene 0 puntos en 2026 (11º de 11 constructores).

| Resultado | Prob. |
|-----------|-------|
| P20 | 15.9 % |
| DNF | 15.5 % |
| P19 | 15.4 % |
| P18 | 11.6 % |
| P21 | 10.6 % |
| P17 | 7.7 % |

**La moda es P20, con un riesgo de DNF del 15.5 %.** Cualquier pronóstico de "P5–P7" carece de base en los datos de 2026.

### 5.4 Safety Cars físicos (Poisson-Gamma, predictiva Binomial Negativa)
| k | Prob. |
|---|-------|
| 0 | 48.2 % |
| 1 | 32.2 % |
| 2 | 13.4 % |
| 3 | 4.5 % |
| 4+ | 1.8 % |

Moda y pick EV-óptimo: **0 Safety Cars**. λ posterior: media 0.80, IC 90 % [0.27, 1.55].

---

## 6. Validación y limitaciones (honestidad metodológica)

**Anclas de calibración observadas en el histórico de México (2015–2025):**
- La pole convierte en victoria el 50 % de las veces.
- El ganador sale, en promedio, de la posición 1.8.
- Verstappen concentra 5 de 10 victorias de la era moderna.

**Limitaciones:**
1. **Safety Cars:** n=4 → la incertidumbre de λ es alta (IC 90 % [0.27, 1.55]). Es un prior débil, no una distribución calibrada; por eso "0" y "1" son casi equiprobables en la práctica.
2. **Sin telemetría por vuelta:** la vuelta rápida no usa degradación real (β1) porque FastF1 no aporta vueltas sin autenticación; se usa ritmo + historial, explícitamente.
3. **Clima no causal:** se presenta pero no altera la distribución (sin datos de lluvia que justifiquen cambiar λ o DNF).
4. **Sin backtest temporal completo:** la validación leave-one-out (predecir cada edición 2015–2025 con solo datos previos) queda como siguiente paso. No se publican métricas de calibración que no se hayan calculado.
5. **Semilla fija:** reproducible (semilla 42); no se reportan intervalos multi-semilla en esta versión.

---

## 7. Respuestas finales para la quiniela

| # | Respuesta |
|---|-----------|
| 1 | Pole: **ANT (Antonelli)** |
| 2 | Podio: **1º ANT · 2º HAM · 3º VER** |
| 3 | Vuelta rápida: **RUS (Russell)** |
| 4 | Checo Pérez: **P20** |
| 5 | Safety Cars físicos: **0** |
