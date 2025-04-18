import uuid

from django.db import models

from core.models import Role, User


class LeaveCategory(models.Model):
    class ResetPolicyChoices(models.IntegerChoices):
        NONE = 0, "不會重置"
        MONTHLY = 1, "每月重置"
        YEARLY = 2, "每年重置"

    name = models.CharField("假別名稱", max_length=32)
    reset_policy = models.SmallIntegerField(
        "重置規則",
        choices=ResetPolicyChoices.choices,
        default=ResetPolicyChoices.NONE,
    )
    effective_start_date = models.DateField("生效日期（起）", null=True, blank=True)
    effective_end_date = models.DateField("生效日期（止）", null=True, blank=True)

    def __str__(self):
        return self.name


class RoleLeavePolicy(models.Model):
    """
    每個職級對應的假別預設可請時數
    """

    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="職級")
    category = models.ForeignKey(
        LeaveCategory, on_delete=models.CASCADE, verbose_name="假別"
    )
    default_amount = models.IntegerField("預設可請時數")


class UserLeaveBalance(models.Model):
    """
    每個使用者實際剩餘的假別
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="使用者")
    category = models.ForeignKey(
        LeaveCategory, on_delete=models.CASCADE, verbose_name="假別"
    )
    remaining_amount = models.IntegerField("剩餘時數")


class LeaveRequest(models.Model):
    """
    請假申請主表
    """

    class StatusChoices(models.IntegerChoices):
        SUBMITTED = 0, "已送出"
        LOCKED = 1, "已鎖定"
        APPROVED = 2, "已同意"
        REJECTED = 3, "已拒絕"

    uuid = models.UUIDField(
        "請假單號", primary_key=True, default=uuid.uuid4, editable=False
    )
    submitted_at = models.DateTimeField("送出時間", auto_now_add=True)
    effective_start_datetime = models.DateTimeField("生效起始時間")
    effective_end_datetime = models.DateTimeField("生效結束時間")
    category = models.ForeignKey(
        LeaveCategory, on_delete=models.CASCADE, verbose_name="假別"
    )
    status = models.IntegerField(
        "狀態", choices=StatusChoices.choices, default=StatusChoices.SUBMITTED
    )
    comment = models.TextField("附言", blank=True, null=True)
    reason = models.TextField("請假原因", blank=True, null=True)

    request_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="leave_requests",
        verbose_name="申請人",
    )
    process_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_leaves",
        verbose_name="審核主管",
    )
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    processed_at = models.DateTimeField("審核時間", null=True, blank=True)


class LeaveRequestPerDay(models.Model):
    """
    請假明細（每一天的細項記錄），較方便查詢請假紀錄
    """

    request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name="per_day_entries",
        verbose_name="請假單",
    )
    date = models.DateField("請假日期")
    start_time = models.TimeField("開始時間")
    end_time = models.TimeField("結束時間")

    def leave_hours(self):
        """
        計算請假時數
        """
        return self.end_time.hour - self.start_time.hour
