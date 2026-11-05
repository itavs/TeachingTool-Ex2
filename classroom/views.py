from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe
from .forms import MeetingForm
from .models import Membership


def membership_for(user, course_id):
    """Resolve every request against current database membership, not UI state."""
    return Membership.objects.select_related("course").filter(user=user, course_id=course_id).first()


def unavailable(request):
    # Identical response for a missing resource and a resource in another course.
    return render(request, "classroom/unavailable.html", status=404)


@login_required
@require_safe
def course_list(request):
    memberships = request.user.memberships.select_related("course").order_by("course__code")
    return render(request, "classroom/course_list.html", {"memberships": memberships})


@login_required
@require_safe
def course_detail(request, course_id):
    membership = membership_for(request.user, course_id)
    if membership is None:
        return unavailable(request)
    return render(request, "classroom/course_detail.html", {
        "membership": membership, "course": membership.course,
        "meetings": membership.course.meetings.all(),
    })


@login_required
@require_safe
def meeting_detail(request, course_id, meeting_id):
    membership = membership_for(request.user, course_id)
    if membership is None:
        return unavailable(request)
    meeting = membership.course.meetings.filter(pk=meeting_id).first()
    if meeting is None:
        return unavailable(request)
    return render(request, "classroom/meeting_detail.html", {
        "membership": membership, "course": membership.course, "meeting": meeting,
    })


@login_required
@require_http_methods(["GET", "POST"])
def meeting_form(request, course_id, meeting_id=None):
    membership = membership_for(request.user, course_id)
    if membership is None:
        return unavailable(request)
    if membership.role != Membership.Role.LECTURER:
        return render(request, "classroom/forbidden.html", {"course": membership.course}, status=403)
    meeting = None
    if meeting_id is not None:
        meeting = membership.course.meetings.filter(pk=meeting_id).first()
        if meeting is None:
            return unavailable(request)
    form = MeetingForm(request.POST if request.method == "POST" else None, instance=meeting)
    if request.method == "POST" and form.is_valid():
        saved = form.save(commit=False)
        # Course is always server-selected; posted course/user/role values are ignored.
        saved.course = membership.course
        saved.save()
        messages.success(request, "Meeting updated." if meeting is not None else "Meeting created.")
        return redirect("meeting-detail", course_id=membership.course_id, meeting_id=saved.pk)
    return render(request, "classroom/meeting_form.html", {
        "course": membership.course, "form": form, "meeting": meeting,
    })
