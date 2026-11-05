from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course-list"),
    path("courses/<int:course_id>/", views.course_detail, name="course-detail"),
    path("courses/<int:course_id>/meetings/new/", views.meeting_form, name="meeting-create"),
    path("courses/<int:course_id>/meetings/<int:meeting_id>/", views.meeting_detail, name="meeting-detail"),
    path("courses/<int:course_id>/meetings/<int:meeting_id>/edit/", views.meeting_form, name="meeting-edit"),
]
