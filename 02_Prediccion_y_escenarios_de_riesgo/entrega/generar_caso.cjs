'use strict';
// Reproduce el caso con los mismos contratos de decisión que utiliza la demo.
const fs = require('node:fs');
const path = require('node:path');
const Decision = require('../demo/decision.js');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '../demo/data/resultados.json'), 'utf8'));
const rows = data.municipios.filter(r => r.stable_catalog_state);
const key = '23008', r = rows.find(r => r.key === key);
const position = pool => Decision.rank(pool, 'tasa').findIndex(x => x.key === key) + 1;
const selected = Decision.planScenario(rows, 50, 1000, 25, 'tasa').selected.find(x => x.key === key);
const artifact = {
  source: 'demo/data/resultados.json',
  configuration: {state: null, search: '', stable_catalog: true, method: 'ridge', lens: 'tasa', capacity: 50, minimum_stability: 'todas', reach: 1000, response: 25},
  municipality: {key, historic_name: r.name, state: r.state_name, risk: r.risk, baseline: r.baseline, observed_2024: r.observed, ln_2024: r.ln, ns_2021: r.history.find(h => h.year === 2021).ns, ns_2024: r.latest_ns, profile: r.profile},
  position_ridge: position(rows),
  position_reference: position(rows.map(x => ({...x, risk: x.baseline}))),
  stability: Decision.selectionStability(rows, 50, 'tasa')[key],
  scenario: {served: selected.served, additional_hypothetical: selected.additional, before: r.risk, after: selected.after, reduction_pp: r.risk - selected.after},
  caveat: 'Nombre del catálogo histórico. Frecuencia entre variantes correlacionadas, no probabilidad. Respuesta hipotética, sin efecto causal demostrado.'
};
fs.writeFileSync(path.join(__dirname, 'caso_municipal.json'), JSON.stringify(artifact, null, 2) + '\n');
console.log(JSON.stringify({key, position: artifact.position_ridge, stability: artifact.stability.count + '/6', scenario: artifact.scenario}, null, 2));
