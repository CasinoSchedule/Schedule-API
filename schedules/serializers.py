from rest_framework import serializers

from profiles.models import EmployeeProfile
from profiles.serializers import EmployeeProfileSerializer
from schedules.models import Schedule, WorkDay, Shift


class WorkDaySerializer(serializers.ModelSerializer):

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
                  "end_time", "day")


class ShiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift
        fields = "__all__"


class MultipleShiftSerializer(serializers.ModelSerializer):
    # def __init__(self, *args, **kwargs):
    #     many = kwargs.pop('many', True)
    #     super(MultipleShiftSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = Shift
        fields = "__all__"


class EmployeeShiftScheduleSerializer(serializers.ModelSerializer):

    #shift_set = ShiftSerializer(many=True, read_only=True)
    test = serializers.ReadOnlyField()

    class Meta:
        model = EmployeeProfile
        fields = "__all__"


class ShiftByDateSerializer(serializers.ModelSerializer):

    day = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Shift
        fields = "__all__"
