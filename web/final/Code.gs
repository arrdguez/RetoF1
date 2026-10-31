/**
 * Instantánea preclasificación. Fuente: reports/strategy_prediction_dto.json,
 * reports/informe_cientifico.md y docs/reto_f1_transcripcion.md.
 * No se recalculan probabilidades ni se consultan resultados en tiempo real.
 */
function doGet() {
  const page = HtmlService.createTemplateFromFile('Index');
  page.payload = JSON.stringify(getPredictionData_()).split(String.fromCharCode(60)).join('\\u003c');
  return page.evaluate()
    .setTitle('APEX Intelligence · GP de México 2026')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function getPredictionData_() {
  return {
    event: 'Mexico City Grand Prix 2026',
    eventDate: '1 de noviembre de 2026',
    simulations: 20000,
    rounds: 18,
    maxPoints: 80,
    // Los cinco pronósticos coinciden con el DTO. Probabilidades en porcentaje.
    predictions: [
      { id: 'pole', label: 'Pole position', answer: 'Antonelli · ANT', pct: 16.35, points: 10, type: 'individual', method: 'Plackett–Luce + Monte Carlo', note: 'Piloto con el mejor tiempo de Q3. No equivale a probabilidad de victoria.' },
      { id: 'podium', label: 'Podio oficial', answer: 'ANT · HAM · VER', pct: 0.53, points: 35, type: 'conjunta', method: 'Simulación + valor esperado', note: 'Orden exacto: 1.º Antonelli, 2.º Hamilton, 3.º Verstappen. Los 35 puntos solo se obtienen si el orden es exacto; puede haber puntos parciales.' },
      { id: 'lap', label: 'Vuelta rápida', answer: 'Hamilton · HAM', pct: 15.42, points: 10, type: 'individual', method: 'Ritmo + historial de México', note: 'Estimación del piloto que marcará el giro más rápido en carrera.' },
      { id: 'checo', label: 'Checo Pérez', answer: 'DNF · Abandono', pct: 15.89, points: 15, type: 'resultado exacto', method: 'Posición simulada + riesgo DNF', note: 'DNF es el resultado individual más frecuente, no la probabilidad total de terminar en la zona baja.' },
      { id: 'sc', label: 'Safety Cars físicos', answer: '0 · Ninguno', pct: 48.23, points: 10, type: 'conteo exacto', method: 'Poisson–Gamma bayesiano', note: 'Se cuentan coches de seguridad físicos; no se incluyen Virtual Safety Cars (VSC).' }
    ],
    // Pole y Checo: DTO. Victoria: informe científico (cifras más precisas del prototipo D).
    charts: [
      { id: 'pole', title: 'Pole position', question: '¿Quién tiene más opciones de salir primero?', scale: 20, rows: [['ANT', 16.35], ['HAM', 13.41], ['VER', 12.19], ['LEC', 10.21], ['NOR', 8.39]], note: 'Cinco candidatos destacados; el resto no aparece en esta selección.' },
      { id: 'winner', title: 'Victoria', question: '¿Quién tiene más opciones de ganar?', scale: 20, rows: [['ANT', 16.61], ['HAM', 14.02], ['VER', 12.52], ['LEC', 10.85], ['NOR', 8.58], ['RUS', 7.99]], note: 'Probabilidades individuales, distintas de la probabilidad de acertar el podio completo.' },
      { id: 'checo', title: 'Checo Pérez', question: '¿Qué resultado exacto es más frecuente?', scale: 20, rows: [['DNF', 15.89], ['P19', 13.26], ['P20', 12.30], ['P18', 11.23], ['P17', 8.70], ['P21', 7.74]], note: 'Seis escenarios destacados. DNF significa abandono.' },
      { id: 'sc', title: 'Safety Cars físicos', question: '¿Cuántos coches de seguridad podrían salir?', scale: 50, rows: [['0', 48.23], ['1', 32.15], ['2', 13.40], ['3', 4.47], ['4 o más', 1.75]], note: '4 o más es el resto calculado a partir del DTO; solo Safety Cars físicos.' }
    ]
  };
}

