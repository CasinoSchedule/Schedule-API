from django.shortcuts import render
from rest_framework import generics, status
import datetime
import calendar
from rest_framework.response import Response
from django.db.models import Count
from django.contrib.auth.models import User
import logging

from rest_framework.views import APIView

from profiles.models import EmployeeProfile
from schedules.models import Schedule, WorkDay, Shift, EOList, EOEntry, CallOut, \
    TimeOffRequest
from schedules.serializers import ScheduleSerializer, \
    WorkDaySerializer, EmployeeShiftSerializer, ShiftSerializer, \
    EmployeeShiftScheduleSerializer, MultipleShiftSerializer, \
    ShiftByDateSerializer, UserSerializer, ShiftCreateSerializer, \
    EOListSerializer, EOEntrySerializer, CallOutSerializer, \
    TimeOffRequestCreateSerializer, TimeOffRequestDisplaySerializer

from schedules.twilio_functions import twilio_shift


logger = logging.getLogger("debug_logger")


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


def print_time(time):
    """
    time: a time field string, 11:00:00
    """
    return time.strftime("%I:%M %p")


def print_date(date):
    return date.strftime('%A, %B %d')


def phone_notify_employees(data):

    employee_ids = set([x.employee.id for x in data])
    logger.debug("employee ids: {}".format(employee_ids))
    for person in EmployeeProfile.objects.filter(id__in=employee_ids,
                                           phone_notifications=True).all():
        logger.debug("person: {}".format(person))
        logger.debug("person id: {}".format(person.id))
        #logger.debug("person: {}".format(person))

        message = 'You have new shifts posted.\n\n'
        matches = [x for x in data if x.employee.id == person.id]
        logger.debug("matches: {}".format(matches))

        for match in matches:
            date = WorkDay.objects.get(id=match.day.id).day_date
            time = match.starting_time
            message += "{} at {}\n".format(
                print_date(date),
                print_time(time)
            )

        num = person.phone_number
        twilio_shift(num, message)


def date_string_to_datetime(date_string, time=None):
    """
    Turns a date string like '2016-6-20' into a Date object.
    time must only be hours and minutes.
    """
    year, month, day = [int(x) for x in date_string.split('-')]
    if time:
        hour = int(time.split(':')[0])
        return datetime.datetime(year, month, day, hour)

    return datetime.datetime(year, month, day)


def is_past(date, time):
    """
    Return True if the date and time passed in is later than current moment.
    """
    requested_time = date_string_to_datetime(date, time)
    return datetime.datetime.now() > requested_time


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

        qs = self.request.user.employeeprofile.shift_set.filter(
            day__day_date__gte=start_day,
            day__day_date__lte=final_day,
            visible=True
        )

        return qs.order_by("day__day_date")


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


