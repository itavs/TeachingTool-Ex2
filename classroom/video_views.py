from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render,redirect
from .attendance import CourseAccessError
from .models import VideoJob,Membership
from .participation_views import scoped,context
from .video_forms import VideoUploadForm
from .video_jobs import save_upload,owned_job,payload,recover_jobs


@scoped(Membership.Role.LECTURER,('GET','POST'))
def video_list(request,meeting,membership):
    form=VideoUploadForm(request.POST if request.method=='POST' else None,request.FILES if request.method=='POST' else None)
    status=200
    if request.method=='POST':
        status=400
        if getattr(request,'video_upload_error',None):
            form.is_valid()
            form.add_error('video',request.video_upload_error);status=413
        elif len(request.FILES.getlist('video'))!=1:
            form.is_valid();form.add_error('video','Upload exactly one MP4 video.')
        elif form.is_valid():
            try:
                job=save_upload(meeting.pk,request.user,form.cleaned_data['video'])
                return redirect('video-detail',course_id=meeting.course_id,meeting_id=meeting.pk,job_id=job.pk)
            except ValidationError as error:
                form.add_error('video',error)
            except OSError:
                form.add_error(None,'The upload could not be stored. Please try again.');status=503
    recover_jobs()
    jobs=[payload(j) for j in VideoJob.objects.filter(meeting=meeting,owner=request.user)]
    return render(request,'classroom/video_list.html',{**context(meeting,membership),'form':form,'jobs':jobs},status=status)


@scoped(Membership.Role.LECTURER)
def video_detail(request,meeting,membership,job_id):
    job=owned_job(meeting.pk,job_id,request.user)
    return render(request,'classroom/video_detail.html',{**context(meeting,membership),'job':payload(job)})


@scoped(Membership.Role.LECTURER)
def video_state(request,meeting,membership,job_id):
    job=owned_job(meeting.pk,job_id,request.user)
    return JsonResponse(payload(job))
