from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token


from profiles.models import EmployeeProfile, ManagerProfile
from schedules.models import WorkDay, Shift


class TestSetup(APITestCase):

    def new_employee(self, user):
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


class EmployeeMonthTest(TestSetup):

    def setUp(self):
        self.user = User.objects.create_user(username='test user',
                                             password='blahblah')

        self.employee = self.new_employee(self.user)
        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        self.employee_url = reverse('days_by_month')
        self.scheduler_url = reverse('multiple_shift_by_date')

    def test_initial_shift(self):
        a=1

        response = self.client.get(self.employee_url + '?month=6&year=2016',
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        self.assertEqual(Shift.objects.count(), 0)

    def create_shifts(self):

        data = [
            {"starting_time": "11:00:00", "day": "2016-6-20", "employee": 1},
            {"starting_time": "11:00:00", "day": "2016-6-21", "employee": 1}
        ]

        response = self.client.post(self.scheduler_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Shift.objects.count(), 2)
