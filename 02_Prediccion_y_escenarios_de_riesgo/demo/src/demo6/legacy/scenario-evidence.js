function renderActionEvidence(a){
 $('custom-response').hidden=a.id!=='personalizada';
 $('response').disabled=a.id!=='personalizada';
 $('reach-label').textContent=a.estimand==='ITT'?'¿A cuántas personas planeas enviar el SMS en total?':a.estimand==='ATT'?'¿Con cuántas personas completarías la llamada en total?':'Personas que alcanzarías en total';
 $('coverage-help').textContent=a.estimand==='ITT'?'Cuenta personas distintas a quienes enviarías el SMS, no mensajes ni lectores.':a.estimand==='ATT'?'Cuenta conversaciones completadas sobre el plan de votación, no intentos de llamada.':'Introduce tu capacidad total de contacto. Es un supuesto proporcionado por ti.';
 if($('action-evidence').dataset.action===a.id)return;
 $('action-evidence').dataset.action=a.id;
 $('action-evidence').innerHTML=a.source?`<strong>${a.effect_pp} puntos porcentuales de aumento en el estudio</strong><p>Aplicación hipotética a México; requiere revisar si la población y el contexto son comparables.</p><details><summary>Consultar estudio, fuente y límites</summary><p>${esc(a.country)} · ${esc(a.election)}. ${esc(a.population)}</p><p>Efecto: ${a.effect_pp} pp · Estimador: ${esc(a.estimand)}. ${esc(a.unit)}</p><p>${esc(a.uncertainty)} ${esc(a.limits)}</p><p><a href="${esc(a.source)}" target="_blank" rel="noopener noreferrer">${esc(a.citation)}</a> ${esc(a.locator)}.${a.fulltext?` <a href="${esc(a.fulltext)}" target="_blank" rel="noopener noreferrer">Texto completo ↗</a>`:''}</p><p>Transferencia hipotética a México; no calibrada con CCPC. Un punto porcentual no es una respuesta porcentual entre abstencionistas.</p></details>`:`<strong>${esc(a.label)}</strong><p>${esc(a.limits)}</p>`;
}
