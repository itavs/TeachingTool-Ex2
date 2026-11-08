"use strict";
(() => {
    const config=document.getElementById("video-config");if(!config)return;
    const notice=document.getElementById("video-refresh");
    let timer,controller,clock,data=JSON.parse(document.getElementById("video-initial").textContent),seenAt=Date.now(),stopped=false;
    const set=(id,value)=>{document.getElementById(id).textContent=value;};
    const terminal=()=>["extracted","failed"].includes(data.status);
    function display(value){
        data=value;seenAt=Date.now();set("video-stage",data.stage_label);
        set("video-failure",data.error?`Failed stage: ${data.failed_stage}. ${data.error}`:"");
        set("video-audio",data.audio_seconds?`Extracted audio: ${data.audio_seconds.toFixed(2)} seconds. Temporary audio has been deleted.`:"");
        set("video-source",data.source_removed?"Uploaded MP4 removed by cleanup.":"");tick();
    }
    function tick(){
        const age=(Date.now()-seenAt)/1000;
        set("video-elapsed",(data.processing_seconds+(["validating","extracting"].includes(data.status)?age:0)).toFixed(1));
        set("video-wait",(data.waiting_seconds+(data.status==="queued"?age:0)).toFixed(1));
    }
    async function refresh(){
        if(document.hidden||controller||stopped)return;
        controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),8000);
        try{
            const response=await fetch(config.dataset.url,{cache:"no-store",signal:controller.signal});
            if(response.redirected||[403,404].includes(response.status)){stopped=true;throw new Error("Access changed. Reload and sign in again if needed.");}
            if(!response.ok)throw new Error("Could not refresh; displayed status may be outdated.");
            display(await response.json());notice.textContent=`Updated ${new Date().toLocaleTimeString()}.`;
        }catch(error){if(!document.hidden)notice.textContent=error.name==="AbortError"?"Refresh timed out; displayed status may be outdated.":error.message;}
        finally{clearTimeout(timeout);controller=null;if(!document.hidden&&!stopped&&!terminal())timer=setTimeout(refresh,3000);}
    }
    function resume(){clearInterval(clock);if(!document.hidden){tick();clock=setInterval(tick,1000);refresh();}}
    document.addEventListener("visibilitychange",()=>{clearTimeout(timer);clearInterval(clock);if(document.hidden){if(controller)controller.abort();}else resume();});
    display(data);resume();
})();
