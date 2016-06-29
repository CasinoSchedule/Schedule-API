from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token


# EmployeeShiftsByMonth: Check that date range in correct, as well as user
# filtering.


# shift creation
from profiles.models import EmployeeProfile, ManagerProfile


class TestSetup(APITestCase):

    def new_employee(self, name):
        user = User.objects.create_user(username=name,
                                        password='blahblah')
        EmployeeProfile.objects.create(user=user,
                                       employee_id="123",
                                       phone_number="123",
                                       email="123"
                                       )

    def new_manager(self, name):
        user = User.objects.create_user(username=name,
                                        password='blahblah')

        ManagerProfile.objects.create(user=user,
                                       position_title="test"
                                       )


class ShiftTest(TestSetup):
    # shift creation
    # non-overlapping, return correct response
    # shift deletion

    pass


