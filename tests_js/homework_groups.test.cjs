// Status polling only; no visual browser check or model inference.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
function harness(reply, status=200) {
  const elements=new Map(['group-progress','group-refresh','group-status-1','group-comparison-1','group-reason-1','group-elapsed-1'].map(id=>[id,{textContent:''}]));
  elements.set('group-config',{dataset:{url:'/private-group-state/',pending:'true'}});
  const timers=new Map(),events={};let serial=0,calls=0;
  const document={hidden:false,getElementById:id=>elements.get(id),addEventListener:(name,fn)=>events[name]=fn};
  const context={document,AbortController,
    setTimeout:(fn,delay)=>{const id=++serial;timers.set(id,{fn,delay});return id;},clearTimeout:id=>timers.delete(id),
    fetch:async(url,options)=>{calls++;assert.equal(url,'/private-group-state/');assert.equal(options.credentials,'same-origin');assert.equal(options.method,undefined);return {ok:status===200,status,redirected:false,json:async()=>reply};}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/js/homework_groups.js'),'utf8'),context);
  return {document,elements,timers,events,calls:()=>calls,settle:()=>new Promise(resolve=>setImmediate(resolve))};
}
const data={rows:[{id:1,label:'Waiting for shared AI resource',comparison:'Pending',reason:'<script>text only</script>',elapsed:0}],total:2,finished:0,ready:0,partial:0,failed:0,pending:true};
test('safe text status reads update counts, pause hidden and resume visible',async()=>{
  const h=harness(data);await h.settle();
  assert.equal(h.elements.get('group-reason-1').textContent,'<script>text only</script>');
  assert.equal(h.elements.get('group-status-1').textContent,'Waiting for shared AI resource');
  assert.equal([...h.timers.values()][0].delay,5000);
  h.document.hidden=true;h.events.visibilitychange();assert.equal(h.timers.size,0);
  h.document.hidden=false;h.events.visibilitychange();await h.settle();assert.equal(h.calls(),2);
});
test('finished processing stops polling and still requires separate publication',async()=>{
  const h=harness({...data,pending:false,finished:2,ready:1,partial:1,failed:1});await h.settle();
  assert.equal(h.timers.size,0);
  assert.match(h.elements.get('group-refresh').textContent,/publish each draft separately/);
});
test('access loss stops status polling without requesting generation',async()=>{
  const h=harness({},403);await h.settle();assert.equal(h.timers.size,0);
  assert.match(h.elements.get('group-refresh').textContent,/No new processing/);
});
