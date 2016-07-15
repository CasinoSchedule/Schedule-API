from rest_framework import serializers
from django.contrib.auth.models import User

from profiles.models import EmployeeProfile
from profiles.serializers import EmployeeProfileSerializer
from schedules.models import Schedule, WorkDay, Shift, EOList, EOEntry, CallOut


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
        fields = ("id", "starting_time", "length", "visible", "called_out", "employee",
                  "calendar_date", "end_time", "day")


class ShiftCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift
        fields = "__all__"

    def create(self, validated_data):

        shift = Shift.objects.filter(employee=validated_data['employee'],
                                  day=validated_data['day']).first()

        # Delete shift if starting time is "", otherwise update.
        if shift:
            setattr(shift, 'starting_time', validated_data['starting_time'])
            setattr(shift, 'visible', False)
            shift.save()
        else:
            shift = Shift.objects.create(**validated_data)
        return shift


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


class EOShiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift
        fields = ('employee', 'starting_time')


class EOEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = EOEntry
        fields = ('id', 'eo_list', 'status', 'shift', 'created_at')


class EOListSerializer(serializers.ModelSerializer):
    eo_entries = EOEntrySerializer(read_only=True, many=True)

    class Meta:
        model = EOList
        fields = "__all__"


class CallOutSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallOut
        fields = '__all__'
