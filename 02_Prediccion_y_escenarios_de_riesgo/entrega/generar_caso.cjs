'use strict';
// Reproduce el caso con los mismos contratos de decisión que utiliza la demo.
const fs = require('node:fs');
const path = require('node:path');
const Decision = require('../demo/decision.js');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '../demo/data/resultados.json'), 'utf8'));
const rows = data.municipios.filter(r => r.stable_catalog_state);
const key = '23008', r = rows.find(r => r.key === key);
const position = pool => Decision.rank(pool, 'tasa').findIndex(x => x.key === key) + 1;
const localPlan = Decision.planIntervention([r], {budget:1000,reach:1000,action:'sms_suecia',lens:'tasa'});
const selected = localPlan.selected[0];
const artifact = {
  source: 'demo/data/resultados.json',
  configuration: {scope:'municipio',key,stable_catalog:true,method:'ridge',lens:'tasa',ranking_reference_capacity:50,minimum_stability:'todas',coverage_total:1000,distribution:'prioridad',action:'sms_suecia'},
  evidence: localPlan.action,
  municipality: {key, historic_name: r.name, state: r.state_name, risk: r.risk, baseline: r.baseline, observed_2024: r.observed, ln_2024: r.ln, ns_2021: r.history.find(h => h.year === 2021).ns, ns_2024: r.latest_ns, profile: r.profile},
  position_ridge: position(rows),
  position_reference: position(rows.map(x => ({...x, risk: x.baseline}))),
  stability: Decision.selectionStability(rows, 50, 'tasa')[key],
  scenario: {served:selected.served,additional_hypothetical:selected.additional,additional_low:localPlan.additional_low,additional_high:localPlan.additional_high,before:r.risk,after:selected.after,reduction_pp:r.risk-selected.after},
  caveat:'Nombre del catálogo histórico. Estabilidad 4/6 calculada con ranking de referencia top50, no probabilidad. Efecto SMS ITT externo, transferencia hipotética a México, no validada. Cobertura total de 1,000 personas distintas previstas para envío.'
};
fs.writeFileSync(path.join(__dirname, 'caso_municipal.json'), JSON.stringify(artifact, null, 2) + '\n');
console.log(JSON.stringify({key, position: artifact.position_ridge, stability: artifact.stability.count + '/6', scenario: artifact.scenario}, null, 2));
