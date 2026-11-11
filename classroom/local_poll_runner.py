"""Isolated pinned local Qwen poll generator. No changes to video AI engines."""
import argparse,json,os,socket,subprocess,sys,threading,time
from pathlib import Path
import urllib.request


def emit(**value):print(json.dumps(value),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for key in ['input','output','ollama','models']:parser.add_argument('--'+key,required=True)
    parser.add_argument('--deadline',type=float,required=True)
    parser.add_argument('--parent-pid',type=int,required=True)
    args=parser.parse_args();sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
    import psutil
    from classroom.summary_contract import MODEL,verify_local_model
    from classroom.poll_contract import prompt,schema,validate_generated
    from classroom.process_lock import exclusive_lock,WorkerBusy
    parent=psutil.Process(args.parent_pid);server=None;cleaning=threading.Lock()
    def cleanup():
        with cleaning:
            if server is not None:
                try:
                    owner=psutil.Process(server.pid);children=owner.children(recursive=True)
                    for process in reversed(children+[owner]):
                        try:process.kill()
                        except psutil.Error:pass
                    psutil.wait_procs(children+[owner],timeout=2)
                except psutil.Error:pass
    def watchdog():
        while True:
            if time.monotonic()>=args.deadline or not parent.is_running():cleanup();os._exit(3)
            time.sleep(.25)
    threading.Thread(target=watchdog,daemon=True).start()
    try:
        identity=verify_local_model(args.models)
        data=json.loads(Path(args.input).read_text(encoding='utf-8'))
        lock=Path(__file__).resolve().parent.parent/'.local/videos/.decoder.lock'
        with exclusive_lock(lock):
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
            host=f'127.0.0.1:{port}'
            env={**os.environ,'OLLAMA_HOST':host,'OLLAMA_MODELS':args.models,'OLLAMA_NO_CLOUD':'1',
                 'OLLAMA_NUM_PARALLEL':'1','OLLAMA_MAX_LOADED_MODELS':'1','OLLAMA_CONTEXT_LENGTH':'8192'}
            server=subprocess.Popen([args.ollama,'serve'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            http=urllib.request.build_opener(urllib.request.ProxyHandler({}));base='http://'+host
            while True:
                if server.poll() is not None:emit(result='failed',code='unavailable');return 1
                try:
                    with http.open(base+'/api/version',timeout=1) as response:version=json.load(response)['version']
                    break
                except (OSError,ValueError):time.sleep(.1)
            if version!='0.40.14':emit(result='failed',code='unavailable');return 1
            started=time.perf_counter()
            request=urllib.request.Request(base+'/api/generate',data=json.dumps({'model':MODEL,
                'prompt':prompt(data['material'],data['kind']),'format':schema(data['kind']),
                'think':False,'stream':False,'keep_alive':0,
                'options':{'temperature':.1,'seed':42,'num_ctx':8192,'num_predict':768}}).encode('utf-8'),
                headers={'Content-Type':'application/json'})
            with http.open(request,timeout=max(.1,args.deadline-time.monotonic())) as response:generated=json.load(response)
            if generated.get('done_reason')!='stop':emit(result='failed',code='invalid');return 1
            value=validate_generated(data['kind'],json.loads(generated['response']))
            metadata={**identity,'ollama_version':version,'prompt_version':'poll-en-v2','generation_seconds':time.perf_counter()-started}
            Path(args.output).write_text(json.dumps({'draft':value,'metadata':metadata},ensure_ascii=False),encoding='utf-8')
            emit(result='ok');return 0
    except WorkerBusy:emit(result='failed',code='busy');return 1
    except (FileNotFoundError,OSError):emit(result='failed',code='unavailable');return 1
    except (ValueError,KeyError,TypeError):emit(result='failed',code='invalid');return 1
    except Exception as error:emit(result='failed',code='failed',exception_type=type(error).__name__);return 1
    finally:cleanup()


if __name__=='__main__':raise SystemExit(main())
