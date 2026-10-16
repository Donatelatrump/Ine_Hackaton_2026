(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.UmbralAnalytics=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const finite=Number.isFinite;
  const methodName=method=>({ridge:'Ridge',hgb:'HistGradientBoosting',lightgbm:'LightGBM',catboost:'CatBoost',baseline:'Referencia de 2021'}[method]||'Referencia de 2021');
  function initialMethod(metadata){return ['ridge','hgb','lightgbm','catboost'].includes(metadata.selected_model)?metadata.selected_model:'baseline';}
  function observation(record,year,method='baseline'){
    if(year===2027)return {rate:finite(record[method])?record[method]:null,
      weight:finite(record.observed)&&record.observed>0?record.observed:0,
      ln:record.ln,ns:record.latest_ns};
    const h=record.history.find(item=>item.year===year);
    // LN = SV + NV + NS. Los históricos exportan LN y NS%, no los conteos SV/NV.
    const weight=h&&finite(h.ln)&&finite(h.ns)?h.ln*(1-h.ns/100):0;
    return {rate:finite(h?.risk)?h.risk:null,weight:weight>0?weight:0,ln:h?.ln,ns:h?.ns};
  }
  function subset(records,state,{municipality=true}={}){
    return records.filter(r=>(!state.state||r.state===state.state)&&
      (!state.stable||r.stable_catalog_state)&&
      (!municipality||!state.municipality||r.key===state.municipality));
  }
  function summary(records,year,method){
    let weighted=0,denominator=0,totalWeight=0,valid=0;
    for(const r of records){
      const item=observation(r,year,method);
      totalWeight+=item.weight;
      if(!finite(item.rate))continue;
      valid++;
      if(item.weight>0){weighted+=item.rate*item.weight;denominator+=item.weight;}
    }
    const rate=denominator>0?weighted/denominator:null;
    return {rate,participation:finite(rate)?100-rate:null,total:records.length,valid,
      missing:records.length-valid,denominator,totalWeight,
      populationCoverage:totalWeight>0?100*denominator/totalWeight:null};
  }
  function series(records,method,maxYear=2027){
    const years=[...new Set(records.flatMap(r=>r.history.map(h=>h.year)))];
    if(maxYear===2027)years.push(2027);
    return years.filter(y=>y<=maxYear).sort((a,b)=>a-b)
      .map(year=>({year,...summary(records,year,method)}));
  }
  function historicalError(metadata,method){
    if(metadata.comparison_report)return metadata.comparison_report.cuts['2021'].models[method==='baseline'?'baseline':method]?.error_absoluto_p90;
    return metadata.checks?.['2021']?.[method==='ridge'?'ridge':'persistencia']?.error_absoluto_p90;
  }
  function csv(records,state,metadata){
    const rows=[['Clave INE','Estado','Municipio','Año','Tipo de dato','Método',
      'Abstención (%)','Participación (%)','Base SV+NV','Lista nominal','NS (%)',
      'Referencia 2021 (%)','Ridge 2027 (%)','Diferencia Ridge - referencia (pp)',
      'HistGradientBoosting 2027 (%)','LightGBM 2027 (%)','CatBoost 2027 (%)',
      'Catálogo constante','Fuente','Nota']];
    for(const r of records){
      const item=observation(r,state.year,state.method);
      rows.push([r.key,r.state_name,r.name,state.year,state.year===2027?'Proyección exploratoria':'Observado',
        state.year===2027?methodName(state.method):'No aplica',item.rate,
        finite(item.rate)?100-item.rate:null,item.weight||null,item.ln,item.ns,
        state.year===2027?r.baseline:null,state.year===2027?r.ridge:null,
        state.year===2027&&finite(r.ridge)&&finite(r.baseline)?r.ridge-r.baseline:null,
        state.year===2027?r.hgb:null,state.year===2027?r.lightgbm:null,state.year===2027?r.catboost:null,
        r.stable_catalog_state?'Sí':'No','INE · CCPC 2009–2024',
        state.year===2027?'SV+NV 2024 como base; electorado 2027 no proyectado. Sin estimación no equivale a cero.':
          'SV+NV reconstruido a partir de LN y NS%. Límites históricos sin armonizar.']);
    }
    const cell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
    return '\uFEFF'+rows.map(row=>row.map(cell).join(',')).join('\r\n');
  }
  return {methodName,initialMethod,observation,subset,summary,series,historicalError,csv};
});
