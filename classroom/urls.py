from django.urls import path
from . import views
from . import participation_views as participation
from . import poll_views as polls
from . import video_views as videos

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
    path(meeting_prefix + 'polls/', polls.poll_list, name='poll-list'),
    path(meeting_prefix + 'polls/new/', polls.poll_create, name='poll-create'),
    path(meeting_prefix + 'polls/<int:poll_id>/', polls.poll_detail, name='poll-detail'),
    path(meeting_prefix + 'polls/<int:poll_id>/state/', polls.poll_state, name='poll-state'),
    path(meeting_prefix + 'polls/<int:poll_id>/edit/', polls.poll_edit, name='poll-edit'),
    path(meeting_prefix + 'polls/<int:poll_id>/publish/', polls.poll_publish, name='poll-publish'),
    path(meeting_prefix + 'polls/<int:poll_id>/close/', polls.poll_close, name='poll-close'),
    path(meeting_prefix + 'polls/<int:poll_id>/vote/', polls.poll_vote, name='poll-vote'),
    path(meeting_prefix + 'videos/',videos.video_list,name='video-list'),
    path(meeting_prefix + 'videos/<uuid:job_id>/',videos.video_detail,name='video-detail'),
    path(meeting_prefix + 'videos/<uuid:job_id>/state/',videos.video_state,name='video-state'),
    path(meeting_prefix + 'videos/<uuid:job_id>/transcript/',videos.video_transcript,name='video-transcript'),
]
