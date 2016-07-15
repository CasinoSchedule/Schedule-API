from django.contrib import admin
from profiles.models import ManagerProfile, EmployeeProfile


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "position_title", "created_at",
                    "modified_at")


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name", "employee_id", "position_title",
                    "phone_number", "email", "phone_notifications",
                    "email_notifications", "days_off", "created_at", "modified_at")
