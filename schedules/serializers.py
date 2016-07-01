from rest_framework import serializers
from django.contrib.auth.models import User

from profiles.models import EmployeeProfile
from profiles.serializers import EmployeeProfileSerializer
from schedules.models import Schedule, WorkDay, Shift


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


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


class ShiftCreateSerializer(serializers.ModelSerializer):


    class Meta:
        model = Shift
        fields = "__all__"


class ShiftSerializer(serializers.ModelSerializer):

    day = WorkDaySerializer(read_only=True)

    class Meta:
        model = Shift
        fields = "__all__"


class MultipleShiftSerializer(serializers.ModelSerializer):

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

# class MultipleShiftByDateSerializer(serializers.ModelSerializer):
#
#     day = serializers.PrimaryKeyRelatedField(read_only=True)
#
#     class Meta:
#         model = Shift
#         fields = "__all__"
#
#     def create(self, validated_data):
#         day = WorkDay.objects.get(day_date=validated_data["day"])
#         return Shift(starting_time=validated_data["starting_time"],
#                      day=day,
#                      employee=validated_data["employee"])


