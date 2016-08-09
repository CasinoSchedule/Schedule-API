import calendar
import datetime
import logging
import random

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import EmployeeProfile
from schedules.models import Schedule, WorkDay, Shift, EOList, EOEntry,\
    CallOut, TimeOffRequest, Area, Station, print_date, print_time, \
    ShiftTemplate
from schedules.permissions import IsManager, IsEmployee
from schedules.sendgrid_functions import email_shift
from schedules.serializers import WorkDaySerializer, EmployeeShiftSerializer,\
    ShiftCreateSerializer, EOListSerializer, EOEntrySerializer,\
    CallOutSerializer, TimeOffRequestCreateSerializer,\
    TimeOffRequestDisplaySerializer, AreaSerializer, StationSerializer, \
    ShiftTemplateSerializer

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
    """
    Return the following monday, or param if date is monday.
    """
    if date.weekday():
        one_day = datetime.timedelta(days=1)
        return date + ((7 - date.weekday()) * one_day)
    else:
        return date


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

    employee_ids = set([x.employee.id for x in data])

    for person in EmployeeProfile.objects.filter(id__in=employee_ids,
                                           phone_notifications=True).all():

        message = 'You have new shifts posted.\n\n'
        matches = [x for x in data if x.employee.id == person.id]

        for match in matches:
            date = WorkDay.objects.get(id=match.day.id).day_date
            time = match.starting_time
            message += "{} at {}\n".format(
                print_date(date),
                print_time(time)
            )

        num = person.phone_number
        twilio_shift(num, message)


def email_notify_employees(data):

    employee_ids = set([x.employee.id for x in data])

    for person in EmployeeProfile.objects.filter(id__in=employee_ids,
                                                 email_notifications=True
                                                 ).all():

        message = ''
        matches = [x for x in data if x.employee.id == person.id]

        for match in matches:
            date = WorkDay.objects.get(id=match.day.id).day_date
            time = match.starting_time
            message += "{} at {}\n".format(
                print_date(date),
                print_time(time)
            )

        profile_email = person.email
        email_shift(profile_email, message)


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
    :param date: calendar_date, ie. '2016-6-20'
    :param time: time string, ie. '11:00'
    :return: True if the date and time passed in is later than current moment.
    """
    requested_time = date_string_to_datetime(date, time)
    return datetime.datetime.now() > requested_time


def get_week_shifts(date, department=None):
    """
    :param date: date string
    :param department: optional department id number
    :return: a queryset of all shifts for a given week + department
    """
    current_schedule = get_or_create_schedule(
        date)

    days = current_schedule.workday_set.order_by("day_date")
    start = days.first().day_date
    finish = days.last().day_date

    qs = Shift.objects.filter(day__day_date__gte=start,
                              day__day_date__lte=finish)

    if department:
        qs = qs.filter(employee__department_id=int(department))
    return qs


def change_string_date(date, days):
    """
    :param date: string date
    :param days: number of days to change the date by
    :return: modified string date
    """
    change = datetime.timedelta(days=days)
    date_obj = date_string_to_datetime(date)
    updated_date = date_obj + change
    return "{}-{}-{}".format(updated_date.year,
                             updated_date.month,
                             updated_date.day)


def update_shift_date(shift, days):
    """
    :param shift: A Shift object.
    :param days: Number of days to add to the Shift date.
    :return: An updated Shift saved to the database.
    """

    current = shift.day
    new_date = current.day_date + datetime.timedelta(days=days)
    new_workday = WorkDay.objects.get(day_date=new_date)
    shift.day = new_workday
    shift.save()


def check_shift_overlap(shift, shifts):
    """
    :param shift: A shift object.
    :param shifts: A querset of shift objects to be checked against.
    :return: True if shift is valid, False if it starts within 24 hours of
    a shift in shifts.
    """
    working_date = shift.datetime_obj
    one_day = datetime.timedelta(days=1)
    after = working_date + one_day
    before = working_date - one_day

    qs = shifts.filter(day__day_date__gte=before,
                       day__day_date__lte=after,
                       employee=shift.employee)
    qs = qs.exclude(day__day_date=after,
                    starting_time__gte=working_date.time())
    qs = qs.exclude(day__day_date=before,
                    starting_time__lte=working_date.time())
    return qs.count() == 1


def random_shift_monte_carlo(new_shifts, all_shifts, employee_ids):
    """
    Find a random valid new reshuffling of a shift week.
    :param new_shifts: Shifts with id=None.
    :param all_shifts: Shifts to be checked against for conflicts, typically
    either all shifts or the bordering weeks.
    :param employee_ids: A list of employee id numbers that must be randomly
    reassigned.
    :return: A valid set of new shifts ready to be saved to the database.
    """
    # get a queryset of employees based on unique ids to save databse calls.
    for i in range(1000):
        print(i)
        random.shuffle(employee_ids)
        for i, shift in enumerate(new_shifts):
            shift.employee = EmployeeProfile.objects.get(id=employee_ids[i])
            shift.save()

        all_shifts = Shift.objects.all()

        validity_checks = [
            check_shift_overlap(shift, all_shifts) for shift in new_shifts
            ]
        if set(validity_checks) == {True}:
            return new_shifts

    return 'error'


class EmployeeShiftsByMonth(generics.ListAPIView):
    """
    Takes a month and year and returns schedules for the requesting employee.
    The time frame is an expanded six week calendar view of the month that will
    start from Sunday in the prior month and run into the following month.


    example GET: schedules/employeemonth/?month=6&year=2016
    """
    serializer_class = EmployeeShiftSerializer
    permission_classes = (IsEmployee,)

    def get_queryset(self):

        if not self.request.user.id:
            return []

        year = int(self.request.query_params["year"])
        month = int(self.request.query_params["month"])
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


class ShiftWeekList(generics.ListAPIView):
    """
    Accepts a date querystring. Creates or retrieves the dates for that work
    week and returns all shifts that fall on those days.

    Used for the managers schedule view and generating new WorkDays.

    example: weekshift/?date=2016-6-20
    """
    serializer_class = EmployeeShiftSerializer
    permission_classes = (IsManager,)

    def get_queryset(self):
        date = self.request.query_params.get('date')

        if not date:
            return []
        qs = get_week_shifts(date, self.request.query_params.get('department'))

        return qs


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

     To add a station or area, include an id.
    Example: [
    {"starting_time": "11:00", "day": "2016-6-20", "employee": 1},
     {"starting_time": "11:00", "day": "2016-6-21", "employee": 1}
     ]
    """

    permission_classes = (IsManager,)

    def post(self, request, format=None):

        # If starting time is "" then delete shift if it exists.

        updated_data = []
        for item in request.data:
            # Block past shifts from being changed.
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

    permission_classes = (IsManager,)

    def post(self, request, format=None):
        email_success, phone_success = True, True

        schedule = get_or_create_schedule(request.data['date'])
        first = schedule.workday_set.first()
        last = schedule.workday_set.last()
        shifts = Shift.objects.filter(day__day_date__gte=first.day_date,
                                      day__day_date__lte=last.day_date,
                                      visible=False
                                      ).all()
        logger.debug("number shifts: {}".format(shifts.count()))

        try:
            phone_notify_employees(shifts)
        except:
            phone_success = False
        try:
            email_notify_employees(shifts)
        except:
            email_success = False
        amount = shifts.count()
        shifts.update(visible=True)

        logger.debug("Starting day: {}".format(first.day_date))
        logger.debug("Ending day: {}".format(last.day_date))

        logger.debug("amount: {}".format(amount))

        return Response(
            {'amount updated': amount,
             'phone_success': phone_success,
             'email_success': email_success},
            status=status.HTTP_200_OK
        )


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
            return Response("No employee token sent",
                            status=status.HTTP_400_BAD_REQUEST)

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


