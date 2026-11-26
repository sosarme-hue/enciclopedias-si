window.__btn=(t)=>[...document.querySelectorAll('div[role=button],button,[role=tab],[role=radio]')].filter(x=>x.innerText.trim()===t);
window.__reelPrep=async function(vpath,key,dayLabel){
  const S=window.__S;window.__rready=0;await S(2000);
  const cb=[...document.querySelectorAll('[role=combobox],div[role=button]')].find(e=>/Compositores de Música Clásica y/.test(e.innerText));
  if(cb){cb.click();await S(900);const op=[...document.querySelectorAll('[role=option]')].find(e=>/composers_conductors_soloists/.test(e.innerText));op&&op.click();await S(700);document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));await S(700);}
  if(/composers_conductors_soloists/.test(document.body.innerText.slice(0,4000)))return 'IG still on';
  const r=await window.__get(vpath);window.__inp=null;window.__wantFile=1;
  window.__btn('Añadir vídeo')[0].click();for(let i=0;i<20&&!window.__inp;i++)await S(200);window.__wantFile=0;
  const inp=window.__inp;if(!inp)return 'noinput';await S(1000);
  const dt=new DataTransfer();dt.items.add(new File([r.v],'reel-'+key+'.mp4',{type:'video/mp4',lastModified:Date.now()}));inp.files=dt.files;
  inp.dispatchEvent(new Event('change',{bubbles:true}));inp.dispatchEvent(new Event('input',{bubbles:true}));
  for(let i=0;i<60&&!/1080 x 1920/.test(document.body.innerText);i++)await S(500);
  if(!/1080 x 1920/.test(document.body.innerText))return 'media not attached';
  await S(4000);
  const ed=[...document.querySelectorAll('[contenteditable=true]')].filter(e=>e.offsetParent)[0];ed.focus();
  const d2=new DataTransfer();d2.setData('text/plain',window.__caps[key]);ed.dispatchEvent(new ClipboardEvent('paste',{clipboardData:d2,bubbles:true,cancelable:true}));await S(1500);
  if(!/3 curiosidades/.test(ed.innerText))return 'caption missing';
  // wait for copyright check
  let cr='';for(let i=0;i<60;i++){const t=document.body.innerText;if(/Ya puedes publicar|No se han encontrado problemas/.test(t)){cr='OK';break}if(/silencie|derechos de autor detectad|bloque/i.test(t)&&/Es posible que/.test(t)){cr='WARN';break}await S(1000)}
  window.__cr=cr||'pending';
  for(let k=0;k<2;k++){window.__btn('Siguiente').pop().click();await S(3500);}
  window.__btn('Programar')[0].click();await S(1500);
  const di=document.querySelector('input[placeholder="dd/mm/aaaa"]');di.click();await S(1200);
  let day=null;for(let k=0;k<3&&!day;k++){day=document.querySelector('[role=button][aria-label="'+dayLabel+'"]');if(!day){const h=[...document.querySelectorAll('h2')].find(e=>/\d{4}$/.test(e.innerText.trim()));let p=h;let nb=null;for(let j=0;j<6&&p&&!nb;j++){p=p.parentElement;const bs=[...p.querySelectorAll('[role=button]')].filter(b=>!b.getAttribute('aria-label'));if(bs.length>=2)nb=bs[bs.length-1];}if(!nb)return 'no next';nb.click();await S(900);}}
  if(!day)return 'noday';day.click();await S(800);
  const h=document.querySelector('input[aria-label=horas]');h.focus();h.select&&h.select();window.__rready=1;
  return 'ready '+window.__cr+' '+document.querySelector('input[placeholder="dd/mm/aaaa"]').value;
};
window.__reelFin=async function(){
  const S=window.__S;if(!window.__rready)return 'NOT READY';document.body.click();await S(500);
  const t=[...document.querySelectorAll('[aria-label="Introducción de la hora"], div')].find(e=>/^\s*20\s*:\s*30\s*Europe/.test(e.innerText||''));
  const hv=document.querySelector('input[aria-label=horas]'),mv=document.querySelector('input[aria-label=minutos]');
  if(!t)return 'TIME MISMATCH';
  window.__btn('Programar').pop().click();await S(9000);
  const d=document.querySelector('[role=dialog]');return d?d.innerText.slice(0,200):'nodialog';
};
