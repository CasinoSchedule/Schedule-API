from django.shortcuts import render
from rest_framework import generics, status
import datetime
import calendar
from rest_framework.response import Response

from rest_framework.views import APIView

from schedules.models import Schedule, DayOfWeek, WorkDay, Shift
from schedules.serializers import DayOfWeekSerializer, ScheduleSerializer, \
    WorkDaySerializer, EmployeeShiftSerializer, ShiftSerializer


def create_schedule(monday):
    """
    Create a schedule along with 7 WorkDay objects, starting from the monday
    argument.
    """
    # Add a check to verify monday.

    one_day = datetime.timedelta(days=1)
    new_schedule = Schedule.objects.create()

    for i in range(7):
        date = monday + (one_day * i)
        day = DayOfWeek.objects.get(
            python_int=date.weekday()
        )
        WorkDay.objects.create(day_date=date, day_of_the_week=day,
                               schedule=new_schedule)
    return new_schedule


def most_recent_monday(date):
    """
    Return the date of the most recent monday, return the arg if it is a
     monday.
    param date: is a datetime.datetime.date object.
    """
    one_day = datetime.timedelta(days=1)
    return date - (date.weekday() * one_day)


def next_monday(date):
    one_day = datetime.timedelta(days=1)
    return date + ((7 - date.weekday()) * one_day)


def get_or_create_schedule(date):
    """
    Retrieve or create the schedule that contains the date argument.
    """
    monday = most_recent_monday(date)
    work_day = WorkDay.objects.filter(day_date=monday).first()

    if work_day:
        current_schedule = work_day.schedule
    else:
        current_schedule = create_schedule(monday)

    return current_schedule


class EmployeeShiftsByMonth(generics.ListAPIView):
    """
    Takes a month and year and returns a list of objects, one for each day of
    the month with the associated shifts.

    example POST: {"month": 6, "year": 2016}
    """
    serializer_class = EmployeeShiftSerializer

    def get_queryset(self):

        year, month = int(self.request.query_params["year"]), int(self.request.query_params["month"])
        first_weekday = datetime.date(year, month, 1).weekday()
        preceding_days = (first_weekday + 1) % 7
        month_days = calendar.monthrange(year, month)[1]
        trailing_days = 42 - month_days - preceding_days

        start_day = datetime.date(year, month, 1) - datetime.timedelta(days=preceding_days)
        final_day = datetime.date(year, month, month_days) + datetime.timedelta(days=trailing_days)

        qs = self.request.user.employeeprofile.shift_set.filter(
            day__day_date__gte=start_day,
            day__day_date__lte=final_day
        )
        return qs


class ListCreateShift(generics.ListCreateAPIView):
    serializer_class = ShiftSerializer
    queryset = Shift.objects.all()
    #authentication_classes = []


class WeekShiftsByEmployee(generics.ListAPIView):
    """
    Accepts a date querystring and returns a list of objects, each with an
    employee and the shifts they are scheduled that week.
    """
    pass


# class ArbitraryDateSchedule(generics.RetrieveAPIView):
#     """
#     Takes a date request in a querystring and returns the schedule for that
#     week.
#     Example: schedules/bydate/?date=2015-01-01
#     """
#
#     serializer_class = ScheduleSerializer
#
#     def get_queryset(self):
#
#         date_requested = self.request.query_params["date"]
#
#         a = 1
#         return super().get_queryset()


class CurrentSchedules(generics.ListAPIView):
    """
    Return current and on_deck schedules. This view will check for the current
    date and create the objects if they do not yet exist.
    """

    serializer_class = ScheduleSerializer

    def get_queryset(self):
        qs = []
        today = datetime.datetime.now().date()
        current_schedule = get_or_create_schedule(today)
        # switch other schedules from current to expired.
        # set this schedule to the new current.
        current_schedule.status = "current"

        second_date = today + datetime.timedelta(days=7)
        second_schedule = get_or_create_schedule(second_date)
        second_schedule.status = "on_deck"

        qs.append(current_schedule)
        qs.append(second_schedule)
        return qs


class ScheduleDetail(generics.RetrieveAPIView):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()


class DayOfTheWeekList(generics.ListAPIView):
    serializer_class = DayOfWeekSerializer
    queryset = DayOfWeek.objects.all()


class WorkDayList(generics.ListAPIView):
    serializer_class = WorkDaySerializer
    queryset = WorkDay.objects.all()


class WorkDayDetail(generics.RetrieveAPIView):
    serializer_class = WorkDaySerializer
    queryset = WorkDay.objects.all()
