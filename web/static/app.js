const $ = id => document.getElementById(id);
let file, original, result, ready = false, busy = false, current, timer;
const messages = {uploading:'Subiendo tu imagen…',submitting:'Enviando la solicitud de mejora…',tracking:'La IA está trabajando en tu imagen. Puedes volver a consultar más tarde.',succeeded:'Tu imagen está lista. Abre el resultado y guarda una copia; el enlace es temporal.',failed:'La tarea no pudo completarse. Revisa el historial del proveedor antes de repetirla.',uncertain:'El envío no pudo confirmarse. No se reenviará: revisa el historial de RunningHub antes de iniciar otra tarea.'};
$('access').value = sessionStorage.getItem('studio-access') || '';
function status(text){$('status').textContent=text;}
function controls(){ $('enhance').disabled = !ready || !file || busy || !$('access').value.trim(); $('change').disabled=busy; $('file').disabled=busy; document.querySelectorAll('[name=quality]').forEach(e=>e.disabled=busy); }
async function api(path,options={}){const response=await fetch(path,{...options,headers:{Authorization:'Bearer '+$('access').value.trim(),...options.headers}});let data;try{data=await response.json();}catch{throw Error('No se recibió una respuesta válida. Consulta el estado antes de repetir.');}if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:'No se pudo completar la solicitud.');return data;}
async function choose(candidate){
 if(busy || !candidate)return;
 if(!['image/png','image/jpeg','image/webp'].includes(candidate.type)||candidate.size>10*1024*1024){status('Elige un JPG, PNG o WebP de hasta 10 MiB.');return;}
 const url=URL.createObjectURL(candidate); const img=new Image();img.src=url;
 try{await img.decode();if(img.naturalWidth*img.naturalHeight>40000000||Math.max(img.naturalWidth,img.naturalHeight)>32768)throw Error();}
 catch{URL.revokeObjectURL(url);status('No se puede abrir esta imagen o supera 40 megapíxeles.');return;}
 if(original)URL.revokeObjectURL(original);original=url;file=candidate;result=null;current=null;
 $('image').src=url;$('filename').textContent=candidate.name;$('filesize').textContent=`${img.naturalWidth} × ${img.naturalHeight} · ${(candidate.size/1048576).toFixed(1)} MiB`;
 $('dropzone').hidden=true;$('preview').hidden=false;$('change').hidden=false;$('result-tabs').hidden=true;$('view-label').textContent='01 / TU IMAGEN';
 status(ready?'Lista para ampliar.':'Puedes revisar tu imagen. El procesamiento aún no está habilitado.');controls();
}
$('file').addEventListener('change',e=>choose(e.target.files[0]));$('change').onclick=()=>$('file').click();
$('dropzone').ondragover=e=>{e.preventDefault();$('dropzone').classList.add('drag');};$('dropzone').ondragleave=()=>$('dropzone').classList.remove('drag');$('dropzone').ondrop=e=>{e.preventDefault();$('dropzone').classList.remove('drag');choose(e.dataTransfer.files[0]);};
$('access').oninput=controls;
function show(job){current=job.id;busy=['uploading','submitting','tracking','uncertain'].includes(job.state);status((messages[job.state]||'Consultando…')+(job.state==='uncertain'?' Identificador para recuperar la tarea: '+job.id:''));$('refresh').hidden=!busy;controls();if(job.state==='succeeded' && job.result){result=job.result;$('image').src=result;$('preview').hidden=false;$('dropzone').hidden=true;$('result-tabs').hidden=false;$('original-tab').disabled=!original;$('download').href=result;$('view-label').textContent='RESULTADO / '+job.quality.toUpperCase();}clearTimeout(timer);if(['uploading','submitting','tracking'].includes(job.state))timer=setTimeout(poll,5000);}
async function poll(){if(!current)return;try{show(await api('/api/jobs/'+current));}catch(e){status(e.message);$('refresh').hidden=false;}}
$('refresh').onclick=poll;
$('connect').onclick=async()=>{sessionStorage.setItem('studio-access',$('access').value.trim());try{const jobs=await api('/api/jobs');const active=jobs.find(j=>['uploading','submitting','tracking','uncertain'].includes(j.state));if(active){show(active);poll();}else if(jobs.length){show(jobs[0]);}else{busy=false;controls();status('Acceso confirmado. Elige una imagen para empezar.');}}catch(e){status(e.message);}};
$('enhance').onclick=async()=>{
 if(!file||busy)return;busy=true;controls();result=null;$('result-tabs').hidden=true;status('Subiendo tu imagen…');
 const id=crypto.randomUUID();current=id;sessionStorage.setItem('studio-task',id);sessionStorage.setItem('studio-access',$('access').value.trim());
 try{show(await api('/api/jobs?quality='+document.querySelector('[name=quality]:checked').value,{method:'POST',headers:{'Content-Type':file.type,'Idempotency-Key':id},body:file}));}
 catch(e){status(e.message+' Usa «Consultar mis tareas» para comprobar si se registró.');$('refresh').hidden=false;/* retain busy until journal has been checked */}
};
$('original-tab').onclick=()=>{if(original){$('image').src=original;$('view-label').textContent='ORIGINAL';}};
$('result-tab').onclick=()=>{if(result){$('image').src=result;$('view-label').textContent='RESULTADO';}};
$('image').onerror=()=>status('No se pudo mostrar la imagen. Si es un resultado anterior, su enlace puede haber caducado.');
fetch('/api/config').then(r=>r.json()).then(c=>{ready=c.ready;status(ready?'Elige una imagen para empezar.':'Vista previa disponible. El procesamiento aún no está habilitado.');controls();if(sessionStorage.getItem('studio-task')&&$('access').value){current=sessionStorage.getItem('studio-task');poll();}}).catch(()=>status('No se pudo conectar con el estudio. Recarga la página.'));
