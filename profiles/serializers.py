from rest_framework import serializers
from profiles.models import EmployeeProfile


class EmployeeProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeProfile
        fields = ("id", "employee_id", "position_title", "phone_number",
                  "email", "phone_notifications", "email_notifications",
                  "user", "employment_status", "days_off"
                  )
