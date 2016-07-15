from rest_framework import serializers
from profiles.models import EmployeeProfile
from schedules.models import DayOfWeek


class DayOffSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayOfWeek
        fields = '__all__'


class EmployeeProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeProfile
        fields = ("id", "employee_id", "first_name", "last_name", "days_off", "position_title", "phone_number",
                  "email", "phone_notifications", "email_notifications",
                  "user", "employment_status"
                  )


class UpdateEmployeeProfileSerializer(serializers.ModelSerializer):
    #days = serializers.ListField()

    class Meta:
        model = EmployeeProfile
        fields = '__all__'

    # def update(self, instance, validated_data):
    #     a=1
    #     #instance.regular_days_off.add(DayOfWeek.objects.get(title='Tuesday'))
    #     return super().update(instance, validated_data)

