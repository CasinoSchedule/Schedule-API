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
from schedules.models import WorkDay, Shift


class TestSetup(APITestCase):

    def new_employee(self, name):
        user = User.objects.create_user(username=name,
                                        password='blahblah')
        return EmployeeProfile.objects.create(user=user,
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

    def initialize_week(self, date):
        # date example: 2016-6-20
        self.url = reverse("schedule_shifts")
        response = self.client.get(self.url + "?date={}".format(date))



class ShiftTest(TestSetup):

    # non-overlapping, return correct response
    # shift deletion

    def setUp(self):
        self.employee = self.new_employee('test')
        self.initialize_week("2016-6-20")

    def test_shift_create_delete(self):
        url = reverse("list_create_shift")
        data = {
            "starting_time": "10:00:00",
            "day": WorkDay.objects.first().id,
            "employee": EmployeeProfile.objects.first().id
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shift.objects.count(), 1)

        delete_url = reverse('shift_retrieve_delete',
                             kwargs = {'pk': Shift.objects.first().pk})

        response = self.client.delete(delete_url)
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Shift.objects.count(), 0)

    def test_multiple_shift_create(self):
        url = reverse("shift_create_many")
        data = [
            {
                "starting_time": "10:00:00",
                "day": WorkDay.objects.first().id,
                "employee": EmployeeProfile.objects.first().id
            },
            {
                "starting_time": "10:00:00",
                "day": WorkDay.objects.last().id,
                "employee": EmployeeProfile.objects.first().id
            }
        ]
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shift.objects.count(), 2)
