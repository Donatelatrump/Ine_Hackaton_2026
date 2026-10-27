/* Render the selected state's plan and its 2027 comparison. */
(() => {
  'use strict';
  const normalize=value=>String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const stateAliases={'05':'Coahuila','15':'Estado de M\u00e9xico','16':'Michoac\u00e1n','30':'Veracruz'};
  let renderedPlanKey='';

  function statePlanSection(markdown,name,key){
    const aliases=[name,stateAliases[key]].filter(Boolean).map(normalize);
    const lines=markdown.split(/\r?\n/);
    const start=lines.findIndex(line=>{
      const heading=line.match(/^###\s+\d+(?:\.\d+)?\s+(.+?)\s*$/);
      return heading&&aliases.includes(normalize(heading[1]));
    });
    if(start<0)return '';
    let end=lines.findIndex((line,index)=>index>start&&/^#{1,3}\s+/.test(line));
    if(end<0)end=lines.length;
    return lines.slice(start+1,end).filter(line=>!line.startsWith('- **Impacto orientativo:**')).join('\n').trim();
  }

  function markdownToHtml(markdown){
    const inline=value=>escapeHtml(value).replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
    const lines=markdown.split(/\r?\n/),html=[];
    let list='';
    const closeList=()=>{if(list){html.push(`</${list}>`);list='';}};
    for(const raw of lines){
      const line=raw.trim();
      if(!line){closeList();continue;}
      const ordered=line.match(/^\d+\.\s+(.+)$/),unordered=line.match(/^[-*]\s+(.+)$/);
      if(ordered||unordered){
        const kind=ordered?'ol':'ul';
        if(list&&list!==kind)closeList();
        if(!list){list=kind;html.push(`<${kind}>`);}
        html.push(`<li>${inline((ordered||unordered)[1])}</li>`);
        continue;
      }
      closeList();
      if(!/^---+$/.test(line))html.push(`<p>${inline(line)}</p>`);
    }
    closeList();
    return html.join('');
  }

  const percentage=value=>`${value.toFixed(2)}%`;
  const roundedCount=value=>{
    const step=value<1000?10:value<10000?100:1000;
    return Math.round(value/step)*step;
  };
  function renderComparison(selection,rows){
    const panel=document.getElementById('d6-plan-comparison');
    const values=document.getElementById('d6-plan-comparison-values');
    const note=document.getElementById('d6-plan-comparison-note');
    if(!panel||!values||!note)return;
    const prediction=UmbralAnalytics.summary(rows,2027,selection.method);
    const base=prediction.denominator;
    if(!Number.isFinite(prediction.rate)||!base){
      panel.hidden=false;
      values.innerHTML='<p class="d6-note">No hay base suficiente para comparar este estado.</p>';
      note.textContent='La comparaci\u00f3n incluye municipios con estimaci\u00f3n v\u00e1lida para 2027.';
      return;
    }
    const lowEffect=0.3,centralEffect=1.5,highEffect=3.0,coverage=0.10;
    const impact=effect=>Math.min(base*prediction.rate/100,base*coverage*effect/100);
    const low=impact(lowEffect),central=impact(centralEffect),high=impact(highEffect);
    const afterCentral=Math.max(0,prediction.rate-100*central/base);
    panel.hidden=false;
    values.innerHTML=`<article><span>Sin aplicar el plan \u00b7 predicci\u00f3n 2027</span><strong>${percentage(prediction.rate)}</strong><small>Abstenci\u00f3n estimada; participaci\u00f3n ${percentage(100-prediction.rate)}</small></article><span class="d6-plan-comparison-arrow" aria-hidden="true">\u2192</span><article><span>Plan aplicado \u00b7 escenario central</span><strong>${percentage(afterCentral)}</strong><small>Abstenci\u00f3n estimada; participaci\u00f3n ${percentage(100-afterCentral)}</small></article>`;
    note.textContent=`Escenario: ${roundedCount(low).toLocaleString('es-MX')} a ${roundedCount(high).toLocaleString('es-MX')} votos adicionales (central: ${roundedCount(central).toLocaleString('es-MX')}); mejora estimada de 0.03 a 0.30 puntos porcentuales (central: 0.15). Supone alcanzar al 10 % de la base SV+NV 2024 y usa como proxy el efecto supuesto de informaci\u00f3n institucional pr\u00e1ctica (0.3 a 3.0 puntos; central 1.5) entre personas alcanzadas. No es un efecto comprobado del plan completo; la base excluye municipios sin estimaci\u00f3n.`;
  }

  runtime.renderStatePlan=function(selection,records){
    const panel=document.getElementById('d6-state-plan');
    const content=document.getElementById('d6-state-plan-content');
    const title=document.getElementById('d6-state-plan-title');
    if(!panel||!content||!title)return;
    const key=selection.state?String(selection.state).padStart(2,'0'):'';
    panel.hidden=false;
    if(!key){
      title.textContent='Plan de acci\u00f3n estatal';
      content.innerHTML='<p class="d6-note">Selecciona un estado para consultar su plan.</p>';
      document.getElementById('d6-plan-comparison').hidden=true;
      renderedPlanKey='';
      return;
    }
    const data=window.UMBRAL_FICHAS_ESTATALES;
    const rows=records.filter(row=>String(row.state).padStart(2,'0')===key);
    const name=rows[0]?.state_name||data?.states?.[key]?.name||key;
    if(renderedPlanKey===key){renderComparison(selection,rows);return;}
    try{
      const section=statePlanSection(statePlanMarkdown,name,key);
      if(!section)throw new Error(`No se encontr\u00f3 el plan de ${name}.`);
      title.textContent=`Plan de acci\u00f3n \u00b7 ${name}`;
      content.innerHTML=markdownToHtml(section);
      renderedPlanKey=key;
    }catch(error){
      content.innerHTML=`<p class="d6-note">${escapeHtml(error.message||'No se pudo mostrar el plan estatal.')}</p>`;
    }
    renderComparison(selection,rows);
  };
})();
