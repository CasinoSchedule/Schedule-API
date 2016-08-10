from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

import datetime


from profiles.models import EmployeeProfile, ManagerProfile
from schedules.models import WorkDay, Shift, Department, Area
from schedules.views import most_recent_monday, next_monday, print_time, \
    print_date, date_string_to_datetime, is_past, get_or_create_schedule


class TestSetup(APITestCase):

    def new_employee(self, user):
        return EmployeeProfile.objects.create(user=user,
                                       employee_id="123",
                                       phone_number="123",
                                       email="123"
                                       )

    def new_manager(self, user):
        return ManagerProfile.objects.create(user=user,
                                       position_title="test"
                                       )


class HelperFunctionTests(TestCase):

    def test_get_or_create_schedule(self):
        get_or_create_schedule('2016-7-1')
        days = WorkDay.objects.all().order_by('day_date')
        self.assertEqual(days.count(), 7)
        self.assertEqual(days.first().day_date, datetime.date(2016, 6, 27))
        self.assertEqual(days.last().day_date, datetime.date(2016, 7, 3))


    def test_most_recent_monday(self):
        thursday = datetime.date(2016, 7, 28)
        monday = datetime.date(2016, 7, 25)
        sunday = datetime.date(2016, 7, 1)

        self.assertEqual(most_recent_monday(thursday),
                         datetime.date(2016, 7, 25))
        self.assertEqual(most_recent_monday(monday),
                         monday)
        self.assertEqual(most_recent_monday(sunday),
                         datetime.date(2016, 6, 27))

    def test_next_monday(self):
        thursday = datetime.date(2016, 7, 28)
        monday = datetime.date(2016, 7, 25)
        sunday = datetime.date(2016, 7, 1)

        self.assertEqual(next_monday(thursday),
                         datetime.date(2016, 8, 1))
        self.assertEqual(next_monday(monday),
                         monday)
        self.assertEqual(next_monday(sunday),
                         datetime.date(2016, 7, 4))

    def test_print_time(self):
        self.assertEqual(print_time(datetime.time(11, 0)),
                         '11:00AM')
        self.assertEqual(print_time(datetime.time(17, 15)),
                         '5:15PM')

    def test_print_date(self):
        self.assertEqual(print_date(datetime.date(2016, 7, 28)),
                         'Thursday, July 28')
        self.assertEqual(print_date(datetime.date(2016, 8, 1)),
                         'Monday, August 1')

    # test phone notify
    # test email notify

    def test_date_string_to_datetime(self):
        self.assertEqual(date_string_to_datetime('2011-7-3'),
                         datetime.datetime(2011, 7, 3))
        self.assertEqual(date_string_to_datetime('1999-10-5'),
                         datetime.datetime(1999, 10, 5))

    def test_is_past(self):
        old_date = '2010-6-6'
        future_date = '3010-1-1'
        time = '11:00'
        self.assertTrue(is_past(old_date, time))
        self.assertFalse(is_past(future_date, time))


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

        response = self.client.get(self.employee_url + '?month=6&year=2016',
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        self.assertEqual(Shift.objects.count(), 0)

    def create_delete_shifts(self):

        data = [
            {"starting_time": "11:00:00", "day": "2016-6-20", "employee": 1},
            {"starting_time": "11:00:00", "day": "2016-6-21", "employee": 1}
        ]

        response = self.client.post(self.scheduler_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Shift.objects.count(), 2)

        data = [
            {"starting_time": "", "day": "2016-6-20", "employee": 1},
            {"starting_time": "", "day": "2016-6-21", "employee": 1}
        ]

        response = self.client.post(self.scheduler_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Shift.objects.count(), 0)

    def test_visible(self):
        """
        Test that shifts are not visible to employee by default and that
        they can be made so with ActivateShift Week.
        """
        # make shift
        # check that none are returned
        # make visible, checking response amount
        # check that shifts are returned
        data = [
            {"starting_time": "11:00:00", "day": "2016-6-20", "employee": 1},
            {"starting_time": "11:00:00", "day": "2016-6-21", "employee": 1}
        ]

        # Need to add token

        unauth_response = self.client.post(self.scheduler_url, data, format='json')
        self.assertEqual(unauth_response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(self.employee_url + '?month=6&year=2016',
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        # self.assertEqual(Shift.objects.count(), 2)



class ShiftWeekTest(TestSetup):
    """
    Tests for the ShiftWeekList view to check for WorkDay creation and
    shift filtering.
    """

    def setUp(self):
        self.url = reverse('schedule_shifts')
        self.user = User.objects.create_user(username='test user',
                                             password='blahblah')
        self.employee = self.new_employee(self.user)

    def initial_query_test(self):
        response = self.client.get(self.url + '?date=2016-6-20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        response = self.client.get(self.url + '?date=2016-6-27')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        self.assertEqual(WorkDay.objects.all(), 14)

    def shift_filter_test(self):
        shifts = [Shift.objects.create(employee=self.employee,
                                 day=w,
                                 starting_time='11:00'
                                 ) for w in WorkDay.objects.all()]

        response = self.client.get(self.url + '?date=2016-6-20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)

        Shift.objects.last().delete()
        response = self.client.get(self.url + '?date=2016-6-27')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)


class AreaTest(TestSetup):

    def setUp(self):
        self.user = User.objects.create_user(username='test user',
                                             password='blahblah')
        self.manager = self.new_manager(self.user)
        self.list_url = reverse('area_list_create')
        self.station_url = reverse('station_list_create')
        self.department = Department.objects.create(title='test')
        self.area1 = Area.objects.create(title='test_area',
                                         department=self.department)

    def test_area_list_create(self):

        not_allowed = self.client.get(self.list_url)
        self.assertEqual(not_allowed.status_code, status.HTTP_401_UNAUTHORIZED)

        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data = {'title': 'test_area', 'department': self.department.id}
        post_response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_station_list_create(self):

        not_allowed = self.client.get(self.station_url)
        self.assertEqual(not_allowed.status_code, status.HTTP_401_UNAUTHORIZED)

        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data = {'title': 'test_station', 'area':Area.objects.first().id}
        post_response = self.client.post(self.station_url, data, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)



