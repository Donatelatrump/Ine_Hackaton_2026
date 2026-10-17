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

  function renderComparison(selection,rows){runtime.renderPlanComparison?.(selection,rows);}

  runtime.renderStatePlan=function(selection,records){
    const panel=document.getElementById('d6-state-plan');
    const content=document.getElementById('d6-state-plan-content');
    const title=document.getElementById('d6-state-plan-title');
    if(!panel||!content||!title)return;
    panel.hidden=selection.year!==2027;
    if(selection.year!==2027)return;
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
