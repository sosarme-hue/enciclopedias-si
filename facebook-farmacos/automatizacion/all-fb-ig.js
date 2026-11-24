(async(N)=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const vis=e=>e.getClientRects().length>0;
const P=el=>el[Object.keys(el).find(x=>x.startsWith('__reactProps'))]||{};
const pr=JSON.parse(await window.__escoPrep(N));if(!pr.img)throw 'noimg';
const d=window.__want;const [Y,MO,DA]=d.fecha.split('-').map(Number);const [H,MI]=d.hora.split(':').map(Number);
const ME=['January','February','March','April','May','June','July','August','September','October','November','December'];
const MES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
const days=()=>[...document.querySelectorAll('[aria-label]')].filter(vis).filter(x=>/^\w+day, \d+ \w+ \d{4}$/.test(x.getAttribute('aria-label')));
const dis=()=>[...document.querySelectorAll('input[placeholder="dd/mm/aaaa"]')].filter(vis);
const wantDs=[String(DA).padStart(2,'0')+'/'+String(MO).padStart(2,'0')+'/'+Y,DA+'/'+MO+'/'+Y,DA+' de '+MES[MO-1]+' de '+Y];
const sp=()=>[...document.querySelectorAll('[role=spinbutton]')].filter(vis);
async function setSpin(i,v){for(let g=0;g<70;g++){const el=sp()[i];const c=+el.getAttribute('aria-valuenow');if(c===v)return true;const key=c<v?'ArrowUp':'ArrowDown';P(el).onKeyDown({key,code:key,keyCode:key==='ArrowUp'?38:40,which:key==='ArrowUp'?38:40,type:'keydown',target:el,currentTarget:el,preventDefault(){},stopPropagation(){},nativeEvent:new KeyboardEvent('keydown',{key}),isDefaultPrevented(){return false},isPropagationStopped(){return false},persist(){}});await sl(40)}return false}
const nD=dis().length;
for(let q=0;q<nD;q++){
 if(wantDs.includes(dis()[q].value)){}else{
 const di=dis()[q];di.scrollIntoView({block:'center'});
 if(q>0||!days().length){document.body.click();await sl(300);di.focus();di.click();await sl(600)}
 let done=false;
 for(let k=0;k<14;k++){const ds=days();if(!ds.length)throw 'nocal'+q;const want=' '+DA+' '+ME[MO-1]+' '+Y;const t=ds.find(x=>x.getAttribute('aria-label').endsWith(want));if(t){t.click();await sl(500);done=true;break}
  const m=ds[10].getAttribute('aria-label').split(' ');const cur=(+m[3])*12+ME.indexOf(m[2]);const tg=Y*12+MO-1;
  let p=ds[0];let svgs=null;for(let i=0;i<14;i++){p=p.parentElement;const s=[...p.querySelectorAll('svg')].filter(vis);if(s.length){svgs=s;break}}
  const btn=x=>{let c=x;while(c&&!P(c).onClick)c=c.parentElement;return c};(tg>cur?btn(svgs[svgs.length-1]):btn(svgs[0])).click();await sl(450)}
 if(!done)throw 'nodate'+q;}
 await setSpin(2*q,H);await setSpin(2*q+1,MI);await sl(300);
}
const v=sp().map(e=>+e.getAttribute('aria-valuenow'));const dv=dis().map(i=>i.value);
const img=/\d+ x \d+/.exec(document.body.innerText)?.[0];
const okd=dv.length>=1&&dv.every(x=>wantDs.includes(x));const okt=v.length===2*dv.length&&v.every((x,i)=>x===(i%2?MI:H));
if(!(okd&&okt&&img))throw 'mismatch '+dv.join(',')+' '+v.join(':');
const b=[...document.querySelectorAll('[role=button],button')].filter(vis).find(e=>e.innerText.trim()==='Programar');b.click();
for(let i=0;i<80;i++){await sl(250);const t=document.body.innerText;if(t.includes('Se ha programado la publicaci')||t.includes('Ahorra tiempo')||t.includes('Hay más publicaciones')){await sl(2500);return 'scheduled '+N+' x'+dv.length}}
throw 'noconfirm'})
