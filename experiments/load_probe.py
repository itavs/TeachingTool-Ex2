"""Opt-in isolated real HTTP attendance/vote probe. Never starts AI or uses demo DB."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import os
from pathlib import Path
import statistics
import sys
import threading
import time
from urllib.parse import urlencode
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory',required=True,help='Fresh isolated output/runtime directory, never demo storage.')
    args=parser.parse_args()
    directory=Path(args.directory).resolve()
    if (directory/'validation.sqlite3').exists():
        raise SystemExit('Refusing an existing validation database. Choose a fresh directory.')
    directory.mkdir(parents=True,exist_ok=True)
    os.environ['TEACHINGTOOL_VALIDATION_DIR']=str(directory)
    os.environ['DJANGO_SETTINGS_MODULE']='teachingtool.validation_settings'
    import django
    django.setup()
    from django.core.management import call_command
    from django.core.wsgi import get_wsgi_application
    from django.contrib.auth import get_user_model
    from django.test import Client
    from django.middleware.csrf import _get_new_csrf_string
    from django.db import connections
    from django.urls import reverse
    from django.utils import timezone
    from classroom.models import Course,Meeting,Membership,AttendanceRecord,PollVote
    from classroom.attendance import open_window,token_for
    from classroom.poll_services import create_manual_draft,publish

    call_command('migrate',verbosity=0,interactive=False)
    class Server(ThreadingMixIn,WSGIServer):
        daemon_threads=True
        request_queue_size=256
    class Quiet(WSGIRequestHandler):
        def log_message(self,*args): pass
    server=make_server('127.0.0.1',0,get_wsgi_application(),server_class=Server,handler_class=Quiet)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    port=server.server_port
    report={'scope':'Loopback threaded WSGI + SQLite HTTP server; not classroom Wi-Fi/device test',
        'conditions_declared_before_requests':{'each_size':[80,100],'no_unexpected_status':True,
            'p95_seconds_below':5,'max_seconds_below':10,'exact_unique_counts':True,
            'duplicate_attendance':'302 idempotent','duplicate_vote':'409 rejected'},'runs':[]}
    try:
        for n in [80,100]:
            course=Course.objects.create(code=f'LOAD-{n}',title='Synthetic load only')
            meeting=Meeting.objects.create(course=course,title='Isolated load',starts_at=timezone.now())
            teacher=get_user_model().objects.create_user(f'load_teacher_{n}')
            Membership.objects.create(user=teacher,course=course,role='lecturer')
            sessions=[]
            for i in range(n):
                user=get_user_model().objects.create_user(f'load_{n}_{i}')
                Membership.objects.create(user=user,course=course,role='student')
                client=Client();client.force_login(user)
                csrf=_get_new_csrf_string()
                sessions.append((client.cookies['sessionid'].value,csrf))
            window=open_window(meeting.pk,teacher);token=token_for(window,timezone.now())
            poll=create_manual_draft(meeting.pk,teacher,'opinion','en',{'question':'Choose a sample', 'options':['A','B','C','D']})
            publish(meeting.pk,poll.pk,teacher,poll.version)
            connections.close_all()
            def phase(path,values,expected):
                barrier=threading.Barrier(n)
                def send(i):
                    cookie,csrf=sessions[i]
                    conn=http.client.HTTPConnection('127.0.0.1',port,timeout=15)
                    barrier.wait(timeout=20);started=time.perf_counter()
                    try:
                        body=urlencode({**values,'csrfmiddlewaretoken':csrf})
                        conn.request('POST',path,body,{'Content-Type':'application/x-www-form-urlencoded',
                            'Cookie':f'sessionid={cookie}; csrftoken={csrf}'})
                        response=conn.getresponse();response.read()
                        return response.status,time.perf_counter()-started
                    except Exception as error:return type(error).__name__,time.perf_counter()-started
                    finally:conn.close()
                with ThreadPoolExecutor(max_workers=n) as pool:results=list(pool.map(send,range(n)))
                times=sorted(t for _,t in results);statuses={str(s):sum(v==s for v,_ in results) for s,_ in results}
                return {'statuses':statuses,'p50_seconds':statistics.median(times),
                    'p95_seconds':times[int(.95*(n-1))],'max_seconds':max(times),
                    'passed':all(s==expected for s,_ in results) and times[int(.95*(n-1))]<5 and max(times)<10}
            attendance_path=reverse('attendance-scan',args=[course.pk,meeting.pk,token])
            vote_path=reverse('poll-vote',args=[course.pk,meeting.pk,poll.pk])
            row={'users':n,'attendance':phase(attendance_path,{},302),'vote':phase(vote_path,{'option_index':2},302),
                 'duplicate_attendance':phase(attendance_path,{},302),'duplicate_vote':phase(vote_path,{'option_index':1},409)}
            row['attendance_count']=AttendanceRecord.objects.filter(meeting=meeting).count()
            row['vote_count']=PollVote.objects.filter(poll=poll).count()
            row['original_choices_preserved']=PollVote.objects.filter(poll=poll,option_index=2).count()==n
            row['passed']=all(row[k]['passed'] for k in ['attendance','vote','duplicate_attendance','duplicate_vote']) and row['attendance_count']==row['vote_count']==n and row['original_choices_preserved']
            report['runs'].append(row)
            print('Synthetic users:',n,'passed:',row['passed'],flush=True)
    finally:
        server.shutdown();server.server_close();connections.close_all()
        (directory/'results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not all(row['passed'] for row in report['runs']):raise SystemExit(1)


if __name__=='__main__':main()
