from rest_framework import serializers

from profiles.serializers import EmployeeProfileSerializer
from schedules.models import WorkDay, Shift, EOList, EOEntry, CallOut, \
    TimeOffRequest, Area, Station, ShiftTemplate


class WorkDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkDay
        fields = "__all__"


class WorkDayDateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkDay
        fields = ('day_date',)


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):

    #station_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    station_set = StationSerializer(read_only=True, many=True)

    class Meta:
        model = Area
        fields = '__all__'


class EmployeeShiftSerializer(serializers.ModelSerializer):

    employee = EmployeeProfileSerializer(read_only=True)
    station = StationSerializer(read_only=True)

    class Meta:
        model = Shift
        fields = ("id", "starting_time", "area", "station", "length",
                  "visible", "called_out", "employee", "calendar_date",
                  "end_time", "day", 'epoch_milliseconds')


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


class TimeOffRequestCreateSerializer(serializers.ModelSerializer):

    employee = serializers.PrimaryKeyRelatedField(read_only=True)
    days = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = TimeOffRequest
        fields = '__all__'


class TimeOffRequestDisplaySerializer(serializers.ModelSerializer):

    employee = EmployeeProfileSerializer(read_only=True)
    days = WorkDayDateSerializer(read_only=True, many=True)

    class Meta:
        model = TimeOffRequest
        fields = '__all__'


class ShiftTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShiftTemplate
        fields = '__all__'
