from django.contrib import admin
from profiles.models import ManagerProfile, EmployeeProfile, Available


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "position_title",
                    "user_name", "department", "created_at", "modified_at")


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name", "department", "employee_id", "position_title",
                    "phone_number", "email", "phone_notifications",
                    "email_notifications", "days_off", 'shift_title', "created_at", "modified_at")


@admin.register(Available)
class AvailableAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
