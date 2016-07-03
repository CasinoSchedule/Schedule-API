from django.shortcuts import render
from rest_framework import generics, status
import datetime
import calendar
from rest_framework.response import Response
from django.db.models import Count
from django.contrib.auth.models import User

from rest_framework.views import APIView

from profiles.models import EmployeeProfile
from schedules.models import Schedule, WorkDay, Shift
from schedules.serializers import ScheduleSerializer, \
    WorkDaySerializer, EmployeeShiftSerializer, ShiftSerializer, \
    EmployeeShiftScheduleSerializer, MultipleShiftSerializer, \
    ShiftByDateSerializer, UserSerializer, ShiftCreateSerializer

from schedules.twilio_functions import twilio_shift


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
        WorkDay.objects.create(day_date=date,
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
    date param is a string, ie. "2016-6-20"
    """
    dates = date.split("-")
    dates = [int(x) for x in dates]
    working_date = datetime.date(dates[0], dates[1], dates[2])


    monday = most_recent_monday(working_date)
    work_day = WorkDay.objects.filter(day_date=monday).first()

    if work_day:
        current_schedule = work_day.schedule
    else:
        current_schedule = create_schedule(monday)

    return current_schedule


def phone_notify_employees(data):
    # Add shift information later.

    employee_ids = set([x['employee'] for x in data])
    for employee in EmployeeProfile.objects.filter(id__in=employee_ids,
                                           phone_notifications=True):
        num = employee.phone_number
        twilio_shift(num)


class EmployeeShiftsByMonth(generics.ListAPIView):
    """
    Takes a month and year and returns schedules for the requesting employee.
    The time frame is an expanded six week calendar view of the month that will
    start from Sunday in the prior month and run into the following month.


    example GET: schedules/employeemonth/?month=6&year=2016
    """
    serializer_class = EmployeeShiftSerializer

    def get_queryset(self):

        if not self.request.user.id:
            return []

        year, month = int(self.request.query_params["year"]), int(self.request.query_params["month"])
        first_weekday = datetime.date(year, month, 1).weekday()
        preceding_days = (first_weekday + 1) % 7
        month_days = calendar.monthrange(year, month)[1]
        trailing_days = 42 - month_days - preceding_days

        start_day = datetime.date(year, month, 1) - datetime.timedelta(days=preceding_days)
        final_day = datetime.date(year, month, month_days) + datetime.timedelta(days=trailing_days)

        # qs = self.request.user.employeeprofile.shift_set.filter(
        #     day__day_date__gte=start_day,
        #     day__day_date__lte=final_day
        # )
        #
        # return qs.order_by("day__day_date")

        """ placeholder """
        qs = []
        for i in range(42):
            current = start_day + datetime.timedelta(days=i)
            shift = Shift.objects.filter(day__day_date=current).first()
            if shift:
                qs.append(shift)
            else:
                qs.append({"calendar_date": current,
                           "starting_time": None,
                           "length": None,
                           "employee": None,
                           "end_time": None,
                           "day": None
                           })
        return qs



class CustomShift(APIView):

    def get(self, request, format=None):
        data = Shift.objects.first()
        answer = {str(data.calendar_date): "test"}
        return Response(answer)


class ListCreateShift(generics.ListCreateAPIView):
    serializer_class = ShiftSerializer
    queryset = Shift.objects.all()
    #authentication_classes = []


class ShiftRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShiftSerializer
    queryset = Shift.objects.all()


class ShiftWeekList(generics.ListAPIView):
    """
    Accepts a date querystring. Creates or retrieves the dates for that work
    week and returns all shifts that fall on those days.

    Used for the managers schedule view and generating new WorkDays.

    example: weekshift/?date=2016-6-20
    """
    serializer_class = EmployeeShiftSerializer

    def get_queryset(self):
        if not self.request.query_params.get("date"):
            return []

        # dates = self.request.query_params["date"].split("-")
        # dates = [int(x) for x in dates]
        # working_date = datetime.date(dates[0], dates[1], dates[2])
        # current_schedule = get_or_create_schedule(working_date)

        current_schedule = get_or_create_schedule(self.request.query_params["date"])

        days = current_schedule.workday_set.order_by("day_date")
        start = days.first().day_date
        finish = days.last().day_date

        qs = Shift.objects.filter(day__day_date__gte=start,
                                  day__day_date__lte=finish)

        return qs


class ScheduleDetail(generics.RetrieveAPIView):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()


class WorkDayList(generics.ListAPIView):
    serializer_class = WorkDaySerializer
    queryset = WorkDay.objects.all()


class WorkDayDetail(generics.RetrieveAPIView):
    serializer_class = WorkDaySerializer
    queryset = WorkDay.objects.all()


class ShiftCreateMany(APIView):
    """
    Mark, I can change the inputs to date objects if that would be easier.

    Create multiple schedules with one POST request.
    Example: [
    {"starting_time": "11:00:00", "day": 20, "employee": 1},
     {"starting_time": "11:00:00", "day": 21, "employee": 1}
     ]
    """

    def post(self, request, format=None):
        serializer = ShiftCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShiftCreateManyByDate(APIView):
    """
    Create multiple schedules with one POST request, using the date parameter.
    Example: [
    {"starting_time": "11:00:00", "day": "2016-6-20", "employee": 1},
     {"starting_time": "11:00:00", "day": "2016-6-21", "employee": 1}
     ]
    """
    # New schedules and WorkDays are created if needed.

    def post(self, request, format=None):

        updated_data = []
        for item in request.data:
            workday = WorkDay.objects.filter(day_date=item['day']).first()
            if workday:
                item['day'] = workday.id
            else:
                get_or_create_schedule(item['day'])
                item['day'] = WorkDay.objects.get(day_date=item['day']).id

            #item['day'] = WorkDay.objects.get(day_date=item['day']).id
            updated_data.append(item)

        serializer = ShiftCreateSerializer(data=updated_data, many=True)
        if serializer.is_valid():
            serializer.save()
            phone_notify_employees(request.data)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ShiftCreateByDate(generics.CreateAPIView):
    """
    Create a Shift object using a date, rather than a WorkDay id number.
    example: {"starting_time": "11:00:00", "day": "2016-6-20", "employee": 1}
    """
    queryset = Shift.objects.all()
    serializer_class = ShiftByDateSerializer

    def perform_create(self, serializer):
        date = self.request.data["day"]
        day = WorkDay.objects.get(day_date=date)
        serializer.save(day=day)


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [
    #     permissions.AllowAny
    # ]


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# class CurrentSchedules(generics.ListAPIView):
#     """
#     Return current and on_deck schedules. This view will check for the current
#     date and create the objects if they do not yet exist.
#     """
#
#     serializer_class = ScheduleSerializer
#
#     def get_queryset(self):
#         qs = []
#         today = datetime.datetime.now().date()
#         current_schedule = get_or_create_schedule(today)
#         # switch other schedules from current to expired.
#         # set this schedule to the new current.
#         current_schedule.status = "current"
#
#         second_date = today + datetime.timedelta(days=7)
#         second_schedule = get_or_create_schedule(second_date)
#         second_schedule.status = "on_deck"
#
#         qs.append(current_schedule)
#         qs.append(second_schedule)
#         return qs


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
