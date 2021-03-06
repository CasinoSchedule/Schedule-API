from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

import datetime

from profiles.models import EmployeeProfile, ManagerProfile, Available
from schedules.models import Department, DayOfWeek, Shift, WorkDay
from schedules.views import get_or_create_schedule


class EmployeeTests(APITestCase):
    """
    Tests for employee profile list, create, and update endpoints.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(username='test_user1',
                                             password='pass_word')
        self.user2 = User.objects.create_user(username='test_user2',
                                              password='pass_word')
        self.department1 = Department.objects.create(title='d1')
        self.department2 = Department.objects.create(title='d2')

        self.manager_user = User.objects.create_user(username='manager',
                                                     password='pass_word')
        self.manager_profile = ManagerProfile.objects.create(position_title='test',
                                                             first_name='m',
                                                             last_name='n',
                                                             user=self.manager_user)
        self.manager_token = Token.objects.get(user_id=self.manager_user.id)

        for title in ['Day', 'Swing', 'Grave']:
            Available.objects.create(title=title)


        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            DayOfWeek.objects.create(title=day)

    def test_detail_delete(self):
        self.employee = EmployeeProfile.objects.create(user=self.user1,
                                                       first_name='john',
                                                       last_name='smith')
        url = reverse('employee_detail_delete', kwargs={'pk': self.employee.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.employee.first_name)

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EmployeeProfile.objects.count(), 0)

    def test_employee_list_create(self):
        EmployeeProfile.objects.create(user=self.user1,
                                       first_name='a',
                                       last_name='b',
                                       department=self.department1)
        url = reverse('employee_list_create')

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.manager_token.key)
        response = self.client.get(url + '?department=' + str(self.department1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'a')

        data = {'first_name': 'c', 'last_name': 'd',
                'department': self.department2.id,
                'user': self.user2.id}
        create_response = self.client.post(url, data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)

    def test_employee_profile_update(self):
        # change availability, regular_days_off
        employee = EmployeeProfile.objects.create(first_name='a',
                                       last_name='b',
                                       )
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.manager_token.key)

        data = {'first_name': 'aa', 'last_name': 'b',
                'regular_days_off': [DayOfWeek.objects.first().id],
                'availability': [Available.objects.first().id]
                }
        url = reverse('employee_update', kwargs={'pk': employee.pk})
        response = self.client.put(url, data, format='json')

        employee = EmployeeProfile.objects.first()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(employee.first_name, 'aa')
        self.assertEqual(employee.last_name, 'b')
        self.assertEqual(employee.regular_days_off.first().title,
                         DayOfWeek.objects.first().title)
        self.assertEqual(employee.availability.first().title,
                         Available.objects.first().title)

    def test_user_create_with_profile(self):
        new_employee = EmployeeProfile.objects.create(first_name='a',
                                                      last_name='b')
        url = reverse('user_with_profile')
        data = {'username': 'new_employee_profile', 'password': 'pass_word',
                'profile_id': new_employee.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_user = User.objects.get(username='new_employee_profile')
        self.assertEqual(new_user.employeeprofile, new_employee)

    def test_profile_check(self):
        users = [User.objects.create_user(username=str(x), password='pass_word') for x in range(1,4)]
        EmployeeProfile.objects.create(user=users[0], first_name='a', last_name='b')
        ManagerProfile.objects.create(user=users[1], first_name='c', last_name='d', position_title='e')

        url = reverse('profile_check')
        response = self.client.get(url)
        self.assertEqual(response.data['type'], 'no token')

        token = Token.objects.get(user_id=users[2].id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url)
        self.assertEqual(response.data['type'], 'no profile')

        token = Token.objects.get(user_id=users[1].id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url)
        self.assertEqual(response.data['type'], 'manager')

        token = Token.objects.get(user_id=users[0].id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(url)
        self.assertEqual(response.data['type'], 'employee')


class EmailTests(APITestCase):
    # Note: The try/except blocks are two broad for all of these views. If
    # these features get implamented then I will sharpen them up.

    def setUp(self):
        get_or_create_schedule('2016-7-4')
        self.department1 = Department.objects.create(title='d1')
        self.department2 = Department.objects.create(title='d2')

        self.employee1 = EmployeeProfile.objects.create(
            first_name='a',
            last_name='a',
            email='a@sink.sendgrid.net',
            email_notifications=True,
            department=self.department1)
        self.employee2 = EmployeeProfile.objects.create(
            first_name='b',
            last_name='b',
            email='b@sink.sendgrid.net',
            email_notifications=True,
            department=self.department1)
        self.employee3 = EmployeeProfile.objects.create(
            first_name='c',
            last_name='c',
            email='not an email',
            email_notifications=True,
            department=self.department2)

        self.manager_user = User.objects.create_user(username='manager',
                                                     password='pass_word')

        self.manager_profile = ManagerProfile.objects.create(
            position_title='test',
            first_name='m',
            last_name='n',
            user=self.manager_user)

    def test_message_employees(self):
        token = Token.objects.get(user_id=self.manager_user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse('message_employees')
        data = {"department": self.department1.id,
                "subject": "test",
                "body": "test"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, '2 emails sent')

        data = {"department": self.department2.id,
                "subject": "test",
                "body": "test"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data, 'email error')

    def test_message_available_employees(self):
        token = Token.objects.get(user_id=self.manager_user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        shift1 = Shift.objects.create(
            employee=self.employee1,
            starting_time=datetime.time(11, 0),
            day=WorkDay.objects.get(day_date=datetime.date(2016, 7, 4)))

        url = reverse('message_available_employees')
        data = {"date": "2016-7-5",
                "time": "10:00",
                "department": self.department1.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['emails sent'], 1)
        self.assertEqual(response.data['employees notified'], [('b', 'b')])

    def test_notify_new_employee(self):
        token = Token.objects.get(user_id=self.manager_user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse('notify_new_employee')
        data = {'email': 'test@sink.sendgrid.net',
                'profile_id': self.employee1.id,
                'development': True}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'email sent successfully')

        # Find an employee profile id that is not in use
        ids = EmployeeProfile.objects.values_list('id', flat=True)
        unused_id = max(ids) + 1

        data = {'email': 'test@sink.sendgrid.net',
                'profile_id': unused_id,
                'development': True}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'No employee profile found')
