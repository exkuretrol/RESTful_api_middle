from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

appname = "api"
urlpatterns = [
    path(
        "leaves/",
        views.NormalUserLeaveRequestListCreateAPIView.as_view(),
        name="normal-user-leaves-list",
    ),
    path(
        "leaves/<uuid:request_uuid>/",
        views.NormalUserLeaveRetrieveUpdateDestroyAPIView.as_view(),
        name="normal-user-leaves",
    ),
    path(
        "leaves/categories/",
        views.LeaveCategoryListAPIView.as_view(),
        name="leave-categories-list",
    ),
    path(
        "manage/leaves/",
        views.AdminUserLeaveRequestListAPIView.as_view(),
        name="admin-user-leaves-list",
    ),
    path(
        "manage/leaves/<uuid:request_uuid>/approve/",
        views.LeaveRequestApproveRejectAPIView.as_view(leave_request_action="approve"),
        name="leave-request-approve",
    ),
    path(
        "manage/leaves/<uuid:request_uuid>/reject/",
        views.LeaveRequestApproveRejectAPIView.as_view(leave_request_action="reject"),
        name="leave-request-reject",
    ),
]
