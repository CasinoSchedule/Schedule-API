from django.contrib import admin
from schedules.models import DayOfWeek, WorkDay, Schedule, Shift


@admin.register(DayOfWeek)
class DayOfWeekAdmin(admin.ModelAdmin):
    list_display = ("id", "day", "is_weekend", "python_int")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "manager", "status", "created_at", "modified_at", "starting")


@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ("id", "day_date", "day_of_the_week", "schedule")


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("id", "starting_time", "length", "day", "employee",)

