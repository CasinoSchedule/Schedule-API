from rest_framework import serializers

from schedules.models import DayOfWeek, Schedule, WorkDay


class DayOfWeekSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayOfWeek
        fields = "__all__"


class WorkDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkDay
        fields = "__all__"

class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = "__all__"
