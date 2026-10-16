/* Vista descriptiva; dependencias recibidas explícitamente. */
(() => {
  'use strict';
  window.UmbralDemo6Views=window.UmbralDemo6Views||{};
  window.UmbralDemo6Views.renderSummary=function({A,state,selectedRecords,territoryLabel,records,view,name,$,pct,fmt,esc}){
  function metricCard(label,value,note){
    return `<article><span>${esc(label)}</span><strong>${value}</strong><small>${esc(note)}</small></article>`;
  }
    const rows=selectedRecords();
    const s=A.summary(rows,state.year,state.method);
    const model=state.year===2027?'Proyección · '+name(state.method):'Datos observados';
    $('d6-selection-label').textContent=territoryLabel()+' · '+state.year+' · '+model;
    $('d6-summary').innerHTML=metricCard('Abstención',pct(s.rate),'Promedio ponderado por SV + NV')+
      metricCard('Participación',pct(s.participation),state.year===2027?'Proyección complementaria':'Entre personas con dato de voto')+
      metricCard('Municipios con dato',fmt.format(s.valid)+' / '+fmt.format(s.total),s.missing+' sin dato o sin estimación')+
      metricCard('Cobertura de población',pct(s.populationCoverage),'Sobre la base observable del filtro');
    $('d6-summary-note').textContent='Base con tasa disponible: '+fmt.format(s.denominator)+' personas. '+
      (state.year===2027?'Se usa SV+NV 2024; no representa el electorado proyectado de 2027.':'SV+NV del año seleccionado, reconstruido desde LN y NS%.')+
      ' Los municipios sin dato no se cuentan como cero. La cobertura describe el filtro actual.';
    const stateRows=A.subset(view.length?view:records,state,{municipality:false});
    const st=A.summary(stateRows,state.year,state.method);
    const delta=Number.isFinite(s.rate)&&Number.isFinite(st.rate)?s.rate-st.rate:null;
    $('d6-context').hidden=!state.municipality;
    $('d6-context').innerHTML=`<span>Promedio de ${esc(records.find(r=>r.state===state.state)?.state_name||'la entidad')}: <strong>${pct(st.rate)}</strong></span><span>Brecha del municipio: <strong>${Number.isFinite(delta)?(delta>=0?'+':'')+delta.toFixed(2)+' pp':'Sin comparación'}</strong></span>`;
    $('d6-export').disabled=!rows.length;
  };
})();
