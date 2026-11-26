window.__S=ms=>new Promise(r=>setTimeout(r,ms));
window.__get=(p)=>new Promise(res=>{const w=window.open('','clsimg');const h=e=>{if(e.data&&e.data.got===p){removeEventListener('message',h);res(e.data)}};addEventListener('message',h);w.postMessage({get:p},'*')});
if(!window.__patched){const oc=HTMLInputElement.prototype.click;HTMLInputElement.prototype.click=function(){if(this.type==='file'&&window.__wantFile){window.__inp=this;return}return oc.call(this)};window.__patched=1}
window.__MES=['January','February','March','April','May','June','July','August','September','October','November','December'];
window.__DOW=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
window.__clean=t=>t.replace(/👉[^\n]*https?:\/\/\S+/g,'👉 Biografía completa en Classicapedia, la enciclopedia de la música clásica 🔎').replace(/https?:\/\/\S+/g,'');
window.__prep=async(o)=>{const S=window.__S;const log=[];
 for(let i=0;i<30&&![...document.querySelectorAll('div[role=button],button')].some(b=>b.innerText.trim()==='Añadir foto o vídeo');i++)await S(500);
 const cb=[...document.querySelectorAll('[role=combobox],div[role=button]')].find(e=>/Compositores de Música Clásica y/.test(e.innerText));
 if(cb){cb.click();await S(900);const op=[...document.querySelectorAll('[role=option]')].find(e=>/composers_conductors_soloists/.test(e.innerText));if(op)op.click();await S(700);document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));await S(700);}
 if(document.querySelector('input[role=switch][aria-label="Personaliza la publicación para Facebook e Instagram"]'))return 'IG still on';
 const r=await window.__get(o.path);if(!r.ok)return 'fetchfail';
 window.__inp=null;window.__wantFile=1;[...document.querySelectorAll('div[role=button],button')].find(b=>b.innerText.trim()==='Añadir foto o vídeo').click();
 for(let i=0;i<20&&!window.__inp;i++)await S(200);window.__wantFile=0;const inp=window.__inp;if(!inp)return 'noinput';await S(1000);
 const dt=new DataTransfer();dt.items.add(new File([r.v],o.name,{type:o.type,lastModified:Date.now()}));inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));inp.dispatchEvent(new Event('input',{bubbles:true}));
 let ok=false;for(let k=0;k<40;k++){await S(500);if(/\d+ x \d+/.test((document.body.innerText.match(/Contenido multimedia[\s\S]{0,80}/)||[''])[0])){ok=true;break}}
 if(!ok){inp.dispatchEvent(new Event('change',{bubbles:true}));inp.dispatchEvent(new Event('input',{bubbles:true}));for(let k=0;k<20;k++){await S(500);if(/\d+ x \d+/.test((document.body.innerText.match(/Contenido multimedia[\s\S]{0,80}/)||[''])[0])){ok=true;break}}}
 if(!ok)return 'media not shown';
 const ed=[...document.querySelectorAll('[contenteditable=true]')].filter(e=>e.getBoundingClientRect().height>0).pop();ed.focus();const d2=new DataTransfer();d2.setData('text/plain',window.__clean(o.text));ed.dispatchEvent(new ClipboardEvent('paste',{clipboardData:d2,bubbles:true,cancelable:true}));await S(1500);
 if(ed.innerText.length<100)return 'text fail';
 const sw=document.querySelector('input[role=switch][aria-label="Definir fecha y hora"]');if(!sw.checked)sw.click();await S(1200);
 const di=document.querySelector('input[placeholder="dd/mm/aaaa"]');di.click();di.focus();await S(800);
 const [Y,M,D]=o.date.split('-').map(Number);const dd=new Date(Y,M-1,D);const lab=`${window.__DOW[dd.getDay()]}, ${D} ${window.__MES[M-1]} ${Y}`;
 for(let k=0;k<3;k++){const c=document.querySelector(`[role=button][aria-label="${lab}"]`);if(c){c.click();break}
   const hdr=[...document.querySelectorAll('h2')].find(e=>/^(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre) \d{4}$/.test(e.innerText.trim()));
   let p=hdr;let nxt=null;for(let up=0;up<6&&p&&!nxt;up++){p=p.parentElement;const bs=[...p.querySelectorAll('[role=button]')].filter(b=>!b.getAttribute('aria-label'));if(bs.length>=2)nxt=bs[bs.length-1]}
   if(!nxt)return 'no next month';nxt.click();await S(700);}
 await S(700);const want=`${String(D).padStart(2,'0')}/${String(M).padStart(2,'0')}/${Y}`;if(di.value!==want)return 'date fail '+di.value+' want '+want;
 document.querySelector('input[aria-label=horas]').focus();return 'ready';};
window.__fin=async()=>{const S=window.__S;const h=document.querySelector('input[aria-label=horas]').getAttribute('aria-valuenow'),m=document.querySelector('input[aria-label=minutos]').getAttribute('aria-valuenow');
 if(/Quedan \d+ enlaces/.test(document.body.innerText))return 'LINK WARNING';
 const med=/\d+ x \d+/.test((document.body.innerText.match(/Contenido multimedia[\s\S]{0,80}/)||[''])[0]);if(!med)return 'media lost';
 const b=[...document.querySelectorAll('div[role=button],button')].find(x=>x.innerText.trim()==='Programar');if(!b||b.getAttribute('aria-disabled')==='true')return 'btn disabled';
 b.click();for(let k=0;k<30;k++){await S(500);if(!/Crear publicación/.test(document.title+document.body.innerText.slice(0,300)))return 'done '+h+':'+m+' '+location.pathname;}
 return 'clicked '+h+':'+m+' still '+location.pathname+' :: '+document.body.innerText.slice(0,200).replace(/\n/g,' ');};
'def ok';
