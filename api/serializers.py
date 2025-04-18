from typing import Literal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from core.models import Department, Role, User

from .models import LeaveCategory, LeaveRequest, LeaveRequestPerDay


class LeaveRequestPerDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequestPerDay
        fields = (
            "date",
            "start_time",
            "end_time",
            "leave_hours",
        )
        extra_kwargs = {}


class TotalLeaveHoursMixin:

    def get_total_leave_hours(self, obj):
        """
        Calculate the total leave hours for the leave request.
        """
        total_hours = 0
        for entry in obj.per_day_entries.all():
            total_hours += entry.leave_hours()
        return total_hours


class LeaveRequestSerializer(TotalLeaveHoursMixin, serializers.ModelSerializer):
    """
    Serializer for LeaveRequest model.
    """

    per_day_entries = LeaveRequestPerDaySerializer(many=True, read_only=True)
    total_leave_hours = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = (
            "uuid",
            "category",
            "reason",
            "request_user",
            "process_user",
            "effective_start_datetime",
            "effective_end_datetime",
            "per_day_entries",
            "status",
            "total_leave_hours",
            "created_at",
            "processed_at",
            "comment",
        )
        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class LeaveRequestApproveRejectSerializer(
    TotalLeaveHoursMixin, serializers.ModelSerializer
):
    """
    Serializer for LeaveRequest model. Used for approving leave requests.
    """

    total_leave_hours = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        with transaction.atomic():
            # TODO: check the supervisor is the same department as the request_user
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

        return instance

    class Meta:
        model = LeaveRequest
        fields = (
            "uuid",
            "status",
            "reason",
            "comment",
            "effective_start_datetime",
            "effective_end_datetime",
            "total_leave_hours",
            "request_user",
            "process_user",
        )
        extra_kwargs = {
            "uuid": {
                "read_only": True,
            },
            "status": {
                "read_only": True,
            },
            "reason": {
                "read_only": True,
            },
            "request_user": {
                "read_only": True,
            },
            "effective_start_datetime": {
                "read_only": True,
            },
            "effective_end_datetime": {
                "read_only": True,
            },
        }


OFF_WORK_TIME = timezone.datetime.strptime("18:00", "%H:%M").time()


class LeaveRequestCreateUpdateSerializer(
    TotalLeaveHoursMixin, serializers.ModelSerializer
):
    """
    Serializer for LeaveRequest model. Used for creating and updating leave requests.
    """

    per_day_entries = LeaveRequestPerDaySerializer(many=True, required=False)
    total_leave_hours = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        with transaction.atomic():
            pass

    def create(self, validated_data):
        """
        Create a new LeaveRequest instance.
        """

        # TODO: extract the validation logic to a separate function
        effective_start_datetime = validated_data.get("effective_start_datetime")
        effective_end_datetime = validated_data.get("effective_end_datetime")

        if validated_data.get("per_day_entries", None):
            raise serializers.ValidationError(
                "LeaveRequestPerDay entries should not be provided during creation."
            )

        if effective_start_datetime > effective_end_datetime:
            raise serializers.ValidationError(
                "Effective start datetime must be before effective end datetime."
            )

        if effective_start_datetime.minute != 0 or effective_end_datetime.minute != 0:
            raise serializers.ValidationError(
                "Effective start and end datetimes must be on the hour."
            )

        # TODO: add overlap check

        with transaction.atomic():
            leave_request = LeaveRequest.objects.create(**validated_data)

            # Extract the date and time components
            start_date = effective_start_datetime.date()
            start_time = effective_start_datetime.time()
            end_date = effective_end_datetime.date()
            end_time = effective_end_datetime.time()

            if end_date != start_date:
                # create per_day_entries for each day in the range
                for i in range((end_date - start_date).days + 1):
                    date = start_date + timezone.timedelta(days=i)
                    LeaveRequestPerDay.objects.create(
                        request=leave_request,
                        date=date,
                        start_time=start_time,
                        end_time=end_time if end_date == date else OFF_WORK_TIME,
                    )
            else:
                # create a single per_day_entry
                LeaveRequestPerDay.objects.create(
                    request=leave_request,
                    date=start_date,
                    start_time=start_time,
                    end_time=end_time,
                )
        return leave_request

    class Meta:
        model = LeaveRequest
        fields = (
            "uuid",
            "request_user",
            "per_day_entries",
            "category",
            "effective_start_datetime",
            "effective_end_datetime",
            "total_leave_hours",
            "status",
        )
        extra_kwargs = {
            "uuid": {"read_only": True},
            "status": {"read_only": True},
            "request_user": {"read_only": True},
        }


class LeaveCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for LeaveCategory model.
    """

    class Meta:
        model = LeaveCategory
        fields = ("id", "name")
        extra_kwargs = {}
