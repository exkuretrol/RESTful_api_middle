from django.contrib import admin

from .models import Department, Role, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "department", "role")
    search_fields = ("username", "department__name", "role__name")
    list_filter = ("department", "role")
    ordering = ("username",)
    list_select_related = ("department", "role")
    raw_id_fields = ("department", "role")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_supervisor")
