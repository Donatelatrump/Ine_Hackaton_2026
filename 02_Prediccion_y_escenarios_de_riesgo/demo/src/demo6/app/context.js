'use strict';
const $=id=>document.getElementById(id), fmt=new Intl.NumberFormat('es-MX',{maximumFractionDigits:0}), pct=v=>Number.isFinite(v)?v.toFixed(2)+'%':'Sin estimación';
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const TIER={alta:'🟢 Alta',media:'🟡 Media',baja:'🔴 Baja',sin_datos:'⚪ Sin datos'};
const GROUP_NAME={edad:{'18_29':'Jóvenes 18–29','30_59':'Adultos 30–59','60_mas':'Personas 60+'},sexo:{hombres:'Hombres',mujeres:'Mujeres',no_binario:'No binario'},seccion:{urbana:'Urbana',mixta:'Mixta',rural:'Rural'}};
let records,metadata,perfil,geo,map,layer,filtered=[],view=[],plan,thresholds,thresholdsCache={},stability={},frontier={nucleo:[],frontera:[],fuera:[]},activeKey=null,selectedMap=new Map(),byKey,viewCache={},normCache=new Map();
const colors={bajo:'#8bbbad',medio:'#e8b451',alto:'#bd5472',sin_datos:'#8997ab'};
function quantile(values,q){const s=values.slice().sort((a,b)=>a-b),p=(s.length-1)*q,i=Math.floor(p);return s[i]+(s[Math.min(i+1,s.length-1)]-s[i])*(p-i);}
function norm2(v){let x=normCache.get(v);if(x===undefined){x=norm(v);if(normCache.size>6000)normCache.clear();normCache.set(v,x);}return x;}
function matches(r){return (!$('state').value||r.state===$('state').value)&&(!$('stable').checked||r.stable_catalog_state)&&norm2(r.name+' '+r.key).includes(norm2($('search').value.trim()));}
