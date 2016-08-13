from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

import datetime

from profiles.models import EmployeeProfile, ManagerProfile
from schedules.models import WorkDay, Shift, Department, Area, EOList, EOEntry
from schedules.views import most_recent_monday, next_monday, print_time, \
    print_date, date_string_to_datetime, is_past, get_or_create_schedule, \
    get_week_shifts, change_string_date, update_shift_date, check_shift_overlap


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


class ShiftFunctionTests(TestCase):
    def setUp(self):
        self.employee1 = EmployeeProfile.objects.create(first_name='a',
                                                        last_name='b')
        self.week1 = get_or_create_schedule('2016-7-4')
        self.week2 = get_or_create_schedule('2016-7-11')
        self.shift1 = Shift.objects.create(employee=self.employee1,
                                           day=WorkDay.objects.get(day_date='2016-7-4'),
                                           starting_time=datetime.time(11, 0))
        self.shift2 = Shift.objects.create(employee=self.employee1,
                                           day=WorkDay.objects.get(
                                               day_date='2016-7-5'),
                                           starting_time=datetime.time(11, 0))
        self.shift3 = Shift.objects.create(employee=self.employee1,
                                           day=WorkDay.objects.get(
                                               day_date='2016-7-12'),
                                           starting_time=datetime.time(11, 0))

    def test_get_week_shifts(self):
        first_results = get_week_shifts('2016-7-4')
        self.assertEqual(first_results.count(), 2)

        second_results = get_week_shifts('2016-7-11')
        self.assertEqual(second_results.count(), 1)

        third_results = get_week_shifts('2016-8-1')
        self.assertEqual(third_results.count(), 0)

    def test_change_string_date(self):
        date_string = '2016-1-20'
        self.assertEqual(change_string_date(date_string, 20), '2016-2-9')
        self.assertEqual(change_string_date(date_string, -40), '2015-12-11')

    def test_update_shift_date(self):
        self.assertEqual(self.shift1.day.day_date, datetime.date(2016, 7, 4))
        update_shift_date(self.shift1, 8)
        self.assertEqual(self.shift1.day.day_date, datetime.date(2016, 7, 12))

    def test_check_shift_overlap(self):
        self.assertTrue(check_shift_overlap(self.shift2, Shift.objects.all()))
        update_shift_date(self.shift2, 7)
        self.assertFalse(check_shift_overlap(self.shift2, Shift.objects.all()))


class EmployeeMonthTest(TestSetup):

    def setUp(self):
        self.user = User.objects.create_user(username='test user',
                                             password='blahblah')

        self.employee = self.new_employee(self.user)
        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        self.employee_url = reverse('days_by_month')
        self.scheduler_url = reverse('multiple_shift_by_date')

        self.manager_user = User.objects.create_user(username='manager',
                                                     password='blahblah')

        self.manager_profile = ManagerProfile.objects.create(first_name='a',
                                                         last_name='b',
                                                         user=self.manager_user)

    def test_initial_shift(self):

        response = self.client.get(self.employee_url + '?month=6&year=2016',
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        self.assertEqual(Shift.objects.count(), 0)

    def test_create_delete_shifts(self):
        token = Token.objects.get(user_id=self.manager_user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data = [
            {"starting_time": "11:00:00", "day": "2016-6-20", "employee": self.employee.id},
            {"starting_time": "11:00:00", "day": "2016-6-21", "employee": self.employee.id}
        ]

        response = self.client.post(self.scheduler_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shift.objects.count(), 2)

        data = [
            {"starting_time": "", "day": "2016-6-20", "employee": self.employee.id},
            {"starting_time": "", "day": "2016-6-21", "employee": self.employee.id}
        ]

        response = self.client.post(self.scheduler_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shift.objects.count(), 0)

    def test_visible_activate(self):
        """
        Test that shifts are not visible to employee by default and that
        they can be made so with ActivateShift Week.
        """
        # make shift
        # check that none are returned
        # make visible, checking response amount
        # check that shifts are returned
        data = [
            {"starting_time": "11:00:00", "day": "2016-6-20", "employee": self.employee.id},
            {"starting_time": "11:00:00", "day": "2016-6-21", "employee": self.employee.id}
        ]

        unauth_response = self.client.post(self.scheduler_url, data, format='json')
        self.assertEqual(unauth_response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(self.employee_url + '?month=6&year=2016',
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        token = Token.objects.get(user_id=self.manager_user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.post(self.scheduler_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shift.objects.count(), 2)
        self.assertFalse(Shift.objects.first().visible)

        activate_url = reverse('publish_shift_week')
        data = {'date': '2016-6-20'}
        response = self.client.post(activate_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount updated'], 2)
        self.assertTrue(Shift.objects.first().visible)


class ShiftWeekTest(APITestCase):
    """
    Tests for the ShiftWeekList view to check for WorkDay creation and
    shift filtering.
    """

    def setUp(self):
        self.url = reverse('schedule_shifts')
        self.user = User.objects.create_user(username='test user',
                                             password='blahblah')
        self.employee = EmployeeProfile.objects.create(user=self.user,
                                                       first_name='a',
                                                       last_name='b',
                                                       position_title='c')

        self.manager_user = User.objects.create_user(username='manager',
                                                     password='blahblah')
        self.manager_profile = ManagerProfile.objects.create(first_name='a',
                                                             last_name='b',
                                                             user=self.manager_user)

    def test_shift_filter(self):
        token = Token.objects.get(user_id=self.manager_user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = self.client.get(self.url + '?date=2016-6-20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        response = self.client.get(self.url + '?date=2016-6-27')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        self.assertEqual(WorkDay.objects.count(), 14)

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


class AreaTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test user',
                                             password='blahblah')
        self.manager = ManagerProfile.objects.create(user=self.user,
                                                     position_title='test')
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
        self.assertEqual(response.data[1]['title'], 'test_area')

    def test_station_list_create(self):

        not_allowed = self.client.get(self.station_url)
        self.assertEqual(not_allowed.status_code, status.HTTP_401_UNAUTHORIZED)

        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data = {'title': 'test_station', 'area': Area.objects.first().id}
        post_response = self.client.post(self.station_url, data, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class EOListTests(APITestCase):
    def setUp(self):
        get_or_create_schedule('2016-7-4')
        self.employee = EmployeeProfile.objects.create(first_name='a',
                                                       last_name='b')
        self.eo_list1 = EOList.objects.create(day=WorkDay.objects.get(day_date=datetime.date(2016, 7, 4)))

        self.shift1 = Shift.objects.create(starting_time=datetime.time(11, 0),
                                           employee=self.employee,
                                           day=WorkDay.objects.get(day_date=datetime.date(2016, 7, 4)))

        self.shift2 = Shift.objects.create(starting_time=datetime.time(11, 0),
                                           employee=self.employee,
                                           day=WorkDay.objects.get(
                                               day_date=datetime.date(2016, 7,
                                                                      5)))

    def test_eolist_detail(self):
        url = reverse('retrieve_eo_list')

        data = {'date': '2016-7-4'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {'date': '2016-7-5'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EOList.objects.count(), 2)

    def test_entry_create(self):
        url = reverse('create_eo_entry')

        data = {'shift': self.shift1.id, 'eo_list': self.eo_list1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'shift': self.shift2.id, 'eo_list': self.eo_list1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(EOEntry.objects.count(), 1)

        # Need to correct the response if object not created.


class TimeOffRequestTests(APITestCase):

    def setUp(self):
        pass

    def test_timeoff_create(self):
        pass
