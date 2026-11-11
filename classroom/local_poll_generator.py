"""PollGenerator implementation using only the installed local Qwen runtime."""
import json,os,queue,subprocess,tempfile,threading,time
from pathlib import Path
from django.conf import settings
from .poll_generation import GenerationUnavailable
from .poll_contract import validate_generated
from .process_tree import ProcessTree
from .summary_contract import MODEL,WEIGHTS,MANIFEST_SHA256

ERRORS={
    'unavailable':'The installed local model is unavailable. No draft was saved. Your learning material remains in the form.',
    'busy':'The local model is busy with another task. No draft was saved. Please retry when it finishes.',
    'invalid':'The model output did not pass the draft checks. No draft was saved. Review your material and retry explicitly.',
    'failed':'Local generation failed. No draft was saved. Your learning material remains in the form.',
    'timeout':'Local generation reached its time limit. No draft was saved. Your learning material remains in the form.'}


class LocalPollGenerator:
    def generate(self,material,kind,language):
        if language!='en':raise GenerationUnavailable('Automatic draft generation is currently available in English only. Hebrew polls can still be edited, published and answered.')
        if kind not in ('comprehension','opinion') or not isinstance(material,str) or not material.strip() or len(material)>6000:
            raise GenerationUnavailable('Enter supported poll settings and 1–6000 characters of learning material.')
        runtime=Path(settings.LOCAL_ASR_PYTHON);binary=Path(settings.LOCAL_SUMMARY_OLLAMA)
        if not runtime.is_file() or not binary.is_file():raise GenerationUnavailable(ERRORS['unavailable'])
        root=settings.LOCAL_DIR/'poll-generation';root.mkdir(exist_ok=True)
        self.last_metadata=None
        with tempfile.TemporaryDirectory(dir=root) as directory:
            source=Path(directory)/'input.json';output=Path(directory)/'output.json'
            source.write_text(json.dumps({'material':material,'kind':kind},ensure_ascii=False),encoding='utf-8')
            deadline=time.monotonic()+120
            command=[str(runtime),'-u',str(settings.BASE_DIR/'classroom/local_poll_runner.py'),
                '--input',str(source),'--output',str(output),'--ollama',str(binary),
                '--models',str(settings.LOCAL_SUMMARY_MODELS),'--deadline',str(deadline),'--parent-pid',str(os.getpid())]
            tree=ProcessTree();process=None
            try:
                process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
                tree.attach(process.pid);events=queue.Queue(maxsize=10)
                def reader():
                    try:
                        for line in process.stdout:
                            if len(line)>8192:break
                            events.put(line)
                    finally:events.put(None)
                threading.Thread(target=reader,daemon=True).start();success=False
                while True:
                    if time.monotonic()>=deadline:raise GenerationUnavailable(ERRORS['timeout'])
                    try:line=events.get(timeout=.2)
                    except queue.Empty:continue
                    if line is None:break
                    event=json.loads(line)
                    if event.get('result')=='failed':raise GenerationUnavailable(ERRORS.get(event.get('code'),ERRORS['failed']))
                    success=event.get('result')=='ok'
                process.wait(timeout=max(.1,deadline-time.monotonic()))
                if not success or process.returncode:raise GenerationUnavailable(ERRORS['failed'])
                if not output.is_file() or output.stat().st_size>20000:raise ValueError('Invalid output size')
                result=json.loads(output.read_text(encoding='utf-8'));validate_generated(kind,result['draft'])
                metadata=result['metadata']
                if metadata.get('model')!=MODEL or metadata.get('weights_digest')!=WEIGHTS or metadata.get('manifest_sha256')!=MANIFEST_SHA256:
                    raise ValueError('Unexpected local model identity')
                self.last_metadata=metadata;return result['draft']
            except GenerationUnavailable:raise
            except (ValueError,KeyError,TypeError):raise GenerationUnavailable(ERRORS['invalid']) from None
            except Exception:raise GenerationUnavailable(ERRORS['failed']) from None
            finally:
                tree.close()
                if process is not None:
                    if process.poll() is None:process.kill()
                    process.wait(timeout=3);process.stdout.close()
