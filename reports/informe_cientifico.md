# Informe científico-estadístico de predicción

## Gran Premio de México 2026 — Desafío Tech "Estratega de F1"

**Evento objetivo:** Mexico City Grand Prix 2026 (ronda 19, 1 de noviembre de 2026), Autódromo Hermanos Rodríguez (2,240 m s. n. m.).
**Fecha de corte de datos:** 30–31 de octubre de 2026 (antes del inicio de la clasificación). Ningún dato posterior al corte fue utilizado.

---

## 1. Resumen ejecutivo

| # | Punto | Pronóstico | Prob. | Método estadístico | Puntos |
|---|-------|-----------|-------|--------------------|--------|
| 1 | Pole (Q3) | **ANT — Antonelli** | 16.4 % | Plackett-Luce + Monte Carlo | 10 |
| 2 | Podio (1º·2º·3º) | **ANT · HAM · VER** | 0.5 % conjunta | Plackett-Luce + optimización de EV | 35 |
| 3 | Vuelta rápida | **HAM — Hamilton** | 15.4 % | Rating Bradley-Terry × historial | 10 |
| 4 | Posición de Checo Pérez | **DNF** (o P17-P21) | 15.9 % | Distribución empírica Monte Carlo | 15 |
| 5 | Safety Cars físicos | **0** | 48.2 % | Poisson-Gamma Bayesiano | 10 |

**Mensaje clave:** el campo 2026 está *muy apretado* en la cabeza (los 6 primeros pilotos tienen entre 8 % y 17 % de ganar), por lo que ninguna apuesta de podio tiene alta probabilidad. La certeza real del sistema está en dos extremos: **Checo en la cola (DNF / P17-P21, por Cadillac con 0 puntos)** y **0 Safety Cars** como moda empírica.

---

## 2. Contexto temporal y coherencia

Se define explícitamente el evento y el corte para evitar contaminación (fugas de información futura):

- **Temporada:** 2026. **Evento:** GP de México (R19).
- **Corte:** 31 de octubre de 2026, antes de clasificación. La regla exige entregar antes de la qualy.
- **Dato de ritmo:** las **18 rondas disputadas** de 2026 (R1-R18) descargadas de Jolpica/Ergast, incluidos orden de llegada y abandonos por ronda.
- **Parrilla y equipos:** 22 pilotos / 11 equipos de 2026. El cruce piloto→equipo usa `constructorId` (identificador estable), nunca el nombre visible.

---

## 3. Datos y fuentes

| Conjunto | Fuente | Nota |
|----------|--------|------|
| Resultados 18 rondas 2026 (R1-R18) | Jolpica/Ergast (`api.jolpi.ca`) | orden de llegada, DNF y puntos por ronda |
| Clasificación pilotos/constructores 2026 (R18) | Jolpica/Ergast | indexado por `constructorId` |
| Histórico GP México (resultados + qualy) | Jolpica/Ergast, 2015–2025 | ganadores, podios, poles, vueltas rápidas, DNF por piloto |
| Equipos 2026 por piloto | Wikipedia (tabla "Entries" 2026) | único dato de entrada manual, trazable |
| Safety Cars físicos por edición | Compilado de informes de carrera (2021–2024) | n = 4; ver limitaciones |
| Clima fin de semana 2026 | Open-Meteo | actual, no incorporado causalmente (ver §6) |

---

## 4. Metodología (reseña de cada método)

### 4.1 Rating Bradley-Terry (ritmo de piloto)
Se estima el ritmo de cada piloto con el **modelo Bradley-Terry**, el estándar para comparaciones por pares, ajustado por **máxima verosimilitud** (algoritmo iterativo de Zermelo) sobre las 18 rondas de 2026. La señal son todas las comparaciones "el piloto A terminó delante del piloto B" (y "un DNF pierde contra todo clasificado").

> Es el estimador estadísticamente correcto para rankings, superior a usar log(puntos): capta *a quién vence cada piloto*, no solo cuántos puntos suma. Sustituye a los ratings escritos a mano.

### 4.2 Momento (forma reciente)
Se añade una señal de **forma reciente** con ponderación temporal decreciente sobre las **últimas 4 carreras** (R15-R18): R18 = 0.4, R17 = 0.3, R16 = 0.2, R15 = 0.1. Esto capta subidas tardías de forma (por ejemplo, Verstappen ganó R16 y R17, lo que eleva su momento pese a un inicio de temporada irregular).

### 4.3 Modelo Plackett-Luce (permutaciones)
La posición final es una **permutación**; el modelo canónico para ordenar es Plackett-Luce. La probabilidad de un orden completo es el producto de elecciones sucesivas con pesos proporcionales a `exp(skill)`. Produce la **probabilidad conjunta del podio exacto** (lo que exige el punto 2), no solo marginales.