class AreaListCreate(generics.ListCreateAPIView):
    """
    GET returns a list of all areas.
    To create and area POST title, department, description (optional)
    example: {"title": "test area", department: 1}
    """
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = (IsManager,)


class AreaDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = (IsManager,)


class StationListCreate(generics.ListCreateAPIView):
    """
    GET returns a list of all stations.
    To create you must POST: title, area
    Optional fields: must_fill, grave_start, day_start, swing_start
    example: {"title": "test area", area: 1}
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsManager,)


class StationDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsManager,)


class AutoPopulateWeek(APIView):
    """
    A simple auto-populate feature which copies the previous week.
    POST a department and a date from the week of the new shifts.
    methods: duplicate - repeat previous shift,
    station - randomly change employees, station and time pairs stay the same.
    example: POST {'date': '2016-6-20', deparment: 1, 'method': 'duplicate'}
     to schedules/auto/ to create shifts for that week.
    """
    permission_classes = (IsManager,)

    def post(self, request, format=None):
        # only doing a week right now
        day_change = 7

        current_date = self.request.data.get('date')
        current_schedule = get_or_create_schedule(current_date)
        old_shifts = get_week_shifts(current_date,
                                     self.request.data.get('department'))
        old_shifts.delete()

        previous_date = change_string_date(current_date, -day_change)
        previous_shifts = get_week_shifts(previous_date,
                                          self.request.data.get('department')
                                          )

        if self.request.data.get('method') == 'duplicate':
            for shift in previous_shifts:
                shift.id = None
                shift.visible = False
                update_shift_date(shift, day_change)

            return Response('New shifts created',
                            status=status.HTTP_201_CREATED)

        elif self.request.data.get('method') == 'station':
            employee_id_list = previous_shifts.values_list('employee', flat=True)
            employee_id_list = list(employee_id_list)
            all_shifts = Shift.objects.all()

            # change shift date, visible here. before monto carlo
            for shift in previous_shifts:
                shift.id = None
                shift.visible = False
                update_shift_date(shift, day_change)
            rotated_shifts = random_shift_monte_carlo(previous_shifts,
                                                      Shift.objects.all(),
                                                      employee_id_list)

            return Response('New shifts created',
                            status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShiftTemplateListCreate(generics.ListCreateAPIView):
    """
    For shift_category 1=Grave, 3=Swing.
    """
    queryset = ShiftTemplate.objects.all()
    serializer_class = ShiftTemplateSerializer


class ShiftTemplateDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):

    queryset = ShiftTemplate
    serializer_class = ShiftTemplateSerializer
