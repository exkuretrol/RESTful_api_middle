from typing import Literal

from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from core.models import User

from .models import LeaveCategory, LeaveRequest
from .serializers import (
    LeaveCategorySerializer,
    LeaveRequestApproveRejectSerializer,
    LeaveRequestCreateUpdateSerializer,
    LeaveRequestSerializer,
)


class LeaveCategoryListAPIView(ListAPIView):
    """
    A viewset for viewing and creating LeaveCategory instances.
    """

    # TODO: CRUD?

    queryset = LeaveCategory.objects.all()
    serializer_class = LeaveCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        is_female = self.request.user.gender == User.SexChoices.FEMALE
        if not is_female:
            return super().get_queryset()
        return LeaveCategory.objects.exclude(name="生理假")


class NormalUserLeaveRequestListCreateAPIView(ListCreateAPIView):
    """
    A viewset for viewing and creating LeaveRequest instances.
    """

    queryset = LeaveRequest.objects.select_related("per_day_entries")
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return LeaveRequest.objects.filter(request_user=user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LeaveRequestCreateUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """
        Save the request_user to the serializer.
        """
        serializer.save(request_user=self.request.user)


class NormalUserLeaveRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    A viewset for viewing and editing LeaveRequest instances.
    """

    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"
    lookup_url_kwarg = "request_uuid"

    def get_serializer_class(self):
        if self.action in ["update"]:
            return LeaveRequestCreateUpdateSerializer
        return super().get_serializer_class()


class LeaveRequestApproveRejectAPIView(UpdateAPIView):
    """
    A viewset for approving LeaveRequest instances.
    """

    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestApproveRejectSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "uuid"
    lookup_url_kwarg = "request_uuid"
    leave_request_action = None

    def get_serializer_class(self):
        return LeaveRequestApproveRejectSerializer(action=self.leave_request_action)
