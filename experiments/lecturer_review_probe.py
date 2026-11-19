"""Explicit real local inference, not a software test. No downloads/cloud/DB writes."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True,help='UTF-8 JSON with segments [{start,end,text}] and language en/he.')
    parser.add_argument('--output',required=True,help='New report file; never overwrites evidence.')
    args=parser.parse_args()
    destination=Path(args.output).resolve()
    if destination.exists():raise SystemExit('Choose a new output filename.')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE','teachingtool.settings')
    import django
    django.setup()
    from django.conf import settings
    from classroom.local_summarizer import LocalQwenLecturerReviewer
    import uuid
    work=Path(settings.VIDEO_STORAGE_ROOT)/str(uuid.uuid4())
    work.mkdir(parents=True)
    source=json.loads(Path(args.input).read_text(encoding='utf-8'))
    started=time.perf_counter()
    try:
        result=LocalQwenLecturerReviewer().review(source['segments'],source['language'],
            work_dir=work,deadline=time.monotonic()+120,on_event=lambda event:None,on_tick=lambda:None)
        report={'success':True,'wall_seconds':time.perf_counter()-started,'result':result}
    except Exception as error:
        report={'success':False,'wall_seconds':time.perf_counter()-started,
            'error_type':type(error).__name__,'code':getattr(error,'code','invalid_output'),
            'diagnostic':getattr(error,'diagnostic','')}
    finally:
        # The adapter removes private IPC. No source/demo evidence is deleted here.
        if not any(work.iterdir()):work.rmdir()
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    print('Saved local inference report; success:',report['success'])


if __name__=='__main__':main()