class ShiftCreateManyByDate(APIView):
    """
    Create and/or update multiple schedules with one POST request, using the
     date parameter.

     Currently an employee can only have one shift per day. This will probably
     change in the future.
    Example: [
    {"starting_time": "11:00:00", "day": "2016-6-20", "employee": 1},
     {"starting_time": "11:00:00", "day": "2016-6-21", "employee": 1}
     ]
    """

    def post(self, request, format=None):

        # If starting time is "" then delete shift if it exists.

        updated_data = []
        for item in request.data:

            # if is_past(item['day'], item['starting_time']):
            #     return Response("Changing past shifts is forbidden.",
            #                     status=status.HTTP_403_FORBIDDEN)

            workday = WorkDay.objects.filter(day_date=item['day']).first()
            if workday:
                item['day'] = workday.id
            else:
                get_or_create_schedule(item['day'])
                item['day'] = WorkDay.objects.get(day_date=item['day']).id

            if item['starting_time']:
                updated_data.append(item)
            else:
                shift = Shift.objects.filter(day=item['day'],
                                             employee=item['employee']
                                             ).first()
                if shift:
                    shift.delete()

        serializer = ShiftCreateSerializer(data=updated_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ActivateShiftWeek(APIView):
    """
    POST a date. All shifts for that week will be made visible to employees
    and they will be notified.
    example: {"date": "2016-6-20"}
    """

    def post(self, request, format=None):
        schedule = get_or_create_schedule(request.data['date'])
        first = schedule.workday_set.first()
        last = schedule.workday_set.last()
        shifts = Shift.objects.filter(day__day_date__gte=first.day_date,
                                      day__day_date__lte=last.day_date,
                                      visible=False
                                      ).all()
        logger.debug("number shifts: {}".format(shifts.count()))
        phone_notify_employees(shifts)
        amount = shifts.count()
        shifts.update(visible=True)

        logger.debug("Starting day: {}".format(first.day_date))
        logger.debug("Ending day: {}".format(last.day_date))

        logger.debug("amount: {}".format(amount))

        return Response(
            {'amount updated': amount},
            status=status.HTTP_200_OK
        )


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [
    #     permissions.AllowAny
    # ]


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RetrieveEOList(APIView):
    """
    Post a date to get the EO list for that day. Will add more parameters
    later for department and shift.
    """

    def post(self, request, format=None):
        date = date_string_to_datetime(request.data['date'])
        workday = WorkDay.objects.filter(day_date=date).first()

        if not workday:
            get_or_create_schedule(request.data['date'])

        # Only one shift per workday to start.
        eo_list = EOList.objects.filter(day=workday).first()
        if not eo_list:
            eo_list = EOList.objects.create(day=workday)
        serializer = EOListSerializer(eo_list)
        return Response(serializer.data)


class CreateEOEntry(generics.CreateAPIView):
    """
    Create a new entry on an EO list. POST the shift and EO list ids.

    Note: I need to add a check requiring the dates to match.
    """
    queryset = EOEntry.objects.all()
    serializer_class = EOEntrySerializer

    def perform_create(self, serializer):

        shift_id = self.request.data['shift']
        eo_list_id = self.request.data['eo_list']

        serializer.save(shift=Shift.objects.get(pk=shift_id),
                        eo_list=EOList.objects.get(pk=eo_list_id))


class EOListList(generics.ListAPIView):
    queryset = EOList.objects.all()
    serializer_class = EOListSerializer


class CallOutListCreate(generics.ListCreateAPIView):
    """
    To create a call out send the shift.id and a status.
    status: 1:Pending, 2:Approved, 3:Rejected
    call_type: 1:unpaid, 2:pto, 3:fmla
    example: {"shift": 75, "status": 1, "call_type": 1}
    """
    queryset = CallOut.objects.all()
    serializer_class = CallOutSerializer


class CallOutDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = CallOut.objects.all()
    serializer_class = CallOutSerializer


class TimeOffRequestCreate(generics.ListCreateAPIView):
    """
    Create a time off request with a list of days and a status, 1=Pending.
    example: {"days": ["2016-7-1", "2016-7-2"], "status": 1}
    Employee will be set to the requesting user's employee profile.
    """
    queryset = TimeOffRequest.objects.all()
    serializer_class = TimeOffRequestCreateSerializer

    def perform_create(self, serializer):
        if not self.request.user.id:
            return Response("No employee token sent", status=status.HTTP_400_BAD_REQUEST)

        employee = self.request.user.employeeprofile

        # Note: need to add check for WorkDay

        dates = []
        for day in self.request.data['days']:
            dates.append(WorkDay.objects.get(day_date=day).id)

        serializer.save(employee=employee,
                        days=dates)


class TimeOffRequestList(generics.ListAPIView):
    queryset = TimeOffRequest.objects.all()
    serializer_class = TimeOffRequestDisplaySerializer


# class ShiftCreateByDate(generics.CreateAPIView):
#     """
#     Create a Shift object using a date, rather than a WorkDay id number.
#     example: {"starting_time": "11:00:00", "day": "2016-6-20", "employee": 1}
#     """
#     queryset = Shift.objects.all()
#     serializer_class = ShiftByDateSerializer
#
#     def perform_create(self, serializer):
#         date = self.request.data["day"]
#         day = WorkDay.objects.get(day_date=date)
#         serializer.save(day=day)


#
# class ShiftCreateMany(APIView):
#     """
#     Mark, I can change the inputs to date objects if that would be easier.
#
#     Create multiple schedules with one POST request.
#     Example: [
#     {"starting_time": "11:00:00", "day": 20, "employee": 1},
#      {"starting_time": "11:00:00", "day": 21, "employee": 1}
#      ]
#     """
#
#     def post(self, request, format=None):
#         serializer = ShiftCreateSerializer(data=request.data, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


