function getAvailableYears(){
  const years = new Set();
  if(typeof records === 'undefined' || !records) return [2027];
  for(const r of records){
    for(const h of (r.history||[])){
      if(Number.isFinite(h.year)){
        years.add(h.year);
      }
    }
  }
  years.add(2027);
  return [...years].sort((a,b)=>a-b);
}

function populateMapYearSelector(){
  const sel = $('map-year');
  if(!sel){return;}
  sel.replaceChildren();
  const years = getAvailableYears();
  for(const y of years){
    sel.add(new Option(String(y),String(y)));
  }
  if(years.length){sel.value = String(currentMapYear);}
  console.log('Umbral map: años disponibles:', years);
}

