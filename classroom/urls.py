from django.urls import path
from . import views
from . import participation_views as participation

urlpatterns = [
    path("", views.course_list, name="course-list"),
    path("courses/<int:course_id>/", views.course_detail, name="course-detail"),
    path("courses/<int:course_id>/meetings/new/", views.meeting_form, name="meeting-create"),
    path("courses/<int:course_id>/meetings/<int:meeting_id>/", views.meeting_detail, name="meeting-detail"),
    path("courses/<int:course_id>/meetings/<int:meeting_id>/edit/", views.meeting_form, name="meeting-edit"),
]

meeting_prefix = "courses/<int:course_id>/meetings/<int:meeting_id>/"
urlpatterns += [
    path(meeting_prefix + "attendance/", participation.attendance_dashboard, name="attendance"),
    path(meeting_prefix + "attendance/state/", participation.attendance_state, name="attendance-state"),
    path(meeting_prefix + "attendance/open/", participation.attendance_open, name="attendance-open"),
    path(meeting_prefix + "attendance/close/", participation.attendance_close, name="attendance-close"),
    path(meeting_prefix + "attendance/export/", participation.attendance_export, name="attendance-export"),
    path(meeting_prefix + "attendance/scan/<str:token>/", participation.attendance_scan, name="attendance-scan"),
    path(meeting_prefix + "requests/", participation.requests_page, name="meeting-requests"),
    path(meeting_prefix + "requests/feed/", participation.requests_feed, name="requests-feed"),
]
