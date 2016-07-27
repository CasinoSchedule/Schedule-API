from rest_framework import serializers
from profiles.models import EmployeeProfile, Available
from schedules.models import DayOfWeek
from django.contrib.auth.models import User


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
    availability = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=Available.objects.all(),
        required=False)
    regular_days_off = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=DayOfWeek.objects.all(),
        required=False)

    class Meta:
        model = EmployeeProfile
        fields = '__all__'

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}, }
        fields = '__all__'


class UserCreateWithProfileSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}, }

        fields = ('username', 'password', 'profile_id')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
