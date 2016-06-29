from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from profiles.models import EmployeeProfile
from profiles.serializers import EmployeeProfileSerializer

"""
Views for updating and creating profiles
"""


class EmployeeProfileListCreateView(generics.ListAPIView):
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer
