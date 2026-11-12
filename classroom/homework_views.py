"""Submitted-work foundation only: no review request or AI-generation endpoints."""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .attendance import CourseAccessError
from .models import Membership
from .participation_views import scoped, context
from .homework_forms import AssignmentForm, SubmissionForm, FeedbackEditForm, FeedbackPublishForm
from . import homework_services as services
from . import homework_review as reviews


@scoped()
def assignment_list(request, meeting, membership):
    return render(request, "classroom/homework_list.html", {**context(meeting, membership),
                  "assignments": meeting.homework_assignments.all()})


@scoped(Membership.Role.LECTURER, methods=("GET", "POST"))
def assignment_create(request, meeting, membership):
    form = AssignmentForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        assignment = services.create_assignment(meeting, request.user, form.cleaned_data)
        messages.success(request, "Assignment created.")
        return redirect("homework-detail", course_id=meeting.course_id, meeting_id=meeting.pk, assignment_id=assignment.pk)
    return render(request, "classroom/homework_form.html", {**context(meeting, membership), "form": form})


@scoped(methods=("GET", "POST"))
def assignment_detail(request, meeting, membership, assignment_id):
    assignment = services.assignment_for(meeting, assignment_id)
    is_student = membership.role == Membership.Role.STUDENT
    if request.method == "POST" and not is_student:
        raise CourseAccessError(403)
    form = SubmissionForm(request.POST if request.method == "POST" else None) if is_student else None
    if request.method == "POST" and form.is_valid():
        submission = services.submit_version(meeting, assignment.pk, request.user, form.cleaned_data["text"])
        messages.success(request, f"Your work was saved. Version {submission.version_number} — Submitted.")
        return redirect("homework-submission", course_id=meeting.course_id, meeting_id=meeting.pk,
                        assignment_id=assignment.pk, submission_id=submission.pk)
    versions = assignment.submissions.select_related("student")
    if is_student:
        versions = versions.filter(student=request.user)
    return render(request, "classroom/homework_detail.html", {**context(meeting, membership),
                  "assignment": assignment, "form": form, "versions": versions})


@scoped()
def submission_detail(request, meeting, membership, assignment_id, submission_id):
    assignment = services.assignment_for(meeting, assignment_id)
    submission = services.submission_for(assignment, submission_id, request.user, membership)
    available, reason = reviews.availability(assignment)
    jobs=submission.review_jobs.select_related('draft')
    return render(request, "classroom/homework_submission.html", {**context(meeting, membership),
                  "assignment": assignment, "submission": submission, 'feedback_available':available,
                  'feedback_reason':reason, 'published_feedback':reviews.published_feedback(submission),
                  'jobs':jobs if membership.role=='lecturer' else [],
                  'request_states':[job.display_status for job in jobs]})


@scoped(methods=('POST',))
def review_request(request,meeting,membership,assignment_id,submission_id):
    assignment=services.assignment_for(meeting,assignment_id)
    submission=services.submission_for(assignment,submission_id,request.user,membership)
    try:
        reviews.request_review(submission,request.user)
    except reviews.ReviewError as error:
        messages.error(request,str(error))
    else:
        messages.success(request,f'Feedback requested for Version {submission.version_number}. Lecturer publication is required.')
    return redirect('homework-submission',course_id=meeting.course_id,meeting_id=meeting.pk,assignment_id=assignment.pk,submission_id=submission.pk)


@scoped(Membership.Role.LECTURER,methods=('GET','POST'))
def review_detail(request,meeting,membership,job_id):
    job=reviews.owned_job(meeting,job_id,request.user)
    draft=getattr(job,'draft',None)
    form=FeedbackEditForm(request.POST if request.method=='POST' else None,
        initial={'version':draft.version,'individual_text':draft.individual_text,'comparison_text':draft.comparison_text} if draft else {})
    if job.comparison_status not in ['compared','no_difference']:
        from django.forms import HiddenInput
        form.fields['comparison_text'].disabled=True
        form.fields['comparison_text'].widget=HiddenInput()
    if request.method=='POST':
        if not draft or draft.published_at:
            return HttpResponse('No editable draft is available.',status=409)
        if form.is_valid():
            try:reviews.edit_draft(meeting,job.pk,request.user,form.cleaned_data)
            except reviews.ReviewError as error:form.add_error(None,str(error))
            else:return redirect('homework-review',course_id=meeting.course_id,meeting_id=meeting.pk,job_id=job.pk)
    newer=job.submission.assignment.submissions.filter(student=job.submission.student,version_number__gt=job.submission.version_number).exists()
    failure_reason={'provider_unavailable':'No accepted feedback provider is active for this language.',
                    'individual_failed':'Individual feedback could not be generated or validated. No draft can be published.',
                    'comparison_failed':'The comparison could not be completed. Individual feedback is available for your review.',
                    'interrupted':'The feedback request was interrupted. No new feedback was published.'}.get(job.error_code,'')
    return render(request,'classroom/homework_review.html',{**context(meeting,membership),'job':job,'draft':draft,'form':form,
        'newer_version':newer,'failure_reason':failure_reason,'publish_form':FeedbackPublishForm(initial={'version':draft.version}) if draft else None})


@scoped(Membership.Role.LECTURER,methods=('POST',))
def review_publish(request,meeting,membership,job_id):
    form=FeedbackPublishForm(request.POST)
    if not form.is_valid():return HttpResponse('Invalid publication request.',status=400)
    try:reviews.publish(meeting,job_id,request.user,form.cleaned_data['version'],form.cleaned_data['mode'])
    except reviews.ReviewError as error:return render(request,'classroom/participation_error.html',{**context(meeting,membership),'error':str(error)},status=409)
    messages.success(request,'Feedback published for its recorded submission version.')
    return redirect('homework-review',course_id=meeting.course_id,meeting_id=meeting.pk,job_id=job_id)
