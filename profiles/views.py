from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import generics, status

from profiles.models import EmployeeProfile, ManagerProfile
from profiles.serializers import EmployeeProfileSerializer, \
    UpdateEmployeeProfileSerializer

"""
Views for updating and creating profiles
"""


# class Available


class EmployeeProfileListCreateView(generics.ListCreateAPIView):
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer


class EmployeeProfileGetDelete(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete an employee profile.
    """
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer


class EmployeeProfileUpdate(APIView):
    """
    Update employee profile.
    For days off send a list of integers, 1=Monday, 7=Sunday.
    """

    def put(self, request, pk):

        try:
            profile = EmployeeProfile.objects.get(pk=pk)
        except EmployeeProfile.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateEmployeeProfileSerializer(profile, request.data)
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



