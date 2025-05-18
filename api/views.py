from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from core.models import User

from .models import LeaveCategory, LeaveRequest, UserLeaveBalance
from .serializers import (
    LeaveCategorySerializer,
    LeaveRequestApproveRejectSerializer,
    LeaveRequestCreateUpdateSerializer,
    LeaveRequestSerializer,
    UserLeaveBalanceSerializer,
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


class UserLeaveBalanceListAPIView(ListAPIView):
    """
    A viewset for viewing UserLeaveBalance instances.
    """

    queryset = UserLeaveBalance.objects.all()
    serializer_class = UserLeaveBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.gender == User.SexChoices.FEMALE:
            return UserLeaveBalance.objects.filter(user=user)
        return UserLeaveBalance.objects.filter(user=user).exclude(
            category=LeaveCategory.objects.get(name="生理假")
        )


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
        if self.request.method in ["PUT", "PATCH"]:
            return LeaveRequestCreateUpdateSerializer
        return super().get_serializer_class()


class AdminUserLeaveRequestListAPIView(ListAPIView):
    """
    A viewset for viewing LeaveRequest instances.
    """

    queryset = LeaveRequest.objects.filter(
        status=LeaveRequest.StatusChoices.SUBMITTED
    ).order_by("uuid")
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminUser]


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

    def __init__(self, **kwargs):
        self.leave_request_action = kwargs.get("leave_request_action")
        super().__init__(**kwargs)

    def perform_update(self, serializer):
        update_kwargs = {
            "process_user": self.request.user,
        }
        if self.leave_request_action == "approve":
            update_kwargs["status"] = LeaveRequest.StatusChoices.APPROVED
        elif self.leave_request_action == "reject":
            update_kwargs["status"] = LeaveRequest.StatusChoices.REJECTED
        serializer.save(**update_kwargs)