### 4.4 Monte Carlo (incertidumbre y eventos raros)
Sobre el modelo base: ruido multiplicativo por iteración (mayor en clasificación), abandonos mecánicos por piloto (con penalización para Cadillac, escudería debutante), riesgo de curva 1 según posición de salida, y penalización por salir atrás. **20 000 iteraciones con semilla fija (42)** → distribuciones completas, no una sola cifra.

### 4.5 Poisson-Gamma Bayesiano (Safety Cars)
En lugar de fijar λ=0.75, se modela de forma Bayesiana:
- Prior débil sobre la tasa: λ ~ Gamma(1, 1).
- Posterior con 3 SC en 4 ediciones: λ ~ Gamma(4, 5) → media 0.80, intervalo creíble 90 % [0.27, 1.55].
- **Predictiva** (lo que importa para apostar): **Binomial Negativa**, que ya incorpora la incertidumbre de estimar λ con n=4.

La moda es **0 SC (48.2 %)**, seguida de 1 SC (32.2 %).

### 4.6 Vuelta rápida
Pesos construidos con el rating Bradley-Terry de carrera × historial real de vuelta rápida en México. Sin regresión sintética. Favorece a pilotos con ritmo y con giros rápidos previos aquí (Hamilton y Leclerc lideran el histórico moderno).

### 4.7 Optimización de puntos esperados (EV) — y qué significa "piloto en el podio (posición distinta)"
La regla del concurso otorga **puntos parciales**: si aciertas el piloto pero **no su posición exacta**, ganas **5 pts**.

> **Ejemplo:** si apuestas a VER como ganador y VER termina **2º o 3º**, ganas **5 pts** (no 15 ni 0). Es el premio de consolación por acertar al piloto *dentro del podio* pero no su casilla exacta.

Por eso el podio "más probable" no es necesariamente el que maximiza puntos. Se optimiza la **terna ordenada de pilotos distintos** que maximiza:

```
EV = Σ_slots [ 5·P(piloto en podio) + (w_slot − 5)·P(piloto en posición exacta) ]
```
donde w = (15, 10, 10). La terna resultante (ANT→HAM→VER) es la de mayor valor esperado (≈ 8.9 pts).

---

## 5. Resultados detallados

### 5.1 Pole (moda)
| Piloto | Prob. |
|--------|-------|
| ANT | 16.4 % |
| HAM | 13.4 % |
| VER | 12.2 % |
| LEC | 10.2 % |
| NOR | 8.4 % |

### 5.2 Ganador (marginal)
| Piloto | Prob. |
|--------|-------|
| ANT | 16.6 % |
| HAM | 14.0 % |
| VER | 12.5 % |
| LEC | 10.9 % |
| NOR | 8.6 % |
| RUS | 8.0 % |

### 5.3 Posición de Checo Pérez (distribución empírica)
Cadillac tiene 0 puntos en 2026 (11º de 11 constructores).

| Resultado | Prob. |
|-----------|-------|
| DNF | 15.9 % |
| P19 | 13.3 % |
| P20 | 12.3 % |
| P18 | 11.2 % |
| P17 | 8.7 % |
| P21 | 7.7 % |

**La moda es DNF (15.9 %), con la zona P17-P21 como la más probable si termina.** Cualquier pronóstico de "P5–P7" carece de base en los datos de 2026.

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

### Backtest realizado
- **Safety Cars (leave-one-out, n=4):** se predijo cada edición 2021–2024 con las otras tres. Resultado: **1 acierto de 4**, **Brier 0.691**. Interpretación honesta: con 4 ediciones la tasa λ es débil y el conteo de SC es esencialmente impredecible; la apuesta "0 SC" es la de máximo valor esperado (4.82 pts), pero su calibración es limitada.

### Anclas de calibración observadas en el histórico de México (2015–2025)
- La pole convierte en victoria el 50 % de las veces.
- El ganador sale, en promedio, de la posición 1.8.
- Verstappen concentra 5 de 10 victorias de la era moderna.

### Limitaciones
1. **Safety Cars:** n=4 → IC 90 % de λ = [0.27, 1.55]. Es un prior débil, no una distribución calibrada.
2. **Sin telemetría por vuelta:** la vuelta rápida no usa degradación real (β1) porque FastF1 no aporta vueltas sin autenticación; se usa rating + historial, explícitamente.
3. **Clima no causal:** se presenta pero no altera la distribución.
4. **Sin backtest temporal completo de pole/podio:** requiere standings de temporadas previas (2015–2024); queda como siguiente paso. No se publican métricas de calibración que no se hayan calculado.
5. **Semilla fija:** reproducible (semilla 42); no se reportan intervalos multi-semilla en esta versión.

---

## 7. Respuestas finales para la quiniela

| # | Respuesta |
|---|-----------|
| 1 | Pole: **ANT (Antonelli)** |
| 2 | Podio: **1º ANT · 2º HAM · 3º VER** |
| 3 | Vuelta rápida: **HAM (Hamilton)** |
| 4 | Checo Pérez: **DNF** |
| 5 | Safety Cars físicos: **0** |
