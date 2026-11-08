// Logic-only polling tests: no browser, uploads or AI calls.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');

function harness(data){
    const ids=['video-refresh','video-stage','video-wait','video-elapsed','video-failure','video-audio','video-source','video-asr-progress','video-language','video-transcript-expired','video-transcript-link'];
    const elements=new Map(ids.map(id=>[id,{textContent:''}]));
    elements.set('video-config',{dataset:{url:'/fake-video-state/'}});
    elements.set('video-initial',{textContent:JSON.stringify(data)});
    const timers=new Map(),listeners={};let counter=0,calls=0;
    const document={hidden:false,getElementById:id=>elements.get(id),addEventListener:(name,fn)=>listeners[name]=fn};
    vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/js/videos.js'),'utf8'),{
        document,Date,JSON,AbortController,
        setTimeout:(fn,delay)=>{let id=++counter;timers.set(id,{fn,delay});return id;},clearTimeout:id=>timers.delete(id),
        setInterval:()=>++counter,clearInterval:()=>{},
        fetch:async()=>{calls++;return {ok:true,redirected:false,status:200,json:async()=>data};},
    });
    return {elements,timers,listeners,document,calls:()=>calls,settle:()=>new Promise(resolve=>setImmediate(resolve))};
}

test('extraction success displays audio-only completion and stops polling',async()=>{
    const h=harness({status:'extracted',stage_label:'Audio extraction completed',processing_seconds:2,waiting_seconds:4,audio_seconds:1.2,error:'',source_removed:false});
    await h.settle();
    assert.equal(h.elements.get('video-stage').textContent,'Audio extraction completed');
    assert.match(h.elements.get('video-audio').textContent,/Temporary audio has been deleted/);
    assert.equal(h.elements.get('video-elapsed').textContent,'2.0');
    assert.equal(h.timers.size,0);
});

test('queued tasks keep processing time zero and pause hidden-page reads',async()=>{
    const h=harness({status:'queued',stage_label:'Waiting for worker',processing_seconds:0,waiting_seconds:12,audio_seconds:null,error:'',source_removed:false});
    await h.settle();
    assert.equal(h.elements.get('video-elapsed').textContent,'0.0');
    assert.equal([...h.timers.values()][0].delay,3000);
    h.document.hidden=true;h.listeners.visibilitychange();assert.equal(h.timers.size,0);
    h.document.hidden=false;h.listeners.visibilitychange();await h.settle();assert.equal(h.calls(),2);
});

test('failed task shows the actual failed stage as text without a success claim',async()=>{
    const h=harness({status:'failed',stage_label:'Processing failed',processing_seconds:60,waiting_seconds:5,failed_stage:'Checking video',error:'<script>invalid MP4</script>',audio_seconds:null,source_removed:true});
    await h.settle();
    assert.equal(h.elements.get('video-failure').textContent,'Failed stage: Checking video. <script>invalid MP4</script>');
    assert.equal(h.elements.get('video-audio').textContent,'');
    assert.match(h.elements.get('video-source').textContent,/removed/);
});

test('ASR keeps audio while processing and reveals the full-transcript link on success',async()=>{
    const active=harness({status:'transcribing',stage_label:'Transcribing speech locally',processing_seconds:20,waiting_seconds:3,audio_seconds:56,transcribed_until:10,audio_removed:false,error:''});
    await active.settle();
    assert.match(active.elements.get('video-audio').textContent,/retained temporarily/);
    assert.match(active.elements.get('video-asr-progress').textContent,/10.0/);
    assert.equal(active.elements.get('video-transcript-link').hidden,true);
    const ready=harness({status:'transcribed',stage_label:'Transcription completed',processing_seconds:30,waiting_seconds:3,audio_seconds:56,audio_removed:true,transcript_available:true,detected_language:'he',error:''});
    await ready.settle();
    assert.equal(ready.elements.get('video-transcript-link').hidden,false);
    assert.match(ready.elements.get('video-language').textContent,/he/);
    assert.equal(ready.timers.size,0);
});

test('expired transcript link is hidden even though processing completed',async()=>{
    const h=harness({status:'transcribed',stage_label:'Transcription completed',processing_seconds:30,waiting_seconds:3,audio_seconds:56,audio_removed:true,transcript_available:false,transcript_expired:true,error:''});
    await h.settle();
    assert.equal(h.elements.get('video-transcript-link').hidden,true);
    assert.match(h.elements.get('video-transcript-expired').textContent,/expired/);
});
