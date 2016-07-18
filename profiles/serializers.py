from rest_framework import serializers
from profiles.models import EmployeeProfile, Available
from schedules.models import DayOfWeek


class DayOffSerializer(serializers.ModelSerializer):

    class Meta:
        model = DayOfWeek
        fields = '__all__'


class EmployeeProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeProfile
        fields = ("id", "employee_id", "first_name", "last_name", "days_off",
                  "shift_title", "position_title", "phone_number",
                  "email", "phone_notifications", "email_notifications",
                  "user", "employment_status"
                  )


class UpdateCreateEmployeeProfileSerializer(serializers.ModelSerializer):
    availability = serializers.PrimaryKeyRelatedField(many=True,
                                                      read_only=False,
                                                      queryset=Available.objects.all(),
                                                      required=False)
    regular_days_off = serializers.PrimaryKeyRelatedField(many=True,
                                                          read_only=False,
                                                          queryset=DayOfWeek.objects.all(),
                                                          required=False)

    class Meta:
        model = EmployeeProfile
        fields = '__all__'

    def update(self, instance, validated_data):
        a=1
        #instance.regular_days_off.add(DayOfWeek.objects.get(title='Tuesday'))
        return super().update(instance, validated_data)


# class TestUpdate(serializers.Serializer):
#
#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         return instance