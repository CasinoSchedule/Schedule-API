from django.contrib import admin
from schedules.models import WorkDay, Schedule, Shift, EOList, CallOut, Status, \
    DayOfWeek, TimeOffRequest, Area, Department, Station


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'manager', 'status', 'created_at', 'modified_at', 'starting')


@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ('id', 'day_date', 'schedule')


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("id", "visible", "starting_time", "length", "day", "employee", 'epoch_milliseconds')


@admin.register(EOList)
class EOListAdmin(admin.ModelAdmin):
    list_display = ("id", "day", "created_at", "modified_at")

@admin.register(CallOut)
class CallOutAdmin(admin.ModelAdmin):
    list_display = ('id', 'shift', 'created_at', 'modified_at')

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


@admin.register(DayOfWeek)
class DayOfWeekAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


@admin.register(TimeOffRequest)
class TimeOffRequest(admin.ModelAdmin):
    list_display = ("id", "employee", "status")


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'grave_start', 'day_start', 'swing_start')
