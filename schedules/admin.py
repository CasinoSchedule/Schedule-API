from django.contrib import admin
from schedules.models import WorkDay, Schedule, Shift, EOList, CallOut


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "manager", "status", "created_at", "modified_at", "starting")


@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ("id", "day_date", "schedule")


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("id", "visible", "starting_time", "length", "day", "employee",)


@admin.register(EOList)
class EOListAdmin(admin.ModelAdmin):
    list_display = ("id", "day", "created_at", "modified_at")

@admin.register(CallOut)
class CallOutAdmin(admin.ModelAdmin):
    list_display = ('id', 'shift', 'created_at', 'modified_at')

