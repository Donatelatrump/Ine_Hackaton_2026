/* Vista descriptiva; dependencias recibidas explícitamente. */
(() => {
  'use strict';
  runtime.views=runtime.views||{};
  runtime.views.renderEvidence=function({state,metadata,name,$,fmt,esc}){
    const rows=[];
    const comparison=metadata.comparison_report;
    for(const [year,cut] of Object.entries(comparison.cuts)){
      for(const key of ['baseline','ridge','hgb','lightgbm','catboost']){
        const v=cut.models[key],timing=v.timing;
        rows.push(`<tr><td>${year}</td><td>${key==='baseline'?'Referencia homóloga':name(key)}</td><td>${fmt.format(v.n)}</td><td>${v.mae.toFixed(2)}</td><td>${v.mae_ponderado.toFixed(2)}</td><td>${Math.round(v.precision_top*v.top_k)}/${v.top_k}</td><td>${timing?(timing.fit_seconds_median*1000).toFixed(1):'No aplica'}</td><td>${timing?(timing.predict_seconds_median*1000).toFixed(2):'No medido'}</td></tr>`);
      }
    }
    $('d6-metrics').innerHTML=rows.join('');
    const selected=comparison.aggregates[comparison.selected_model];
    $('d6-model-note').textContent=`Comparamos cuatro modelos con las mismas 15 variables y cohortes. Seleccionado: ${name(comparison.selected_model)}, MAE medio ${selected.mean_mae.toFixed(3)} pp y ponderado ${selected.mean_weighted_mae.toFixed(3)} pp entre 2021 y 2024. LightGBM y HistGradientBoosting quedaron dentro de 0.05 pp de MAE; el desempate favoreció el menor error ponderado de HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva y no valida 2027. En 2024 la referencia conserva más aciertos top50 que el ganador.`;
    $('d6-method-note').textContent=state.year===2027?name(state.method)+'. '+
      (state.method==='baseline'?'Repite la abstención de 2021, última intermedia observada.':'Ajusta la referencia con antecedentes y variables agregadas. No garantiza una mejora en todas las elecciones.'):
      'Los porcentajes históricos son observados. El método no modifica los resultados de '+state.year+'.';
    const labels={abstencion_mismo_tipo:'Abstención en elección homóloga',abstencion_ultimo_proceso:'Abstención del último proceso',diferencia_ultimo_mismo:'Diferencia entre antecedentes',log_lista_nominal:'Tamaño de lista nominal (log)',proporcion_18_29:'Proporción de 18–29 años',proporcion_60_mas_sin_extremos:'Proporción de 60 años o más',proporcion_urbana:'Proporción urbana',eleccion_intermedia:'Tipo de elección'};
    const factors=metadata.coefficients_standardized.filter(v=>Number.isFinite(v.coefficient)).slice().sort((a,b)=>Math.abs(b.coefficient)-Math.abs(a.coefficient)).slice(0,8);
    const max=Math.max(1,...factors.map(v=>Math.abs(v.coefficient)));
    $('d6-factors').innerHTML=factors.map(v=>`<div class="d6-factor"><span>${esc(labels[v.feature]||v.feature.replaceAll('_',' '))}</span><div class="d6-factor-track"><i class="${v.coefficient<0?'negative':''}" style="width:${Math.abs(v.coefficient)/max*100}%"></i></div><strong>${v.coefficient>0?'+':''}${v.coefficient.toFixed(2)}</strong></div>`).join('');
  };
})();
