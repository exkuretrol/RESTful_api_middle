from django.contrib import admin

from .models import (
    LeaveCategory,
    LeaveRequest,
    LeaveRequestPerDay,
    RoleLeavePolicy,
    UserLeaveBalance,
)


@admin.register(LeaveCategory)
class LeaveCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "reset_policy",
        "effective_start_date",
        "effective_end_date",
    )
    search_fields = ("name",)
    list_filter = ("reset_policy",)
    ordering = ("name",)


@admin.register(RoleLeavePolicy)
class RoleLeavePolicyAdmin(admin.ModelAdmin):
    list_display = ("role", "category", "default_amount")
    search_fields = ("role__name", "category__name")
    list_filter = ("role", "category")
    ordering = ("role", "category")


@admin.register(UserLeaveBalance)
class UserLeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "remaining_amount")
    search_fields = ("user__username", "category__name")
    list_filter = ("user", "category")
    ordering = ("user", "category")


class LeaveRequestPerDayInline(admin.TabularInline):
    model = LeaveRequestPerDay
    extra = 0


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "reason",
        "request_user",
        "process_user",
        "effective_start_datetime",
        "effective_end_datetime",
        "status",
        "created_at",
        "processed_at",
        "comment",
    )
    list_filter = ("status", "category", "request_user", "process_user")
    inlines = [LeaveRequestPerDayInline]
    ordering = ("-created_at",)
