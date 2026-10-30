# Pronóstico oficial — GP de México 2026 (resumen ejecutivo)

**Evento:** Mexico City Grand Prix 2026 (R19, 1-nov-2026) · **Corte de datos:** 30-31 oct 2026.
Informe completo: [`informe_cientifico.md`](informe_cientifico.md) · Motor canónico: `python main.py --predict`.

## Quiniela (5 respuestas)

| # | Punto | Pronóstico | Prob. | Método estadístico | Puntos |
|---|-------|-----------|-------|--------------------|--------|
| 1 | Pole (Q3) | **ANT — Antonelli** | 16.4 % | Plackett-Luce + Monte Carlo | 10 |
| 2 | Podio (1º·2º·3º) | **ANT · HAM · VER** | 0.5 % conjunta | Plackett-Luce + optimización EV | 35 |
| 3 | Vuelta rápida | **HAM — Hamilton** | 15.4 % | Rating Bradley-Terry × historial | 10 |
| 4 | Checo Pérez | **DNF** (P17-P21 si termina) | 15.9 % | Distribución empírica Monte Carlo | 15 |
| 5 | Safety Cars físicos | **0** | 48.2 % | Poisson-Gamma Bayesiano | 10 |

## Justificación breve

- **Pole y podio:** campo muy apretado. Antonelli lidera por rating 2026 (9 victorias); Hamilton le sigue por su registro cara a cara; Verstappen suma su dominio histórico en México (5 victorias) y su momento reciente (ganó R16 y R17). La terna ANT→HAM→VER maximiza el valor esperado del podio (8.9 pts).
- **Vuelta rápida:** Hamilton (1 giro rápido histórico en México + rating alto en 2026).
- **Checo:** Cadillac tiene 0 puntos en 2026 (11º de 11); la moda es DNF (15.9 %), con P17-P21 como zona más probable si termina.
- **Safety Cars:** Poisson-Gamma Bayesiano (3 SC en 4 ediciones) → moda **0 SC** (48.2 %), λ posterior media 0.80 (IC 90 % [0.27, 1.55]).

## Metodología (resumen)

Rating **Bradley-Terry** (máxima verosimilitud sobre las 18 rondas de 2026) + **equipo** + **momento** (últimas 4 carreras) + **afinidad México** → Plackett-Luce (permutaciones) → Monte Carlo 20 000 iteraciones (DNF, curva 1, parrilla) → Poisson-Gamma Bayesiano (SC) → optimización de puntos esperados (EV).

**Regla clave del concurso:** si aciertas al piloto en el podio pero no su posición exacta, ganas **5 pts** (premio parcial). Por eso se optimiza la terna completa, no el podio "más probable".

**Backtest realizado (SC, leave-one-out n=4):** 1 acierto de 4, Brier 0.691 → la tasa de Safety Cars es un prior débil; "0 SC" es el pick de máximo valor esperado.

Sin valores a mano, sin regresión sintética, sin Random Forest sobre muestras diminutas. Cada cifra se calcula en `src/models/statistical_engine.py`.
