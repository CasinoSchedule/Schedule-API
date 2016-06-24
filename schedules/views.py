from django.shortcuts import render
from rest_framework import generics, status
import datetime
import calendar

from schedules.models import Schedule, DayOfWeek, WorkDay
from schedules.serializers import DayOfWeekSerializer, ScheduleSerializer, \
    WorkDaySerializer


def create_schedule(monday):
    """
    Create a schedule along with 7 WorkDay objects, starting from the monday
    argument.
    """
    one_day = datetime.timedelta(days=1)
    #now = datetime.datetime.now()
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


class CurrentSchedules(generics.ListAPIView):
    """
    Return current and on_deck schedules. This view will check for the current
    date and create the objects if they do not yet exist.
    """

    # Just current schedule first
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        qs = []
        today = datetime.datetime.now().date()
        monday = most_recent_monday(today)
        work_day = WorkDay.objects.filter(day_date=monday).first()

        if work_day:
            # switch other schedules from current to expired.
            # set this schedule to the new current.
            current_schedule = work_day.schedule
        else:
            current_schedule = create_schedule(monday)
        qs.append(current_schedule)
        return qs


class DayOfTheWeekList(generics.ListAPIView):
    serializer_class = DayOfWeekSerializer
    queryset = DayOfWeek.objects.all()


class WorkDayList(generics.ListAPIView):
    serializer_class = WorkDaySerializer
    queryset = WorkDay.objects.all()
