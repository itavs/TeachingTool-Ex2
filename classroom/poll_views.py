from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import Membership, Poll
from .participation_views import scoped, context
from .poll_forms import GenerationForm, DraftForm, VoteForm, VersionForm
from .poll_generation import GenerationUnavailable
from . import poll_services as rules


def error_page(request, meeting, membership, error):
    return render(request, 'classroom/participation_error.html', {**context(meeting,membership), 'error':str(error)}, status=error.status)


@scoped()
def poll_list(request, meeting, membership):
    polls = meeting.polls.all()
    if membership.role == Membership.Role.STUDENT:
        polls = polls.exclude(status=Poll.Status.DRAFT)
    # List context contains no material, answer, explanation or vote identities.
    items = [{'id':p.pk, 'question':p.question, 'kind_label':p.get_kind_display(),
        'status':p.get_status_display(), 'origin_label':p.origin_label} for p in polls]
    return render(request,'classroom/poll_list.html',{**context(meeting,membership),'polls':items})


@scoped(Membership.Role.LECTURER, ('GET','POST'))
def poll_create(request, meeting, membership):
    form = GenerationForm(request.POST if request.method == 'POST' else None)
    status = 200
    if request.method == 'POST':
        status = 400
        if form.is_valid():
            try:
                poll = rules.create_generated_draft(meeting.pk, request.user, **form.cleaned_data)
                return redirect('poll-edit',course_id=meeting.course_id,meeting_id=meeting.pk,poll_id=poll.pk)
            except GenerationUnavailable as error:
                form.add_error(None,str(error))
                status = 503
            except ValidationError:
                form.add_error(None,'The generated response was invalid. No usable draft was saved. You may retry explicitly.')
    return render(request,'classroom/poll_create.html',{**context(meeting,membership),'form':form},status=status)


@scoped()
def poll_detail(request, meeting, membership, poll_id):
    poll, _ = rules.get_poll(meeting.pk,poll_id,request.user)
    return render(request,'classroom/poll_detail.html',{**context(meeting,membership),
        'display':rules.public_payload(poll,membership,request.user), 'version':poll.version if membership.role == Membership.Role.LECTURER else None,
        'vote_form':VoteForm(poll=poll) if membership.role == Membership.Role.STUDENT and poll.status == Poll.Status.ACTIVE else None})


@scoped()
def poll_state(request, meeting, membership, poll_id):
    poll, _ = rules.get_poll(meeting.pk,poll_id,request.user)
    return JsonResponse(rules.public_payload(poll,membership,request.user))


@scoped(Membership.Role.LECTURER, ('GET','POST'))
def poll_edit(request, meeting, membership, poll_id):
    poll, _ = rules.get_poll(meeting.pk,poll_id,request.user)
    if poll.status != Poll.Status.DRAFT:
        return error_page(request,meeting,membership,rules.PollError('Published polls cannot be edited.'))
    form = DraftForm(request.POST if request.method == 'POST' else None,poll=poll)
    if request.method == 'POST' and form.is_valid():
        try:
            rules.edit_draft(meeting.pk,poll.pk,request.user,form.cleaned_data['version'],form.content())
        except rules.PollError as error:
            return error_page(request,meeting,membership,error)
        messages.success(request,'Draft saved. Review before publishing.')
        return redirect('poll-detail',course_id=meeting.course_id,meeting_id=meeting.pk,poll_id=poll.pk)
    return render(request,'classroom/poll_edit.html',{**context(meeting,membership),'poll':poll,'form':form},status=400 if request.method == 'POST' else 200)


@scoped(Membership.Role.LECTURER, ('POST',))
def poll_publish(request, meeting, membership, poll_id):
    form = VersionForm(request.POST)
    if not form.is_valid():
        return error_page(request,meeting,membership,rules.PollError('Reload the draft before publishing.',400))
    try:
        rules.publish(meeting.pk,poll_id,request.user,form.cleaned_data['version'])
    except (rules.PollError,ValidationError) as error:
        return error_page(request,meeting,membership,error if isinstance(error,rules.PollError) else rules.PollError('The draft is invalid and cannot be published.',400))
    return redirect('poll-detail',course_id=meeting.course_id,meeting_id=meeting.pk,poll_id=poll_id)


@scoped(Membership.Role.LECTURER, ('POST',))
def poll_close(request, meeting, membership, poll_id):
    try:
        rules.close(meeting.pk,poll_id,request.user)
    except rules.PollError as error:
        return error_page(request,meeting,membership,error)
    return redirect('poll-detail',course_id=meeting.course_id,meeting_id=meeting.pk,poll_id=poll_id)


@scoped(Membership.Role.STUDENT, ('POST',))
def poll_vote(request, meeting, membership, poll_id):
    poll, _ = rules.get_poll(meeting.pk,poll_id,request.user)
    form = VoteForm(request.POST,poll=poll)
    if not form.is_valid():
        return error_page(request,meeting,membership,rules.PollError('Select exactly one of the four options.',400))
    # QueryDict normally takes the last value; reject a forged multi-value choice.
    if len(request.POST.getlist('option_index')) != 1:
        return error_page(request,meeting,membership,rules.PollError('Select exactly one option.',400))
    try:
        rules.vote(meeting.pk,poll_id,request.user,form.cleaned_data['option_index'])
    except rules.PollError as error:
        return error_page(request,meeting,membership,error)
    messages.success(request,'Your final response was saved. It cannot be changed.')
    return redirect('poll-detail',course_id=meeting.course_id,meeting_id=meeting.pk,poll_id=poll_id)
