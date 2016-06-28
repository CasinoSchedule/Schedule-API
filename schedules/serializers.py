from rest_framework import serializers

from profiles.models import EmployeeProfile
from profiles.serializers import EmployeeProfileSerializer
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


class EmployeeShiftSerializer(serializers.ModelSerializer):

    employee = EmployeeProfileSerializer(read_only=True)

    class Meta:
        model = Shift
        fields = ("starting_time", "length", "employee", "calendar_date",
                  "end_time")


class ShiftSerializer(serializers.ModelSerializer):


    class Meta:
        model = Shift
        fields = "__all__"


class EmployeeShiftScheduleSerializer(serializers.ModelSerializer):

    #shift_set = ShiftSerializer(many=True, read_only=True)
    test = serializers.ReadOnlyField()

    class Meta:
        model = EmployeeProfile
        fields = "__all__"
