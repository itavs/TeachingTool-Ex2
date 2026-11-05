"""Course-scoped attendance and meeting requests; all writes require POST + CSRF."""
import base64
from functools import wraps
from io import BytesIO
import qrcode
from qrcode.image.svg import SvgPathImage
from openpyxl import Workbook
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import OperationalError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from . import attendance as rules
from .models import MeetingRequest, Membership
from .request_forms import RequestForm


def scoped(role=None, methods=("GET",)):
    def decorate(view):
        @login_required
        @never_cache
        @require_http_methods(methods)
        @wraps(view)
        def guarded(request, course_id, meeting_id, **kwargs):
            try:
                meeting, membership = rules.authorize(meeting_id, request.user)
                if meeting.course_id != course_id:
                    raise rules.CourseAccessError(404)
                if role and membership.role != role:
                    raise rules.CourseAccessError(403)
                return view(request, meeting, membership, **kwargs)
            except rules.CourseAccessError as exc:
                return render(request, "classroom/forbidden.html" if exc.status == 403 else "classroom/unavailable.html",
                    {"course": meeting.course} if exc.status == 403 else {}, status=exc.status)
            except OperationalError:
                return render(request, "classroom/participation_error.html", {
                    "error": "The database is busy. A save could not be confirmed. Check the current status before trying again."}, status=503)
        return guarded
    return decorate


def context(meeting, membership):
    return {"course": meeting.course, "meeting": meeting, "membership": membership}


def state(request, meeting):
    now = timezone.now()
    window = rules.current_window(meeting.pk, now)
    data = {"rows": rules.roster(meeting), "window": None}
    if window:
        token = rules.token_for(window, now)
        url = request.build_absolute_uri(reverse("attendance-scan", args=[meeting.course_id, meeting.pk, token]))
        qr = qrcode.make(url, image_factory=SvgPathImage, border=4)
        svg = qr.to_string()
        age = (now - window.opened_at).total_seconds()
        data["window"] = {"additional": window.additional, "remaining": max(0, (window.closes_at - now).total_seconds()),
            "rotation_in": rules.ROTATION_SECONDS - age % rules.ROTATION_SECONDS,
            "scan_url": url, "qr_image": "data:image/svg+xml;base64," + base64.b64encode(svg).decode("ascii")}
    return data


@scoped(Membership.Role.LECTURER)
def attendance_dashboard(request, meeting, membership):
    return render(request, "classroom/attendance.html", {**context(meeting, membership), "headers": rules.HEADERS, "initial": state(request, meeting)})


@scoped(Membership.Role.LECTURER)
def attendance_state(request, meeting, membership):
    return JsonResponse(state(request, meeting))


@scoped(Membership.Role.LECTURER, ("POST",))
def attendance_open(request, meeting, membership):
    rules.open_window(meeting.pk, request.user)
    return redirect("attendance", course_id=meeting.course_id, meeting_id=meeting.pk)


@scoped(Membership.Role.LECTURER, ("POST",))
def attendance_close(request, meeting, membership):
    rules.close_window(meeting.pk, request.user)
    return redirect("attendance", course_id=meeting.course_id, meeting_id=meeting.pk)


@scoped(Membership.Role.STUDENT, ("GET", "POST"))
def attendance_scan(request, meeting, membership, token):
    try:
        if request.method == "POST":
            record, created = rules.register(meeting.pk, request.user, token)
            messages.success(request, "Attendance recorded. " + record.registration_label if created else "Your attendance was already recorded; the original registration is unchanged.")
            return redirect("meeting-detail", course_id=meeting.course_id, meeting_id=meeting.pk)
        rules.validate_token(meeting.pk, token)
    except rules.AttendanceError as exc:
        return render(request, "classroom/participation_error.html", {**context(meeting, membership), "error": str(exc)}, status=410)
    return render(request, "classroom/attendance_scan.html", context(meeting, membership))


@scoped(Membership.Role.LECTURER)
def attendance_export(request, meeting, membership):
    with transaction.atomic():
        rules.authorize(meeting.pk, request.user, Membership.Role.LECTURER)
        rows = rules.roster(meeting)
        exported = rules.display_time(timezone.now())
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"
    for row in [rules.HEADERS, *rows]:
        sheet.append(row)
        for cell in sheet[sheet.max_row]:
            # Treat user-controlled strings as text, including leading '='.
            if isinstance(cell.value, str):
                cell.data_type = "s"
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column in sheet.columns:
        sheet.column_dimensions[column[0].column_letter].width = min(48, max(18, max(len(str(c.value or "")) for c in column) + 2))
    notes = workbook.create_sheet("Snapshot")
    notes.append(["Exported at (Asia/Jerusalem)", exported])
    notes.append(["Meaning", "Snapshot only. No synchronization or import back into the system."])
    notes.append(["Roster", "Current student memberships. Not registered does not mean absent."])
    output = BytesIO()
    workbook.save(output)
    response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="attendance-{meeting.pk}.xlsx"'
    return response


def request_rows(meeting, user, lecturer):
    items = MeetingRequest.objects.filter(meeting=meeting).select_related("student")
    if not lecturer:
        items = items.filter(student=user)
    return [{"id": item.pk, "author": item.student.get_full_name() or item.student.username,
        "username": item.student.username, "kind": item.get_kind_display(), "text": item.text,
        "created_at": rules.display_time(item.created_at)} for item in items]


@scoped(methods=("GET", "POST"))
def requests_page(request, meeting, membership):
    lecturer = membership.role == Membership.Role.LECTURER
    if request.method == "POST" and lecturer:
        raise rules.CourseAccessError(403)
    form = RequestForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            rules.lock_and_authorize(meeting.pk, request.user, Membership.Role.STUDENT)
            _, created = MeetingRequest.objects.get_or_create(meeting=meeting, student=request.user,
                submission_id=form.cleaned_data["submission_id"], defaults={"kind": form.cleaned_data["kind"],
                    "text": form.cleaned_data["text"], "created_at": timezone.now()})
        messages.success(request, "Request saved." if created else "This request was already saved.")
        return redirect("meeting-requests", course_id=meeting.course_id, meeting_id=meeting.pk)
    return render(request, "classroom/requests.html", {**context(meeting, membership), "form": form,
        "lecturer": lecturer, "rows": request_rows(meeting, request.user, lecturer)}, status=400 if request.method == "POST" else 200)


@scoped(Membership.Role.LECTURER)
def requests_feed(request, meeting, membership):
    return JsonResponse({"rows": request_rows(meeting, request.user, True)})
