/* Ficha descriptiva: conserva siempre el alcance estatal de las fuentes. */
(() => {
  'use strict';
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number=new Intl.NumberFormat('es-MX',{maximumFractionDigits:0});
  const percent=value=>Number.isFinite(value)?value.toFixed(2)+'%':'Sin dato';
  const sourceLink=path=>'../../'+path.split('/').map(encodeURIComponent).join('/');
  const latestObservedRate=(rows)=>{
    for(const year of [2024,2021,2018,2015]){
      const s=UmbralAnalytics.summary(rows,year,'baseline');
      if(Number.isFinite(s.rate)) return {rate:s.rate,year,denominator:s.denominator};
    }
    return null;
  };

  function renderActionPlan(stateKey){
    const title=document.getElementById('d6-action-plan-title');
    const content=document.getElementById('d6-action-plan-content');
    const plan=typeof window!=='undefined'&&window.getStatePlan?window.getStatePlan(stateKey):null;
    if(!title||!content)return;
    if(!plan){
      title.textContent='Plan de acción recomendado';
      content.innerHTML='<p class="d6-note">Selecciona un estado para ver su plan de acción recomendado.</p>';
      return;
    }
    title.textContent=`Plan de acción recomendado · ${escape(plan.name)}`;
    content.innerHTML=`
      <div class="d6-action-plan-body">
        <div class="d6-action-field"><span class="d6-action-label">Prioridad:</span><strong>${plan.priority.charAt(0).toUpperCase()+plan.priority.slice(1)}</strong></div>
        <div class="d6-action-field"><span class="d6-action-label">Ejes estratégicos:</span>${plan.axes.map(a=>`<span class="d6-action-chip">${escape(a)}</span>`).join('')}</div>
        <div class="d6-action-field"><span class="d6-action-label">Enfoque recomendado:</span><p>${escape(plan.priority)}</p></div>
        <div class="d6-action-field"><span class="d6-action-label">Acciones prioritarias:</span><ul class="d6-action-list">${plan.actions.map(a=>`<li>${escape(a)}</li>`).join('')}</ul></div>
        <div class="d6-action-field"><span class="d6-action-label">Actores sugeridos:</span>${plan.actors.map(a=>`<span class="d6-action-chip">${escape(a)}</span>`).join('')}</div>
        <div class="d6-action-field"><span class="d6-action-label">Indicadores de seguimiento:</span>${plan.indicators.map(i=>`<span class="d6-action-chip">${escape(i)}</span>`).join('')}</div>
      </div>
    `;
  }

  if(typeof window!=='undefined'&&window._umbralRuntime){
    window._umbralRuntime.renderProfile=function(selection,records){
      const host=document.getElementById('d6-state-profile');
      const data=window.UMBRAL_FICHAS_ESTATALES;
      if(!host||!data)return;
      const key=selection.state?String(selection.state).padStart(2,'0'):'';
      if(!key){
        host.innerHTML='<div class="d6-profile-empty"><span class="eyebrow">CONTEXTO ANTES DE SIMULAR</span><h3>Consulta la ficha de tu estado</h3><p>Selecciona un estado en el mapa para ver sus antecedentes, contexto poblacional y documentos de referencia. Al entrar a un municipio se conserva la ficha estatal.</p><a href="#modulo-1">Elegir estado en el mapa ↑</a></div>';
        document.getElementById('d6-action-plan-title').textContent='Plan de acción recomendado';
        document.getElementById('d6-action-plan-content').innerHTML='<p class="d6-note">Selecciona un estado para ver su plan de acción recomendado.</p>';
        return;
      }
      const rows=records.filter(r=>String(r.state).padStart(2,'0')===key);
      const info=data.states[key];
      const name=rows[0]?.state_name||info?.name||key;
      const municipality=selection.municipality&&rows.find(r=>r.key===selection.municipality);
      const card=(label,value,note)=>`<article><span>${escape(label)}</span><strong>${escape(value)}</strong><small>${escape(note)}</small></article>`;
      const history=[2015,2018,2021,2024].map(year=>{
        const s=UmbralAnalytics.summary(rows,year,'baseline');
        return `<tr><td>${year}</td><td>${percent(s.rate)}</td><td>${s.valid} / ${s.total}</td></tr>`;
      }).join('');
      const latest=latestObservedRate(rows);
      host.innerHTML=`<div class="d6-profile-heading"><div><span class="eyebrow">FICHA INFORMATIVA ESTATAL · ${escape(key)}</span><h3>${escape(name)}</h3></div><span class="d6-profile-badge">Datos y fuentes</span></div>
        <p class="d6-profile-scope">${municipality?`Estás consultando ${escape(municipality.name)}. Esta ficha corresponde a todo ${escape(name)}; sus cifras no son las del municipio.`:'Contexto de toda la entidad, independiente del filtro de municipios con proyección.'}</p>
        <div class="d6-profile-stats">${card('Población · 2024',info?.population?.['2024']?number.format(info.population['2024']):'Sin dato','Serie demográfica aportada; no lista nominal')}${card('Población · 2027',info?.population?.['2027']?number.format(info.population['2027']):'Sin dato','Proyección demográfica; no electores esperados')}${card('Municipios en la serie · 2027',info?.municipalities?.['2027']??'Sin dato','Cobertura del archivo demográfico')}</div>
        <div class="d6-profile-body"><section><h4>Antecedentes observados del estado</h4><div class="table-wrap"><table><thead><tr><th>Elección</th><th>Abstención</th><th>Municipios con dato</th></tr></thead><tbody>${history}</tbody></table></div><p class="d6-note">Promedios ponderados por SV + NV del año. Se usan todos los registros de la entidad, incluidos los que no tienen proyección para 2027. Presidenciales e intermedias tienen contextos distintos.</p></section><section><h4>Qué permiten conocer estas fuentes</h4><p>Los conteos describen lo ocurrido y las series demográficas aportan contexto poblacional. Los documentos complementan la lectura con metodología, cultura cívica y antecedentes institucionales.</p><p>No identifican por sí solos por qué una persona no votó ni demuestran qué acción funcionaría en este estado.</p><p class="d6-note">${escape(data.population_definition)}</p></section></div>
        <details class="d6-profile-sources"><summary>Documentos revisados y alcance de cada fuente</summary><div class="d6-source-grid">${data.sources.map(s=>`<article><span class="eyebrow">${escape(s.scope)}</span><h4>${escape(s.title)}</h4><p>${escape(s.note)}</p><a href="${sourceLink(s.path)}" target="_blank" rel="noopener">Consultar fuente local ↗</a></article>`).join('')}</div><p class="d6-note">También se revisaron los seis CSV de Bases_de_datos_explicativos. No se suman archivos solapados: la población mostrada procede únicamente de pobproy_ggrupos.csv. Las series de defunciones no se interpretan como motivos de abstención.</p><a href="data/fichas_estatales.json" download>Descargar datos, inventario y huellas de las fuentes ↓</a></details>`;
      renderActionPlan(key);
    };
    runtime.renderProfile=window._umbralRuntime.renderProfile;
  }
})();
