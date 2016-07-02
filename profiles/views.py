from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import generics, status

from profiles.models import EmployeeProfile, ManagerProfile
from profiles.serializers import EmployeeProfileSerializer

"""
Views for updating and creating profiles
"""


class EmployeeProfileListCreateView(generics.ListAPIView):
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer


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



