function initLensCards(){
 const cards=[...document.querySelectorAll('.lens-card')],select=$('lens');
 const apply=value=>{
  if(select.value!==value){select.value=value;update();}
  for(const c of cards){const on=c.dataset.lens===value;c.classList.toggle('active',on);c.setAttribute('aria-checked',on?'true':'false');c.tabIndex=on?0:-1;}
 };
 for(const card of cards){
  card.addEventListener('click',()=>apply(card.dataset.lens));
  card.addEventListener('keydown',e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();apply(card.dataset.lens);}});
 }
 select.addEventListener('change',()=>apply(select.value));
 apply(select.value);
}
