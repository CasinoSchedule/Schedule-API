from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import generics, status
from schedules.sendgrid_functions import signup_email

from profiles.models import EmployeeProfile, ManagerProfile
from profiles.serializers import EmployeeProfileSerializer, \
    UpdateCreateEmployeeProfileSerializer, UserCreateWithProfileSerializer, UserSerializer

"""
Views for updating and creating profiles
"""


class NotifyNewEmployee(APIView):
    """
    POST an email and employee profile id. They will be sent a link to register
    as a new user, linked with that profile.
    example: {"email": "aaron@aol.com", "profile_id": 5}
    """
    def post(self, request, format=None):
        signup_email(request.data['email'], request.data['profile_id'])
        return Response('email sent successfully', status=status.HTTP_200_OK)


class EmployeeProfileListCreateView(generics.ListCreateAPIView):
    """
    Use ?shift_title=1 to filter for employees on graveyard.
    """
    serializer_class = UpdateCreateEmployeeProfileSerializer

    def get_queryset(self):
        qs = EmployeeProfile.objects.all().order_by('created_at')
        shift_title = self.request.query_params.get('shift_title')
        if shift_title:
            shift_title = [int(x) for x in shift_title.split(',')]
            qs = qs.filter(availability__in=shift_title)
        return qs


class EmployeeProfileGetDelete(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete an employee profile.
    """
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer


class EmployeeProfileUpdate(APIView):
    """
    Update employee profile.
    For days_off send a list of integers, 1=Monday, 7=Sunday.
    For availability send a list of integers, 1=grave, 2=day, 3=swing
    """

    def put(self, request, pk):

        try:
            profile = EmployeeProfile.objects.get(pk=pk)
        except EmployeeProfile.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateCreateEmployeeProfileSerializer(profile, request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileCheck(APIView):
    """
    Takes a GET request with a token and returns an object with the type of
    profile the user has under 'type':
    Possible responses: {"type": "employee"}, {"type": "manager"},
     {"type": "no token"}, {"type": "no profile"}
    """

    def get(self, request, format=None):
        if not request.user.id:
            return Response({"type": "no token"})

        if EmployeeProfile.objects.filter(user=request.user).first():
            return Response({"type": "employee"})
        elif ManagerProfile.objects.filter(user=request.user).first():
            return Response({"type": "manager"})
        else:
            return Response({"type": "no profile"})


class UserCreateWithEmployeeProfile(APIView):
    """
    New user creation for those with an existing employee profile object.
    POST name, password, and employee profile_id.
    """
    def post(self, request, format=None):
        serializer = UserCreateWithProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            profile = EmployeeProfile.objects.get(id=request.data['profile_id'])
            if profile.user.id:
                return Response("Profile already has a user",
                                status=status.HTTP_400_BAD_REQUEST
                                )
            profile.user = serializer.instance
            profile.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
