// Pure logic tests, not a browser/phone rendering test. No live HTTP calls.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

function harness(data) {
    class Element {
        constructor(value='') { this.textContent=value; this.children=[]; }
        append(...nodes) { this.children.push(...nodes); }
        replaceChildren(...nodes) { this.children=nodes; }
    }
    const elements=new Map(['poll-refresh-status','poll-status','poll-results','poll-respondents'].map(id=>[id,new Element(id==='poll-status'?'active':'')]));
    elements.set('poll-config',{dataset:{url:'/fake-poll-state/'}});
    const timers=new Map(),listeners={};let serial=0,calls=0;
    const document={hidden:false,getElementById:id=>elements.get(id),createElement:()=>new Element(),addEventListener:(event,fn)=>listeners[event]=fn};
    const context={document,Date,AbortController,
        setTimeout:(fn,delay)=>{const id=++serial;timers.set(id,{fn,delay});return id;},clearTimeout:id=>timers.delete(id),
        fetch:async()=>{calls++;return {ok:true,status:200,redirected:false,json:async()=>data};}};
    vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/js/polls.js'),'utf8'),context);
    return {document,elements,timers,listeners,calls:()=>calls,settle:()=>new Promise(resolve=>setImmediate(resolve))};
}

test('lecturer results render counts with safe text, pause hidden and resume visible',async()=>{
    const h=harness({status:'active',show_results:true,respondent_count:2,results:[{text:'<script>example</script>',count:1,percent:50}]});
    await h.settle();
    assert.equal(h.elements.get('poll-respondents').textContent,'Responses: 2');
    const option=h.elements.get('poll-results').children[0].children[0];
    assert.equal(option.textContent,'<script>example</script>');
    assert.equal(option.children.length,0);
    assert.equal([...h.timers.values()][0].delay,5000);
    h.document.hidden=true;h.listeners.visibilitychange();assert.equal(h.timers.size,0);
    h.document.hidden=false;h.listeners.visibilitychange();await h.settle();assert.equal(h.calls(),2);
});

test('a competing state transition requires reload and stops stale action polling',async()=>{
    const h=harness({status:'closed',show_results:true,results:[],respondent_count:0});
    await h.settle();
    assert.match(h.elements.get('poll-refresh-status').textContent,/status changed/);
    assert.equal(h.timers.size,0);
    assert.equal(h.elements.get('poll-results').children.length,0);
});
