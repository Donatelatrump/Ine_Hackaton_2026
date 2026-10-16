/* Vista descriptiva; dependencias recibidas explícitamente. */
(() => {
  'use strict';
  window.UmbralDemo6Views=window.UmbralDemo6Views||{};
  window.UmbralDemo6Views.renderHistory=function({A,state,selectedRecords,territoryLabel,view,$,pct,fmt,esc}){
  function segments(points,kind){
    let result='',previous=null;
    for(const p of points){
      if(!Number.isFinite(p.rate)){previous=null;continue;}
      if(previous)result+=`<path class="${p.year===2027?'d6-forecast':kind}" d="M${previous.x},${previous.y} L${p.x},${p.y}"/>`;
      previous=p;
    }
    return result;
  }
    const rows=selectedRecords();
    const values=A.series(rows,state.method,state.year);
    const years=values.map(v=>v.year);
    const reference=state.municipality?A.series(A.subset(view,state,{municipality:false}),state.method,state.year):[];
    const x=year=>58+(year-2009)/18*610,y=rate=>234-rate*2;
    const points=values.map(v=>({...v,x:x(v.year),y:y(v.rate)}));
    const ref=reference.map(v=>({...v,x:x(v.year),y:y(v.rate)}));
    const grid=[0,25,50,75,100].map(n=>`<line class="d6-axis" x1="58" x2="668" y1="${y(n)}" y2="${y(n)}"/><text x="48" y="${y(n)+4}" text-anchor="end">${n}%</text>`).join('');
    const dots=points.filter(p=>Number.isFinite(p.rate)).map(p=>`<circle cx="${p.x}" cy="${p.y}" r="5" fill="${p.year===2027?'#fffdf8':'#10685f'}" stroke="#10685f" stroke-width="2"><title>${p.year}: ${pct(p.rate)} · ${p.valid}/${p.total} municipios</title></circle>`).join('');
    $('d6-history-chart').innerHTML=`<svg class="d6-chart" viewBox="0 0 720 280" role="img" aria-label="Evolución de la abstención de ${esc(territoryLabel())}">${grid}${segments(ref,'d6-reference')}${segments(points,'d6-observed')}${dots}${years.map(year=>`<text x="${x(year)}" y="260" text-anchor="middle">${year}</text>`).join('')}</svg>`;
    $('d6-reference-legend').hidden=!state.municipality;
    $('d6-forecast-legend').hidden=state.year!==2027;
    $('d6-history-table').innerHTML=values.map(v=>`<tr><td>${v.year}${v.year===2027?' · Proyección':''}</td><td>${pct(v.rate)}</td><td>${v.valid}/${v.total}</td><td>${fmt.format(v.denominator)}</td></tr>`).join('');
  };
})();
