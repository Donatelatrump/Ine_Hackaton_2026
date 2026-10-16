'use strict';
let statePicker, municipalityPicker, pickerState;
function createSearchablePicker(input, menu, toggle, getOptions, choose) {
 let options = [], active = -1;
 const close = ()=>{menu.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');};
 const highlight = ()=>{
  [...menu.children].forEach((node,i)=>{node.setAttribute('aria-selected',i===active?'true':'false');});
  if(active>=0){input.setAttribute('aria-activedescendant',menu.children[active].id);menu.children[active].scrollIntoView({block:'nearest'});}
 };
 const open = (all=false)=>{
  const query = all?'':norm(input.value.trim());
  options=getOptions().filter(option=>norm(option.label+' '+(option.key||'')).includes(query));
  active=-1;
  menu.replaceChildren();
  options.forEach((option,i)=>{
   const node=document.createElement('div');
   node.id=menu.id+'-'+i;node.setAttribute('role','option');node.setAttribute('aria-selected','false');
   node.textContent=option.label;
   node.addEventListener('pointerdown',event=>event.preventDefault());
   node.addEventListener('click',()=>{choose(option);close();input.focus({preventScroll:true});});
   menu.appendChild(node);
  });
  if(!options.length){const empty=document.createElement('p');empty.className='picker-empty';empty.textContent=input.disabled?'Elige primero un estado':'Sin coincidencias';menu.appendChild(empty);}
  menu.hidden=false;input.setAttribute('aria-expanded','true');input.removeAttribute('aria-activedescendant');
 };
 input.addEventListener('input',()=>open());
 input.addEventListener('focus',()=>{input.select();open(true);});
 input.addEventListener('keydown',event=>{
  if(event.key==='Escape'){close();event.preventDefault();}
  if(event.key==='ArrowDown'||event.key==='ArrowUp'){
   event.preventDefault();if(menu.hidden)open(true);
   if(options.length){active=(active+(event.key==='ArrowDown'?1:-1)+options.length)%options.length;highlight();}
  }
  if(event.key==='Enter'&&!menu.hidden&&options.length){event.preventDefault();choose(options[active>=0?active:0]);close();}
 });
 input.addEventListener('blur',close);
 toggle.addEventListener('pointerdown',event=>event.preventDefault());
 toggle.addEventListener('click',()=>{if(input.disabled)return;if(menu.hidden){input.focus({preventScroll:true});input.select();open(true);}else close();});
 document.addEventListener('pointerdown',event=>{if(!input.parentElement.contains(event.target))close();});
 return {close};
}
function initSearchablePickers() {
 statePicker=createSearchablePicker($('state-picker'),$('state-options'),$('state-toggle'),
  ()=>[...$('state').options].map(o=>({key:o.value,label:o.text})),option=>{
   $('state').value=option.key;
   $('search').value='';
   $('state').dispatchEvent(new Event('input',{bubbles:true}));
   $('state').dispatchEvent(new Event('change',{bubbles:true}));
  });
 municipalityPicker=createSearchablePicker($('search'),$('municipality-options'),$('municipality-toggle'),
  ()=>records.filter(r=>r.state===$('state').value).sort((a,b)=>a.name.localeCompare(b.name,'es')).map(r=>({key:r.key,label:r.name})),option=>{
   $('search').value=option.label;
   $('search').dispatchEvent(new Event('input',{bubbles:true}));
   const polygon=layer.getLayers().find(p=>p.feature.properties.key===option.key);
    if(polygon&&typeof focusMunicipality==='function'){focusMunicipality(option.key,polygon);}
  });
}
function syncSearchablePickers() {
 if(!statePicker)return;
 const state=$('state').value;
 $('state-picker').value=$('state').selectedOptions[0]?.text||'Todo México';
 if(pickerState!==state){
  pickerState=state;
  statePicker.close();municipalityPicker.close();
 }
 $('search').disabled=!state;
 $('municipality-toggle').disabled=!state;
 $('search').placeholder=state?'Escribe o elige un municipio':'Elige primero un estado';
}
