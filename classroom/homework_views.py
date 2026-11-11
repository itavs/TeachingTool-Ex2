"""Submitted-work foundation only: no review request or AI-generation endpoints."""
from django.contrib import messages
from django.shortcuts import redirect, render
from .attendance import CourseAccessError
from .models import Membership
from .participation_views import scoped, context
from .homework_forms import AssignmentForm, SubmissionForm
from . import homework_services as services


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
    return render(request, "classroom/homework_submission.html", {**context(meeting, membership),
                  "assignment": assignment, "submission": submission})
