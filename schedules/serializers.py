from rest_framework import serializers

from schedules.models import DayOfWeek, Schedule, WorkDay, Shift


class DayOfWeekSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayOfWeek
        fields = ("day", "is_weekend", "python_int")


class WorkDaySerializer(serializers.ModelSerializer):

    day_of_the_week = DayOfWeekSerializer(read_only=True)

    class Meta:
        model = WorkDay
        fields = "__all__"


class ScheduleSerializer(serializers.ModelSerializer):
    workday_set = WorkDaySerializer(many=True, read_only=True)
    starting = serializers.ReadOnlyField()

    class Meta:
        model = Schedule
        fields = ("starting", "status", "manager", "created_at", "modified_at",
                  "workday_set")


# class EmployeeWorkDaySerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = WorkDay
#         fields = ()


class EmployeeShiftSerializer(serializers.ModelSerializer):

    #day = WorkDaySerializer(read_only=True)

    class Meta:
        model = Shift
        fields = ("starting_time", "length", "employee", "calendar_date")

class ShiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift
        fields = "__all__"